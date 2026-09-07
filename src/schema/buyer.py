"""Buyer organization and contact domain models and DTOs."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import Field
from src.schema.common import BaseSchema


# --- Buyer Contact ---

class BuyerContactBase(BaseSchema):
    """Base contact person attributes."""
    name: str = Field(..., min_length=1, max_length=200, description="Contact person full name")
    designation: Optional[str] = Field(default=None, max_length=200, description="Job designation")
    mobiles: List[str] = Field(default_factory=list, description="List of mobile numbers")
    whatsapp: Optional[str] = Field(default=None, max_length=100, description="WhatsApp number")
    email: Optional[str] = Field(default=None, max_length=200, description="Email address")
    is_primary: bool = Field(default=False, description="Primary contact flag")


class BuyerContactCreate(BuyerContactBase):
    """Payload for registering a contact person."""
    pass


class BuyerContactUpdate(BaseSchema):
    """Payload for updating a contact person (all fields optional)."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Contact person full name")
    designation: Optional[str] = Field(default=None, max_length=200, description="Job designation")
    mobiles: Optional[List[str]] = Field(default=None, description="List of mobile numbers")
    whatsapp: Optional[str] = Field(default=None, max_length=100, description="WhatsApp number")
    email: Optional[str] = Field(default=None, max_length=200, description="Email address")
    is_primary: Optional[bool] = Field(default=None, description="Primary contact flag")


class BuyerContactResponse(BuyerContactBase):
    """Contact person response contract."""
    id: int = Field(..., description="Contact ID")
    buyer_id: Optional[int] = Field(default=None, description="Parent buyer ID")
    mobile_display: str = Field(default="-", description="Formatted mobile display string")


BuyerContact = BuyerContactResponse


# --- Buyer ---

class BuyerBase(BaseSchema):
    """Base client organization attributes."""
    company_name: str = Field(..., min_length=1, max_length=300, description="Company name")
    address: Optional[str] = Field(default=None, description="Company address")


class BuyerCreate(BuyerBase):
    """Payload for creating a buyer profile."""
    contacts: List[BuyerContactCreate] = Field(default_factory=list, description="Initial company contacts")


class BuyerUpdate(BaseSchema):
    """Payload for updating a buyer profile (all fields optional)."""
    company_name: Optional[str] = Field(default=None, min_length=1, max_length=300, description="Company name")
    address: Optional[str] = Field(default=None, description="Company address")
    contacts: Optional[List[BuyerContactCreate]] = Field(default=None, description="Updated company contacts")


class BuyerResponse(BuyerBase):
    """Buyer profile response contract."""
    id: int = Field(..., description="Buyer ID")
    display_id: Optional[str] = Field(default=None, description="Formatted ID (e.g., BEW-B-1)")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    contacts: List[BuyerContactResponse] = Field(default_factory=list, description="Company contacts")


Buyer = BuyerResponse


class BuyerProfile(BuyerResponse):
    """Extended buyer profile with business history and outstanding ledger metrics."""
    sales: List[Any] = Field(default_factory=list, description="Sales transaction history")
    work_orders: List[Any] = Field(default_factory=list, description="Work order history")
    total_spent: float = Field(default=0.0, ge=0.0, description="Total billed value")
    outstanding_balance: float = Field(default=0.0, description="Pending payable balance")
