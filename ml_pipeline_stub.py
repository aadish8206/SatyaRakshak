"""
ml_pipeline_stub.py
--------------------
This is the piece that sits BEFORE the database: it plays the role of your
two trained models and shows exactly how their outputs become the documents
written into the suspected_users collection.

Model 1 (slide 4) - Content Veracity:
    TF-IDF + Logistic Regression (or BERT) -> P(article is fake) per post.
    Here we simulate a per-user average veracity score; swap
    `veracity_score_for_user` for a call into your trained model.

Model 2 (slide 5) - Behavioral Anomaly Detection:
    Multivariate Gaussian over [post_frequency, post_volume, fake_content_ratio].
    mu, Sigma estimated from "normal" users; p(x) computed for every user;
    p(x) < epsilon => flagged as anomalous/coordinated.

Combined risk_score (slide 2, "we combine both scores into a single risk rank"):
    risk_score = w1 * veracity_score + w2 * anomaly_score

Two ways to get results into the database, both included below:
  1. insert_flagged_users_direct()  - pipeline writes straight to MongoDB
  2. insert_flagged_users_via_api() - pipeline POSTs to the running FastAPI
     service, useful once the pipeline runs on a different machine/schedule
     than the API server (matches the "Real Time Streaming" roadmap item).

Run standalone to insert demo data:
    python ml_pipeline_stub.py
"""

import numpy as np
import pandas as pd
import requests

from database import init_db, get_collection

API_URL = "http://127.0.0.1:8000"  # backend base URL, used only by the API path
PUSH_VIA_API = False  # True = POST to the running FastAPI service; False = write to Mongo directly


# ---------------------------------------------------------------------------
# MODEL 2: Multivariate Gaussian anomaly detector (slide 5 math, implemented)
# ---------------------------------------------------------------------------

class GaussianAnomalyDetector:
    """
    Fits mu (mean vector) and Sigma (covariance matrix) over behavioral
    features from users assumed "normal", then scores every user's
    probability density p(x). Low p(x) => behaviorally anomalous.
    """

    def __init__(self, epsilon: float = 1e-4):
        self.epsilon = epsilon
        self.mu = None
        self.sigma = None
        self.sigma_inv = None
        self.sigma_det = None
        self.n_features = None

    def fit(self, X: np.ndarray):
        self.n_features = X.shape[1]
        self.mu = X.mean(axis=0)
        self.sigma = np.cov(X, rowvar=False) + np.eye(self.n_features) * 1e-6  # regularize
        self.sigma_inv = np.linalg.inv(self.sigma)
        self.sigma_det = np.linalg.det(self.sigma)
        return self

    def density(self, X: np.ndarray) -> np.ndarray:
        """p(x) for each row of X - the multivariate Gaussian PDF from slide 5."""
        diff = X - self.mu
        exponent = -0.5 * np.einsum("ij,jk,ik->i", diff, self.sigma_inv, diff)
        norm_const = 1.0 / np.sqrt(((2 * np.pi) ** self.n_features) * self.sigma_det)
        return norm_const * np.exp(exponent)

    def anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Normalized 0-1 "how anomalous" score for ranking/risk purposes.
        Converts density -> score via -log(p(x)), then min-max normalizes,
        so lower density (rarer behavior) becomes a HIGHER score.
        """
        p = self.density(X)
        p = np.clip(p, 1e-300, None)  # avoid log(0)
        neg_log_p = -np.log(p)
        lo, hi = neg_log_p.min(), neg_log_p.max()
        if hi - lo < 1e-12:
            return np.zeros_like(neg_log_p)
        return (neg_log_p - lo) / (hi - lo)

    def flag(self, X: np.ndarray) -> np.ndarray:
        """Boolean flag per slide 5's threshold rule: p(x) < epsilon."""
        return self.density(X) < self.epsilon


# ---------------------------------------------------------------------------
# MODEL 1: Content veracity - swap this for your real TF-IDF/BERT model
# ---------------------------------------------------------------------------

def veracity_score_for_user(fake_content_ratio: float) -> float:
    """
    In the real pipeline: for every post by this user, run the TF-IDF+LogReg
    or BERT classifier to get P(fake), then average per user. Here we
    approximate it from fake_content_ratio as a stand-in - replace this
    function body with a call to your trained model's `.predict_proba(...)`
    averaged over the user's posts.
    """
    noise = np.random.normal(0, 0.03)
    return float(np.clip(fake_content_ratio + noise, 0, 1))


# ---------------------------------------------------------------------------
# Demo data generator (mirrors slide 6's Group X / Y / Z synthetic users)
# Replace this with your real FactDrill-derived, user-augmented dataframe.
# ---------------------------------------------------------------------------

