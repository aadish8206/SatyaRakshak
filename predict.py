"""
SatyaRakshak — Coordinated Disinformation Detection
Inference module for backend integration.

Loads pre-trained artifacts (no retraining) and exposes predict_risk()
for scoring a new claim + a user's posting history.

Required artifact files (same directory by default):
    tfidf_vectorizer.pkl      - Model 1 TF-IDF vectorizer (fit on claim train split)
    logreg_model.pkl          - Model 1 LogisticRegression classifier
    tfidf_full_vectorizer.pkl - Model 1b TF-IDF vectorizer (fit on full claim corpus)
    gaussian_mu.npy           - Model 2 fitted mean vector [total_posts, fake_ratio]
    gaussian_sigma.npy        - Model 2 fitted covariance matrix
    gaussian_epsilon.npy      - Model 2 anomaly threshold (5th percentile density)
    corpus_claims.csv         - full claim corpus used for Model 1b similarity matching
                                 (columns: claim, label_binary, user)

NOTE on the anomaly normalization constant (P_X_MAX below): this is an estimate
of the maximum density seen when the Gaussian was fit on the original 150-user
training population. If you retrain Model 2 on a different population, re-derive
this from user_stats['p_x'].max() and update it here.
"""

import os
import joblib
import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal
from sklearn.metrics.pairwise import cosine_similarity

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))

# Rough max density observed at training time (from user_stats['p_x'].describe()).
# Used only to normalize p_x into a 0-1 "anomaly score" for fusion.
P_X_MAX = 0.2415

# Fusion weights: (fake_prob, anomaly, shared_campaign)
WEIGHTS_FULL = (0.4, 0.4, 0.2)          # used when a trustworthy fake_prob is available
WEIGHTS_FALLBACK = (0.0, 0.5, 0.5)      # used when fake_prob is unavailable/unreliable

SIMILARITY_THRESHOLD = 0.6


def load_artifacts(artifact_dir=ARTIFACT_DIR):
    """Load all model artifacts once at process startup; reuse across requests."""
    vectorizer = joblib.load(os.path.join(artifact_dir, "tfidf_vectorizer.pkl"))
    clf = joblib.load(os.path.join(artifact_dir, "logreg_model.pkl"))
    tfidf_full = joblib.load(os.path.join(artifact_dir, "tfidf_full_vectorizer.pkl"))
    mu = np.load(os.path.join(artifact_dir, "gaussian_mu.npy"))
    sigma = np.load(os.path.join(artifact_dir, "gaussian_sigma.npy"))
    epsilon = float(np.load(os.path.join(artifact_dir, "gaussian_epsilon.npy")))

    corpus_path = os.path.join(artifact_dir, "corpus_claims.csv")
    corpus_claims = None
    corpus_matrix = None
    if os.path.exists(corpus_path):
        corpus_claims = pd.read_csv(corpus_path)
        corpus_matrix = tfidf_full.transform(corpus_claims["claim"].fillna(""))

    return {
        "vectorizer": vectorizer,
        "clf": clf,
        "tfidf_full": tfidf_full,
        "mu": mu,
        "sigma": sigma,
        "epsilon": epsilon,
        "corpus_claims": corpus_claims,
        "corpus_matrix": corpus_matrix,
    }


def predict_risk(claim_text, user_history_df, artifacts, similarity_threshold=SIMILARITY_THRESHOLD):
    """
    claim_text: str — the new claim to assess
    user_history_df: DataFrame with columns ['claim', 'label_binary'] — this user's past posts
    artifacts: dict returned by load_artifacts()

    Returns a dict with each signal plus a final fused risk_score in [0, 1].
    """
    vectorizer = artifacts["vectorizer"]
    clf = artifacts["clf"]
    tfidf_full = artifacts["tfidf_full"]
    mu, sigma, epsilon = artifacts["mu"], artifacts["sigma"], artifacts["epsilon"]
    corpus_claims = artifacts["corpus_claims"]
    corpus_matrix = artifacts["corpus_matrix"]

    # --- Model 1: claim-level fake probability ---
    X_claim = vectorizer.transform([claim_text])
    fake_idx = list(clf.classes_).index("fake")
    fake_prob = float(clf.predict_proba(X_claim)[0][fake_idx])

    # --- Model 2: user-level statistical anomaly ---
    total_posts = len(user_history_df) + 1
    fake_posts = int((user_history_df["label_binary"] == "fake").sum()) + 1  # assume new claim fake for scoring
    fake_ratio = fake_posts / total_posts

    rv = multivariate_normal(mean=mu, cov=sigma)
    p_x = float(rv.pdf([total_posts, fake_ratio]))
    is_anomaly = bool(p_x < epsilon)
    norm_anomaly = 1 - min(p_x / P_X_MAX, 1.0)

    # --- Model 1b: shared-campaign / near-duplicate claim detection ---
    shared_campaign = False
    matched_claims = 0
    matched_users = []
    if corpus_matrix is not None:
        X_new = tfidf_full.transform([claim_text])
        sims = cosine_similarity(X_new, corpus_matrix)[0]
        match_mask = sims > similarity_threshold
        matched_claims = int(match_mask.sum())
        shared_campaign = matched_claims > 0
        if shared_campaign and "user" in corpus_claims.columns:
            matched_users = corpus_claims.loc[match_mask, "user"].unique().tolist()

    # --- Fusion ---
    if user_history_df is not None and len(user_history_df) > 0:
        w_fake, w_anom, w_shared = WEIGHTS_FULL
    else:
        w_fake, w_anom, w_shared = WEIGHTS_FALLBACK

    risk_score = w_fake * fake_prob + w_anom * norm_anomaly + w_shared * int(shared_campaign)

    return {
        "fake_prob": round(fake_prob, 3),
        "total_posts": total_posts,
        "fake_ratio": round(fake_ratio, 3),
        "p_x": p_x,
        "is_anomaly": is_anomaly,
        "shared_campaign": shared_campaign,
        "matched_claims": matched_claims,
        "matched_users": matched_users,
        "risk_score": round(risk_score, 3),
    }


if __name__ == "__main__":
    # Quick smoke test — replace with real data before deploying.
    artifacts = load_artifacts()
    dummy_history = pd.DataFrame({"claim": [], "label_binary": []})
    result = predict_risk(
        "A viral WhatsApp message says a factory worker infected with HIV added his blood to Coca-Cola bottles.",
        dummy_history,
        artifacts,
    )
    print(result)
