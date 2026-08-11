"""
schemas.py
----------
Pydantic models = the contract between the ML pipeline, the database, and
the frontend. FastAPI uses these to validate incoming data and to
auto-generate the request/response shapes shown at /docs.

The only MongoDB-specific wrinkle is the _id field: Mongo stores it as an
ObjectId, but JSON (and your frontend) wants a plain string. PyObjectId
below handles that conversion both ways.
"""

from typing import Optional, List, Any
from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema


class PyObjectId(str):
    """Lets Pydantic accept a Mongo ObjectId and always serialize it as str."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        def validate(value: Any) -> str:
            if isinstance(value, ObjectId):
                return str(value)
            if isinstance(value, str) and ObjectId.is_valid(value):
                return value
            raise ValueError("Invalid ObjectId")

        return core_schema.no_info_plain_validator_function(
            validate, serialization=core_schema.to_string_ser_schema()
        )


class SuspectedUserIn(BaseModel):
    """What the ML pipeline sends when it flags a user (no id yet)."""
    username: str = Field(..., min_length=1, max_length=100)
    post_frequency: float = Field(..., ge=0, description="Posts per day")
    post_volume: int = Field(..., ge=0, description="Total posts observed")
    fake_content_ratio: float = Field(..., ge=0, le=1)
    veracity_avg_score: float = Field(..., ge=0, le=1, description="Model 1 output")
    anomaly_probability: float = Field(..., description="Model 2 p(x); can be very small")
    risk_score: float = Field(..., ge=0, le=1, description="Combined 0-1 ranking score")
    group_label: str = Field(
        default="suspicious_spreader",
        description="suspicious_spreader | normal | inactive",
    )


class SuspectedUserOut(SuspectedUserIn):
    """What the frontend receives back for each flagged user."""
    id: PyObjectId = Field(..., alias="_id")
    status: str
    flagged_at: str
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


class StatusUpdate(BaseModel):
    status: str = Field(..., description="pending_review | confirmed | dismissed")
    reviewed_by: str = Field(..., description="Moderator name/id")


class BulkInsertResult(BaseModel):
    inserted: int
    ids: List[str]