def generate_demo_users(n_suspicious=15, n_normal=60, n_inactive=25, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []

    for i in range(n_suspicious):  # Group X: coordinated spreaders
        rows.append(dict(
            username=f"spreader_{i:03d}",
            post_frequency=rng.uniform(15, 40),      # posts/day - very high
            post_volume=int(rng.uniform(200, 800)),
            fake_content_ratio=rng.uniform(0.6, 0.95),
            group_label="suspicious_spreader",
        ))

    for i in range(n_normal):  # Group Y: organic users
        rows.append(dict(
            username=f"user_{i:03d}",
            post_frequency=rng.uniform(0.5, 5),
            post_volume=int(rng.uniform(5, 150)),
            fake_content_ratio=rng.uniform(0.0, 0.15),
            group_label="normal",
        ))

    for i in range(n_inactive):  # Group Z: inactive
        rows.append(dict(
            username=f"lurker_{i:03d}",
            post_frequency=rng.uniform(0, 0.2),
            post_volume=int(rng.uniform(0, 5)),
            fake_content_ratio=rng.uniform(0.0, 0.3),
            group_label="inactive",
        ))

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Pipeline: features -> scores -> risk_score
# ---------------------------------------------------------------------------

def run_pipeline(df: pd.DataFrame, w_veracity: float = 0.5, w_anomaly: float = 0.5) -> pd.DataFrame:
    features = df[["post_frequency", "post_volume", "fake_content_ratio"]].to_numpy()

    # Fit the anomaly model on users NOT in the suspicious group, to learn
    # what "normal" looks like (slide 5: "capture normal, organic spreader
    # behavior").
    normal_mask = (df["group_label"] != "suspicious_spreader").to_numpy()
    detector = GaussianAnomalyDetector(epsilon=1e-6).fit(features[normal_mask])

    df = df.copy()
    df["anomaly_probability"] = detector.density(features)
    df["anomaly_score"] = detector.anomaly_score(features)
    df["veracity_avg_score"] = df["fake_content_ratio"].apply(veracity_score_for_user)

    df["risk_score"] = (
        w_veracity * df["veracity_avg_score"] + w_anomaly * df["anomaly_score"]
    ).clip(0, 1)

    return df


# ---------------------------------------------------------------------------
# Writing results into the database (the actual "add sus users to DB" step)
# ---------------------------------------------------------------------------

def _flagged_records(df: pd.DataFrame, risk_threshold: float) -> list[dict]:
    """
    Only users above risk_threshold go into the moderation queue - this is
    the filtering step that turns raw scored data into an actionable list,
    not a dump of every user processed.
    """
    flagged = df[df["risk_score"] >= risk_threshold]
    return [
        {
            "username": r.username,
            "post_frequency": float(r.post_frequency),
            "post_volume": int(r.post_volume),
            "fake_content_ratio": float(r.fake_content_ratio),
            "veracity_avg_score": float(r.veracity_avg_score),
            "anomaly_probability": float(r.anomaly_probability),
            "risk_score": float(r.risk_score),
            "group_label": r.group_label,
        }
        for r in flagged.itertuples()
    ]


def insert_flagged_users_direct(df: pd.DataFrame, risk_threshold: float = 0.5) -> int:
    """Write flagged users straight into MongoDB (no API hop)."""
    from datetime import datetime, timezone

    records = _flagged_records(df, risk_threshold)
    if not records:
        return 0

    now = datetime.now(timezone.utc).isoformat()
    for rec in records:
        rec["status"] = "pending_review"
        rec["flagged_at"] = now
        rec["reviewed_at"] = None
        rec["reviewed_by"] = None

    init_db()
    coll = get_collection()
    result = coll.insert_many(records)
    return len(result.inserted_ids)


def insert_flagged_users_via_api(df: pd.DataFrame, risk_threshold: float = 0.5) -> int:
    """Send flagged users to the FastAPI service's bulk-insert endpoint instead."""
    records = _flagged_records(df, risk_threshold)
    if not records:
        return 0

    resp = requests.post(f"{API_URL}/api/users/flag/bulk", json=records, timeout=10)
    resp.raise_for_status()
    return resp.json()["inserted"]


if __name__ == "__main__":
    demo_df = generate_demo_users()
    scored_df = run_pipeline(demo_df)

    insert_fn = insert_flagged_users_via_api if PUSH_VIA_API else insert_flagged_users_direct
    n_inserted = insert_fn(scored_df, risk_threshold=0.5)

    print(f"Processed {len(scored_df)} users through Model 1 + Model 2.")
    print(f"Flagged and inserted {n_inserted} suspected users into MongoDB.")
    print(
        scored_df.sort_values("risk_score", ascending=False)
        [["username", "group_label", "veracity_avg_score", "anomaly_score", "risk_score"]]
        .head(10)
        .to_string(index=False)
    )