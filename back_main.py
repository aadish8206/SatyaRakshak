"""
main.py
-------
SatyaRakshak backend API (MongoDB-backed).

Flow this file implements (matches slide 2's "Actionable Moderation Queue"):

    [ML pipeline: veracity model + anomaly model]
                    |  computes risk_score per user
                    v
        POST /api/users/flag  or  /api/users/flag/bulk
                    |  writes into the suspected_users collection (MongoDB)
                    v
              suspected_users collection
                    |
                    v
        GET /api/users/suspected   <-- frontend calls this to render the queue
                    |
                    v
        moderator reviews in the UI, calls
        PATCH /api/users/suspected/{id}/status

Run it:
    pip install -r requirements.txt
    # make sure MongoDB is running (local `mongod`, or set MONGO_URI to Atlas)
    uvicorn main:app --reload --port 8000

Then open http://127.0.0.1:8000/docs for interactive API docs.
"""

from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, get_collection, ping
from schemas import SuspectedUserIn, SuspectedUserOut, StatusUpdate, BulkInsertResult

app = FastAPI(
    title="SatyaRakshak API",
    description="Backend for coordinated-disinformation user flagging & moderation queue (MongoDB)",
    version="1.0.0",
)

# Allow the frontend to call this API. Restrict allow_origins to your real
# frontend's URL before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
def root():
    return {"service": "SatyaRakshak API", "status": "running", "db_connected": ping()}


# ---------------------------------------------------------------------------
# WRITE: ML pipeline -> MongoDB
# ---------------------------------------------------------------------------

@app.post("/api/users/flag", response_model=SuspectedUserOut, status_code=201)
def flag_user(user: SuspectedUserIn):
    """Insert a single suspected user (called by the ML pipeline)."""
    coll = get_collection()
    doc = user.model_dump()
    doc["status"] = "pending_review"
    doc["flagged_at"] = _now_iso()
    doc["reviewed_at"] = None
    doc["reviewed_by"] = None

    result = coll.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


@app.post("/api/users/flag/bulk", response_model=BulkInsertResult, status_code=201)
def flag_users_bulk(users: List[SuspectedUserIn]):
    """Insert many suspected users at once (typical after a batch model run)."""
    if not users:
        raise HTTPException(status_code=400, detail="Empty user list")

    coll = get_collection()
    now = _now_iso()
    docs = []
    for user in users:
        doc = user.model_dump()
        doc["status"] = "pending_review"
        doc["flagged_at"] = now
        doc["reviewed_at"] = None
        doc["reviewed_by"] = None
        docs.append(doc)

    result = coll.insert_many(docs)
    return {"inserted": len(result.inserted_ids), "ids": [str(i) for i in result.inserted_ids]}


# ---------------------------------------------------------------------------
# READ: MongoDB -> frontend
# ---------------------------------------------------------------------------

@app.get("/api/users/suspected", response_model=List[SuspectedUserOut])
def get_suspected_users(
    status: Optional[str] = Query(None, description="Filter: pending_review|confirmed|dismissed"),
    group_label: Optional[str] = Query(None, description="Filter: suspicious_spreader|normal|inactive"),
    min_risk: float = Query(0.0, ge=0, le=1, description="Only return risk_score >= this"),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Main endpoint the frontend calls to render the moderation queue.
    Sorted by risk_score descending - highest-risk accounts first, matching
    the "clear priority list" described in the problem statement.
    """
    coll = get_collection()
    query: dict = {"risk_score": {"$gte": min_risk}}
    if status:
        query["status"] = status
    if group_label:
        query["group_label"] = group_label

    cursor = coll.find(query).sort("risk_score", -1).limit(limit)
    return list(cursor)


@app.get("/api/users/suspected/{user_id}", response_model=SuspectedUserOut)
def get_user(user_id: str):
    coll = get_collection()
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user id")

    doc = coll.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return doc


# ---------------------------------------------------------------------------
# UPDATE / DELETE: moderator actions from the frontend
# ---------------------------------------------------------------------------

@app.patch("/api/users/suspected/{user_id}/status")
def update_status(user_id: str, update: StatusUpdate):
    """Moderator confirms or dismisses a flagged account from the dashboard."""
    if update.status not in ("pending_review", "confirmed", "dismissed"):
        raise HTTPException(status_code=400, detail="Invalid status value")

    coll = get_collection()
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user id")

    result = coll.update_one(
        {"_id": oid},
        {"$set": {
            "status": update.status,
            "reviewed_by": update.reviewed_by,
            "reviewed_at": _now_iso(),
        }},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "status updated", "id": user_id, "status": update.status}


@app.delete("/api/users/suspected/{user_id}")
def delete_user(user_id: str):
    coll = get_collection()
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user id")

    result = coll.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "deleted", "id": user_id}


# ---------------------------------------------------------------------------
# Stats endpoint - handy for a dashboard summary widget
# ---------------------------------------------------------------------------

@app.get("/api/stats/summary")
def summary_stats():
    coll = get_collection()
    return {
        "total_flagged": coll.count_documents({}),
        "pending_review": coll.count_documents({"status": "pending_review"}),
        "confirmed": coll.count_documents({"status": "confirmed"}),
        "high_risk_ge_0_75": coll.count_documents({"risk_score": {"$gte": 0.75}}),
    }