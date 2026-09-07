"""Inventory, raw material catalog, and stock flow domain models and DTOs."""
from datetime import datetime, date
from typing import Optional
from pydantic import Field
from src.schema.common import BaseSchema, StockMovementType


# --- Raw Material Category ---

class RawMaterialCategoryBase(BaseSchema):
    """Base fields for raw material classification."""
    name: str = Field(..., min_length=1, max_length=200, description="Category name (e.g., Steel, Brass)")
    name_bn: Optional[str] = Field(default=None, max_length=200, description="Bengali category name")
    description: Optional[str] = Field(default=None, description="Category description")


class RawMaterialCategoryCreate(RawMaterialCategoryBase):
    """Payload for registering a raw material category."""
    pass


class RawMaterialCategoryUpdate(BaseSchema):
    """Payload for updating a raw material category (all fields optional)."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Category name")
    name_bn: Optional[str] = Field(default=None, max_length=200, description="Bengali category name")
    description: Optional[str] = Field(default=None, description="Category description")


class RawMaterialCategoryResponse(RawMaterialCategoryBase):
    """Raw material category response contract."""
    id: int = Field(..., description="Category ID")
    material_count: int = Field(default=0, ge=0, description="Count of linked materials")


RawMaterialCategory = RawMaterialCategoryResponse


# --- Raw Material Catalog ---

class RawMaterialBase(BaseSchema):
    """Base fields for master raw material catalog."""
    name: str = Field(..., min_length=1, max_length=300, description="Material name")
    category_id: Optional[int] = Field(default=None, description="Linked category ID")
    name_bn: Optional[str] = Field(default=None, max_length=300, description="Bengali name")
    default_unit: Optional[str] = Field(default="kg", max_length=50, description="Default unit")
    description: Optional[str] = Field(default=None, description="Specification notes")
    min_stock_level: float = Field(default=0.0, ge=0.0, description="Low stock alert threshold")


class RawMaterialCreate(RawMaterialBase):
    """Payload for registering a master raw material."""
    pass


class RawMaterialUpdate(BaseSchema):
    """Payload for updating a raw material (all fields optional)."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=300, description="Material name")
    category_id: Optional[int] = Field(default=None, description="Linked category ID")
    name_bn: Optional[str] = Field(default=None, max_length=300, description="Bengali name")
    default_unit: Optional[str] = Field(default=None, max_length=50, description="Default unit")
    description: Optional[str] = Field(default=None, description="Specification notes")
    min_stock_level: Optional[float] = Field(default=None, ge=0.0, description="Low stock alert threshold")


class RawMaterialResponse(RawMaterialBase):
    """Raw material master catalog response contract."""
    id: int = Field(..., description="Material ID")
    display_id: Optional[str] = Field(default=None, description="Formatted ID (e.g., BEW-ITEM-1)")
    category_name: Optional[str] = Field(default=None, description="Resolved category name")
    current_stock: float = Field(default=0.0, description="Live stock balance")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")


RawMaterial = RawMaterialResponse


# --- Stock Movement ---

class StockMovementBase(BaseSchema):
    """Base fields for stock flow audit record."""
    raw_material_id: int = Field(..., description="Linked material ID")
    movement_type: StockMovementType = Field(..., description="IN, OUT, or ADJUST")
    quantity: float = Field(..., gt=0.0, description="Quantity moved")
    unit: Optional[str] = Field(default=None, max_length=50, description="Unit")
    source_type: Optional[str] = Field(default=None, max_length=50, description="Source type (purchase, sale, work_order)")
    source_id: Optional[str] = Field(default=None, max_length=50, description="Document display ID")
    supplier_id: Optional[int] = Field(default=None, description="Supplier shop ID")
    rate_per_unit: float = Field(default=0.0, ge=0.0, description="Unit rate")
    total_amount: float = Field(default=0.0, ge=0.0, description="Total amount")
    notes: Optional[str] = Field(default=None, description="Movement remarks")
    movement_date: Optional[date] = Field(default=None, description="Transaction date")


class StockMovementCreate(StockMovementBase):
    """Payload to record a new stock movement."""
    pass


class StockMovementResponse(StockMovementBase):
    """Stock movement response contract."""
    id: int = Field(..., description="Movement ID")
    raw_material_name: Optional[str] = Field(default=None, description="Resolved material name")
    supplier_name: Optional[str] = Field(default=None, description="Resolved supplier name")
    movement_date_display: str = Field(default="-", description="Formatted date")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")


StockMovement = StockMovementResponse


# --- Supplier Material Rate ---

class SupplierMaterialRateBase(BaseSchema):
    """Base fields for supplier quotation and historical rates."""
    supplier_id: int = Field(..., description="Supplier shop ID")
    raw_material_id: int = Field(..., description="Material ID")
    rate: float = Field(..., gt=0.0, description="Price per unit")
    notes: Optional[str] = Field(default=None, description="Pricing terms")
    effective_date: Optional[date] = Field(default=None, description="Effective date")


class SupplierMaterialRateCreate(SupplierMaterialRateBase):
    """Payload for registering a supplier material rate."""
    pass


class SupplierMaterialRateUpdate(BaseSchema):
    """Payload for updating a supplier material rate."""
    rate: Optional[float] = Field(default=None, gt=0.0, description="Price per unit")
    notes: Optional[str] = Field(default=None, description="Pricing terms")
    effective_date: Optional[date] = Field(default=None, description="Effective date")


class SupplierMaterialRateResponse(SupplierMaterialRateBase):
    """Supplier rate response contract."""
    id: int = Field(..., description="Rate ID")
    supplier_name: Optional[str] = Field(default=None, description="Resolved supplier name")
    raw_material_name: Optional[str] = Field(default=None, description="Resolved material name")
    effective_date_display: str = Field(default="-", description="Formatted date")


SupplierMaterialRate = SupplierMaterialRateResponse


# --- Inventory Item (Legacy) ---

class InventoryItemBase(BaseSchema):
    """Base fields for legacy workshop inventory items."""
    shop_id: int = Field(..., description="Supplier shop ID")
    material_name: str = Field(..., min_length=1, max_length=500, description="Item description")
    purchase_date: Optional[date] = Field(default=None, description="Purchase date")
    quantity: float = Field(default=0.0, ge=0.0, description="Quantity")
    cost: float = Field(default=0.0, ge=0.0, description="Total purchase cost")
    tags: Optional[str] = Field(default=None, description="Material tags")


class InventoryItemCreate(InventoryItemBase):
    """Payload for creating a legacy inventory item."""
    pass


class InventoryItemUpdate(BaseSchema):
    """Payload for updating a legacy inventory item."""
    shop_id: Optional[int] = Field(default=None, description="Supplier shop ID")
    material_name: Optional[str] = Field(default=None, min_length=1, max_length=500, description="Item description")
    purchase_date: Optional[date] = Field(default=None, description="Purchase date")
    quantity: Optional[float] = Field(default=None, ge=0.0, description="Quantity")
    cost: Optional[float] = Field(default=None, ge=0.0, description="Total purchase cost")
    tags: Optional[str] = Field(default=None, description="Material tags")


class InventoryItemResponse(InventoryItemBase):
    """Legacy inventory item response contract."""
    id: int = Field(..., description="Inventory item ID")
    shop_name: str = Field(default="Unknown", description="Resolved supplier name")
    purchase_date_display: str = Field(default="-", description="Formatted date")


InventoryItem = InventoryItemResponse
