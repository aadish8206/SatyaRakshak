"""
database.py
------------
MongoDB connection layer for SatyaRakshak.

Everything else in this project (the ML pipeline and the API) talks to the
database ONLY through the functions in this file - get_collection() and
init_db(). That means the rest of the codebase never touches pymongo
directly, so if you later move from a local Mongo instance to Atlas (or add
auth, retries, etc.) you only edit this one file.

Config comes from environment variables so the same code works locally and
in deployment:
    MONGO_URI       e.g. "mongodb://localhost:27017" or an Atlas SRV string
    MONGO_DB_NAME    defaults to "satyarakshak"
"""

import os
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "satyarakshak")
COLLECTION_NAME = "suspected_users"

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Single shared MongoClient (it already pools connections internally)."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_db() -> Database:
    return get_client()[DB_NAME]


def get_collection() -> Collection:
    """The suspected_users collection - the "Actionable Moderation Queue" store."""
    return get_db()[COLLECTION_NAME]


def init_db() -> None:
    """
    Create indexes needed for the moderation queue's common queries:
      - risk_score descending -> "show highest-risk accounts first"
      - status                -> filter pending_review / confirmed / dismissed
      - username               -> fast lookup / de-dup on repeated pipeline runs
    Safe to call every startup - create_index() is a no-op if it already exists.
    """
    coll = get_collection()
    coll.create_index([("risk_score", DESCENDING)])
    coll.create_index([("status", ASCENDING)])
    coll.create_index([("username", ASCENDING)])


def ping() -> bool:
    """Quick connectivity check, useful for a health-check endpoint."""
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False