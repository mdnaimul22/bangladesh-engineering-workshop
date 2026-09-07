"""Supplier purchase and procurement voucher domain models and DTOs."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import Field
from src.schema.common import BaseSchema, PaymentStatus


# --- Purchase Line Item ---

class PurchaseItemBase(BaseSchema):
    """Base fields for purchase invoice line item."""
    raw_material_id: Optional[int] = Field(default=None, description="Raw material master catalog ID")
    product_name: Optional[str] = Field(default=None, max_length=500, description="Product / material description")
    specification: Optional[str] = Field(default=None, max_length=1000, description="Specification or size")
    quantity: float = Field(default=0.0, ge=0.0, description="Quantity")
    weight: float = Field(default=0.0, ge=0.0, description="Weight (kg)")
    unit: Optional[str] = Field(default="kg", max_length=50, description="Measurement unit")
    rate_per_unit: float = Field(default=0.0, ge=0.0, description="Unit rate")
    total_amount: float = Field(default=0.0, ge=0.0, description="Line total amount")


class PurchaseItemCreate(PurchaseItemBase):
    """Payload for adding a line item to a purchase."""
    pass


class PurchaseItemUpdate(BaseSchema):
    """Payload for updating a purchase line item (all fields optional)."""
    raw_material_id: Optional[int] = Field(default=None, description="Raw material ID")
    product_name: Optional[str] = Field(default=None, max_length=500, description="Product name")
    specification: Optional[str] = Field(default=None, max_length=1000, description="Specification")
    quantity: Optional[float] = Field(default=None, ge=0.0, description="Quantity")
    weight: Optional[float] = Field(default=None, ge=0.0, description="Weight")
    unit: Optional[str] = Field(default=None, max_length=50, description="Unit")
    rate_per_unit: Optional[float] = Field(default=None, ge=0.0, description="Unit rate")
    total_amount: Optional[float] = Field(default=None, ge=0.0, description="Line total")


class PurchaseItemResponse(PurchaseItemBase):
    """Purchase line item response contract."""
    id: Optional[int] = Field(default=None, description="Line item ID")
    purchase_id: Optional[str] = Field(default=None, description="Parent purchase UUID")
    current_stock: Optional[float] = Field(default=None, description="Resolved current stock level")


PurchaseItem = PurchaseItemResponse
SupplierPurchaseItem = PurchaseItemResponse


# --- Purchase Voucher ---

class PurchaseBase(BaseSchema):
    """Base procurement voucher attributes."""
    supplier_id: int = Field(..., description="Supplier shop ID")
    purchase_date: Optional[date] = Field(default=None, description="Voucher transaction date")
    work_order_id: Optional[str] = Field(default=None, description="Linked work order UUID")
    voucher_no: Optional[str] = Field(default=None, max_length=100, description="Supplier invoice / memo number")
    voucher_file_path: Optional[str] = Field(default=None, description="Scanned voucher image path")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment lifecycle state")
    paid_amount: float = Field(default=0.0, ge=0.0, description="Paid amount")
    notes: Optional[str] = Field(default=None, description="Purchase remarks")


class PurchaseCreate(PurchaseBase):
    """Payload for creating a purchase voucher with line items."""
    items: List[PurchaseItemCreate] = Field(default_factory=list, description="Voucher line items")


class PurchaseUpdate(BaseSchema):
    """Payload for updating a purchase voucher (all fields optional)."""
    supplier_id: Optional[int] = Field(default=None, description="Supplier ID")
    purchase_date: Optional[date] = Field(default=None, description="Purchase date")
    work_order_id: Optional[str] = Field(default=None, description="Work order ID")
    voucher_no: Optional[str] = Field(default=None, max_length=100, description="Voucher number")
    voucher_file_path: Optional[str] = Field(default=None, description="Voucher file path")
    payment_status: Optional[PaymentStatus] = Field(default=None, description="Payment status")
    paid_amount: Optional[float] = Field(default=None, ge=0.0, description="Paid amount")
    notes: Optional[str] = Field(default=None, description="Remarks")
    items: Optional[List[PurchaseItemCreate]] = Field(default=None, description="Line items")


class PurchaseResponse(PurchaseBase):
    """Purchase voucher response contract."""
    id: Optional[str] = Field(default=None, description="Purchase UUID")
    display_id: Optional[str] = Field(default=None, description="Formatted ID (e.g. BEW-BUY-1)")
    voucher_id: Optional[str] = Field(default=None, description="Voucher serial (e.g. BEW-VCH-P-1)")
    supplier_name: str = Field(default="Unknown", description="Supplier shop name")
    purchase_date_display: str = Field(default="-", description="Formatted date")
    total_amount: float = Field(default=0.0, description="Total voucher value")
    item_count: int = Field(default=0, ge=0, description="Count of items")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    items: List[PurchaseItemResponse] = Field(default_factory=list, description="Voucher line items")


Purchase = PurchaseResponse
SupplierPurchase = PurchaseResponse
