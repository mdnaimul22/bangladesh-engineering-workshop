"""Material and product sales domain models and DTOs."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import Field
from src.schema.common import BaseSchema


# --- Sale Line Item ---

class SaleItemBase(BaseSchema):
    """Base fields for customer sale invoice line item."""
    raw_material_id: Optional[int] = Field(default=None, description="Material master catalog ID")
    product_name: Optional[str] = Field(default=None, max_length=500, description="Product / material name")
    quantity: float = Field(default=0.0, ge=0.0, description="Quantity sold")
    unit_price: float = Field(default=0.0, ge=0.0, description="Unit selling price")
    total_price: float = Field(default=0.0, ge=0.0, description="Total price")
    weight: float = Field(default=0.0, ge=0.0, description="Weight (kg)")
    inventory_link_id: Optional[int] = Field(default=None, description="Legacy inventory link ID")


class SaleItemCreate(SaleItemBase):
    """Payload for adding a line item to a sale invoice."""
    pass


class SaleItemUpdate(BaseSchema):
    """Payload for updating a sale line item (all fields optional)."""
    raw_material_id: Optional[int] = Field(default=None, description="Material ID")
    product_name: Optional[str] = Field(default=None, max_length=500, description="Product name")
    quantity: Optional[float] = Field(default=None, ge=0.0, description="Quantity")
    unit_price: Optional[float] = Field(default=None, ge=0.0, description="Unit price")
    total_price: Optional[float] = Field(default=None, ge=0.0, description="Total price")
    weight: Optional[float] = Field(default=None, ge=0.0, description="Weight")
    inventory_link_id: Optional[int] = Field(default=None, description="Inventory link ID")


class SaleItemResponse(SaleItemBase):
    """Sale line item response contract."""
    id: Optional[int] = Field(default=None, description="Item ID")
    sale_id: Optional[int] = Field(default=None, description="Parent sale ID")
    inventory_material_name: Optional[str] = Field(default=None, description="Resolved inventory material name")


SaleItem = SaleItemResponse


# --- Sale Invoice ---

class SaleBase(BaseSchema):
    """Base fields for sales invoice."""
    buyer_id: int = Field(..., description="Client buyer ID")
    sale_date: Optional[date] = Field(default=None, description="Sale invoice date")
    total_amount: float = Field(default=0.0, ge=0.0, description="Total sale invoice value")
    voucher_image: Optional[str] = Field(default=None, description="Invoice image path")


class SaleCreate(SaleBase):
    """Payload for creating a sales invoice with line items."""
    items: List[SaleItemCreate] = Field(default_factory=list, description="Line items sold")


class SaleUpdate(BaseSchema):
    """Payload for updating a sales invoice (all fields optional)."""
    buyer_id: Optional[int] = Field(default=None, description="Buyer ID")
    sale_date: Optional[date] = Field(default=None, description="Sale date")
    total_amount: Optional[float] = Field(default=None, ge=0.0, description="Total amount")
    voucher_image: Optional[str] = Field(default=None, description="Voucher image path")
    items: Optional[List[SaleItemCreate]] = Field(default=None, description="Line items")


class SaleResponse(SaleBase):
    """Sales transaction response contract."""
    id: Optional[int] = Field(default=None, description="Sale ID")
    display_id: Optional[str] = Field(default=None, description="Transaction ID (e.g. BEW-TRX-1)")
    voucher_id: Optional[str] = Field(default=None, description="Voucher ID (e.g. BEW-VCH-S-1)")
    buyer_name: str = Field(default="Unknown", description="Client company name")
    sale_date_display: str = Field(default="-", description="Formatted date")
    item_count: int = Field(default=0, ge=0, description="Item count")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    items: List[SaleItemResponse] = Field(default_factory=list, description="Sold items breakdown")


Sale = SaleResponse
