import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
import predict
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timezone


load_dotenv("atlas-credentials.env")

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "satyarakshak")

client = MongoClient(mongo_uri)
db = client[db_name]

ml_artifacts = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_artifacts["data"] = predict.load_artifacts(artifact_dir="artifacts")
    print("Artifacts loaded.")
    yield

app = FastAPI(title="SatyaRakshak API", lifespan=lifespan)

@app.get("/health")
def health_check():
    try:
        client.admin.command("ping")
        return {"status": "ok", "mongo": "connected", "database": db_name}
    except Exception as e:
        return {"status": "error", "mongo": str(e)}


class PredictRequest(BaseModel):
    claim_text: str
    user_id: str

def get_category(risk_score: float, shared_campaign: bool) -> str:
    if risk_score >= 0.7 and shared_campaign:
        return "Coordinated"
    elif risk_score >= 0.7:
        return "Suspicious"
    elif risk_score >= 0.3:
        return "Under Review"
    else:
        return "Real"

@app.post("/predict")
def predict_endpoint(req: PredictRequest):
    artifacts = ml_artifacts["data"]

    # 1. Pull this user's past claims from Mongo
    past_claims = list(db.claims.find({"user_id": req.user_id}))
    history_df = pd.DataFrame(past_claims) if past_claims else pd.DataFrame(columns=["claim", "label_binary"])
    if not history_df.empty and "claim_text" in history_df.columns:
        history_df = history_df.rename(columns={"claim_text": "claim"})

    # 2. Run the model pipeline
    result = predict.predict_risk(req.claim_text, history_df, artifacts)
    result["category"] = get_category(result["risk_score"], result["shared_campaign"])

    # 3. Log this claim
    db.claims.insert_one({
        "user_id": req.user_id,
        "claim_text": req.claim_text,
        "label_binary": "fake" if result["risk_score"] >= 0.5 else "real",
        "risk_score": result["risk_score"],
        "fake_prob": result["fake_prob"],
        "shared_campaign": result["shared_campaign"],
        "category": result["category"],
        "timestamp": datetime.now(timezone.utc),
    })

    # 4. Update this user's rolling stats
    db.users.update_one(
        {"user_id": req.user_id},
        {"$set": {
            "total_posts": result["total_posts"],
            "fake_ratio": result["fake_ratio"],
            "last_risk_score": result["risk_score"],
            "category": result["category"],
            "updated_at": datetime.now(timezone.utc),
        }},
        upsert=True,
    )

    return {"user_id": req.user_id, **result}        