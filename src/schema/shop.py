"""Shop, category, and tag domain models and DTOs."""
from datetime import datetime
from typing import Optional, List
from pydantic import Field
from src.schema.common import BaseSchema


# --- Category ---

class CategoryBase(BaseSchema):
    """Base fields for business category."""
    name: str = Field(..., min_length=1, max_length=500, description="Bengali / primary category name")
    name_en: Optional[str] = Field(default=None, alias="name_english", max_length=500, description="English category name")


class CategoryCreate(CategoryBase):
    """Payload for creating a category."""
    pass


class CategoryUpdate(BaseSchema):
    """Payload for updating a category."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=500, description="Bengali / primary category name")
    name_en: Optional[str] = Field(default=None, alias="name_english", max_length=500, description="English category name")


class CategoryResponse(CategoryBase):
    """Category response contract."""
    id: int = Field(..., description="Category ID")


Category = CategoryResponse


# --- Tag ---

class TagBase(BaseSchema):
    """Base fields for search tag."""
    name: str = Field(..., min_length=1, max_length=200, description="Tag name")
    name_bn: Optional[str] = Field(default=None, max_length=200, description="Bengali tag name")


class TagCreate(TagBase):
    """Payload for registering a tag."""
    pass


class TagUpdate(BaseSchema):
    """Payload for updating a tag."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Tag name")
    name_bn: Optional[str] = Field(default=None, max_length=200, description="Bengali tag name")


class TagResponse(TagBase):
    """Tag response contract."""
    id: int = Field(..., description="Tag ID")
    shop_count: int = Field(default=0, ge=0, description="Linked shops count")


Tag = TagResponse


# --- Shop ---

class ShopBase(BaseSchema):
    """Base fields for workshop / supplier profile."""
    name: str = Field(..., min_length=1, max_length=500, description="Shop or workshop name")
    category_id: Optional[int] = Field(default=None, description="Linked category ID")
    serial_no: Optional[str] = Field(default=None, max_length=100, description="Serial number")
    proprietor: Optional[str] = Field(default=None, max_length=250, description="Owner / proprietor name")
    address: Optional[str] = Field(default=None, description="Physical location address")
    mobile: Optional[str] = Field(default=None, max_length=100, description="Mobile contact numbers")
    transaction_status: Optional[str] = Field(default=None, max_length=100, description="Account transaction status")
    whatsapp: Optional[str] = Field(default=None, max_length=100, description="WhatsApp contact number")
    email_web: Optional[str] = Field(default=None, max_length=250, description="Email or web address")
    products: Optional[str] = Field(default=None, description="Services and products summary")
    visiting_card: Optional[str] = Field(default=None, max_length=500, description="Card image path")


class ShopCreate(ShopBase):
    """Payload for creating a new workshop profile."""
    tag_ids: List[int] = Field(default_factory=list, description="Associated tag IDs")


class ShopUpdate(BaseSchema):
    """Payload for updating an existing workshop profile (all fields optional)."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=500, description="Shop name")
    category_id: Optional[int] = Field(default=None, description="Category ID")
    serial_no: Optional[str] = Field(default=None, max_length=100, description="Serial number")
    proprietor: Optional[str] = Field(default=None, max_length=250, description="Owner name")
    address: Optional[str] = Field(default=None, description="Physical address")
    mobile: Optional[str] = Field(default=None, max_length=100, description="Phone numbers")
    transaction_status: Optional[str] = Field(default=None, max_length=100, description="Transaction status")
    whatsapp: Optional[str] = Field(default=None, max_length=100, description="WhatsApp number")
    email_web: Optional[str] = Field(default=None, max_length=250, description="Email / Website")
    products: Optional[str] = Field(default=None, description="Products summary")
    visiting_card: Optional[str] = Field(default=None, max_length=500, description="Card file path")
    tag_ids: Optional[List[int]] = Field(default=None, description="Associated tag IDs")


class ShopResponse(ShopBase):
    """Workshop profile response contract."""
    id: int = Field(..., description="Shop ID")
    category_name: Optional[str] = Field(default=None, description="Resolved category name in Bengali")
    category_name_en: Optional[str] = Field(default=None, alias="category_name_english", description="Resolved category name in English")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    tags: List[TagResponse] = Field(default_factory=list, description="Associated domain tags")


Shop = ShopResponse


class ShopSearchResult(ShopResponse):
    """Shop record enriched with search match score."""
    relevance_score: Optional[float] = Field(default=None, description="Semantic / token match score")
