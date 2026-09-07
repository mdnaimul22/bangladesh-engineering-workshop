"""Analytics logging and public visitor message domain models and DTOs."""
from datetime import datetime
from typing import Optional
from pydantic import Field
from src.schema.common import BaseSchema


# --- Visitor Message ---

class VisitorMessageBase(BaseSchema):
    """Base fields for public visitor inquiries."""
    name: str = Field(..., min_length=1, max_length=200, description="Visitor sender name")
    phone: Optional[str] = Field(default=None, max_length=100, description="Contact phone number")
    email: Optional[str] = Field(default=None, max_length=200, description="Email address")
    subject: Optional[str] = Field(default=None, max_length=300, description="Inquiry subject")
    message: str = Field(..., min_length=1, description="Message content")


class VisitorMessageCreate(VisitorMessageBase):
    """Payload for submitting a visitor inquiry message."""
    pass


class VisitorMessageResponse(VisitorMessageBase):
    """Visitor message response contract."""
    id: int = Field(..., description="Message ID")
    ip_address: Optional[str] = Field(default=None, description="Sender IP address")
    created_at: Optional[datetime] = Field(default=None, description="Submission timestamp")


VisitorMessage = VisitorMessageResponse


# --- Analytics Log ---

class AnalyticsLogBase(BaseSchema):
    """Base fields for traffic telemetry."""
    ip_address: Optional[str] = Field(default=None, max_length=100, description="Visitor IP address")
    user_agent: Optional[str] = Field(default=None, max_length=500, description="Browser client user agent")
    page_url: Optional[str] = Field(default=None, max_length=1000, description="Requested URL path")
    referer: Optional[str] = Field(default=None, max_length=1000, description="HTTP referer header")


class AnalyticsLogCreate(AnalyticsLogBase):
    """Payload for recording a visit telemetry event."""
    pass


class AnalyticsLogResponse(AnalyticsLogBase):
    """Traffic telemetry log response contract."""
    id: int = Field(..., description="Log record ID")
    created_at: Optional[datetime] = Field(default=None, description="Visit timestamp")


AnalyticsLog = AnalyticsLogResponse
