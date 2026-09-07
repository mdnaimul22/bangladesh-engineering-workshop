"""Common schema primitives, enums, and utility data contracts."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Universal Pydantic configuration for all BEW-ERP schemas."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )


class PaymentStatus(str, Enum):
    """Payment lifecycle status for invoices, purchases, and jobs."""
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class WorkOrderStatus(str, Enum):
    """Production lifecycle status for workshop jobs."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class StockMovementType(str, Enum):
    """Inventory flow directions."""
    IN = "IN"
    OUT = "OUT"
    ADJUST = "ADJUST"


class DocumentType(str, Enum):
    """Engineering blueprint and attachment classifications."""
    DRAWING = "Drawing"
    PHOTO = "Photo"
    HARD_COPY = "HardCopy"
    OTHER = "Other"


class Pagination(BaseSchema):
    """Pagination metadata contract for list endpoints."""
    page: int = Field(default=1, ge=1, description="Current page number")
    per_page: int = Field(default=10, ge=1, le=100, description="Records per page")
    total_pages: int = Field(default=1, ge=0, description="Total pages count")
    total_items: int = Field(default=0, ge=0, description="Total matching records count")
    has_prev: bool = Field(default=False, description="Has preceding page")
    has_next: bool = Field(default=False, description="Has succeeding page")


class OperationResult(BaseSchema):
    """Standard mutation or deletion outcome response."""
    success: bool = Field(description="Operation success status")
    message: str = Field(description="Descriptive outcome message")
    error_code: Optional[str] = Field(default=None, description="Diagnostic error code if failed")


class IDSequence(BaseSchema):
    """Atomic sequence tracker state."""
    prefix: str = Field(..., max_length=20, description="Sequence prefix (e.g., BEW-WO-)")
    next_number: int = Field(default=1, ge=1, description="Next sequential number")
