"""Engineering production work order, blueprint, and component parts domain models and DTOs."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import Field
from src.schema.common import BaseSchema, WorkOrderStatus, PaymentStatus, DocumentType


# --- Work Order Document ---

class WorkOrderDocumentBase(BaseSchema):
    """Base fields for blueprint, CAD drawing, or photo attachment."""
    file_path: str = Field(..., max_length=1000, description="Storage file path")
    document_type: DocumentType = Field(default=DocumentType.OTHER, description="Attachment type")
    notes: Optional[str] = Field(default=None, max_length=500, description="Notes or revision summary")


class WorkOrderDocumentCreate(WorkOrderDocumentBase):
    """Payload for attaching a document to a work order."""
    pass


class WorkOrderDocumentUpdate(BaseSchema):
    """Payload for updating a document attachment."""
    file_path: Optional[str] = Field(default=None, max_length=1000, description="File path")
    document_type: Optional[DocumentType] = Field(default=None, description="Document type")
    notes: Optional[str] = Field(default=None, max_length=500, description="Notes")


class WorkOrderDocumentResponse(WorkOrderDocumentBase):
    """Document attachment response contract."""
    id: Optional[int] = Field(default=None, description="Document ID")
    work_order_id: Optional[str] = Field(default=None, description="Parent work order UUID")
    created_at: Optional[datetime] = Field(default=None, description="Upload timestamp")


WorkOrderDocument = WorkOrderDocumentResponse


# --- Work Order Part ---

class WorkOrderPartBase(BaseSchema):
    """Base fields for component part or outsourced machining consumed in a job."""
    raw_material_id: Optional[int] = Field(default=None, description="Material master catalog ID")
    part_name: Optional[str] = Field(default=None, max_length=500, description="Part description")
    supplier_id: Optional[int] = Field(default=None, description="Supplier shop ID")
    voucher_no: Optional[str] = Field(default=None, max_length=100, description="Supplier invoice number")
    voucher_file_path: Optional[str] = Field(default=None, description="Memo image path")
    measurement: Optional[str] = Field(default=None, max_length=200, description="Dimensions")
    unit: Optional[str] = Field(default="pcs", max_length=50, description="Unit")
    qty: float = Field(default=0.0, ge=0.0, description="Quantity")
    weight: float = Field(default=0.0, ge=0.0, description="Weight (kg)")
    price: float = Field(default=0.0, ge=0.0, description="Cost")


class WorkOrderPartCreate(WorkOrderPartBase):
    """Payload for adding a part to a work order."""
    pass


class WorkOrderPartUpdate(BaseSchema):
    """Payload for updating a work order part (all fields optional)."""
    raw_material_id: Optional[int] = Field(default=None, description="Material ID")
    part_name: Optional[str] = Field(default=None, max_length=500, description="Part name")
    supplier_id: Optional[int] = Field(default=None, description="Supplier ID")
    voucher_no: Optional[str] = Field(default=None, max_length=100, description="Voucher number")
    voucher_file_path: Optional[str] = Field(default=None, description="Voucher file path")
    measurement: Optional[str] = Field(default=None, max_length=200, description="Measurement")
    unit: Optional[str] = Field(default=None, max_length=50, description="Unit")
    qty: Optional[float] = Field(default=None, ge=0.0, description="Quantity")
    weight: Optional[float] = Field(default=None, ge=0.0, description="Weight")
    price: Optional[float] = Field(default=None, ge=0.0, description="Price")


class WorkOrderPartResponse(WorkOrderPartBase):
    """Work order part response contract."""
    id: Optional[int] = Field(default=None, description="Part ID (None for linked purchases)")
    work_order_id: Optional[str] = Field(default=None, description="Parent work order UUID")
    supplier_name: Optional[str] = Field(default=None, description="Supplier name")
    current_stock: Optional[float] = Field(default=None, description="Current stock level")
    is_linked_purchase: bool = Field(default=False, description="Originated from procurement")


WorkOrderPart = WorkOrderPartResponse


# --- Work Order ---

class WorkOrderBase(BaseSchema):
    """Base fields for manufacturing production work order."""
    buyer_id: int = Field(..., alias="company_id", description="Client buyer ID")
    job_name: str = Field(..., min_length=1, max_length=500, description="Job / production title")
    job_date: Optional[date] = Field(default=None, description="Order start date")
    job_description: Optional[str] = Field(default=None, description="Technical specifications")
    status: WorkOrderStatus = Field(default=WorkOrderStatus.OPEN, description="Job status")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    paid_amount: float = Field(default=0.0, ge=0.0, description="Received payment")
    quoted_price: float = Field(default=0.0, ge=0.0, description="Quotation price billed")
    delivery_date: Optional[date] = Field(default=None, description="Delivery deadline")
    labor_cost: float = Field(default=0.0, ge=0.0, description="Labor and machining cost")
    material_cost: float = Field(default=0.0, ge=0.0, description="Direct material cost")
    hard_copy_path: Optional[str] = Field(default=None, description="Hard copy document path")
    notes: Optional[str] = Field(default=None, description="Job remarks")


class WorkOrderCreate(WorkOrderBase):
    """Payload for creating a work order with parts and blueprints."""
    parts: List[WorkOrderPartCreate] = Field(default_factory=list, description="Initial parts")
    documents: List[WorkOrderDocumentCreate] = Field(default_factory=list, description="Initial blueprints")


class WorkOrderUpdate(BaseSchema):
    """Payload for updating a work order (all fields optional)."""
    buyer_id: Optional[int] = Field(default=None, alias="company_id", description="Buyer ID")
    job_name: Optional[str] = Field(default=None, min_length=1, max_length=500, description="Job title")
    job_date: Optional[date] = Field(default=None, description="Order date")
    job_description: Optional[str] = Field(default=None, description="Technical specifications")
    status: Optional[WorkOrderStatus] = Field(default=None, description="Job status")
    payment_status: Optional[PaymentStatus] = Field(default=None, description="Payment status")
    paid_amount: Optional[float] = Field(default=None, ge=0.0, description="Paid amount")
    quoted_price: Optional[float] = Field(default=None, ge=0.0, description="Quotation price")
    delivery_date: Optional[date] = Field(default=None, description="Delivery deadline")
    labor_cost: Optional[float] = Field(default=None, ge=0.0, description="Labor cost")
    material_cost: Optional[float] = Field(default=None, ge=0.0, description="Material cost")
    hard_copy_path: Optional[str] = Field(default=None, description="Hard copy path")
    notes: Optional[str] = Field(default=None, description="Job remarks")
    parts: Optional[List[WorkOrderPartCreate]] = Field(default=None, description="Parts")
    documents: Optional[List[WorkOrderDocumentCreate]] = Field(default=None, description="Documents")


class WorkOrderResponse(WorkOrderBase):
    """Work order response contract."""
    id: Optional[str] = Field(default=None, description="Work order UUID")
    display_id: Optional[str] = Field(default=None, description="Formatted ID (e.g. BEW-WO-1)")
    voucher_id: Optional[str] = Field(default=None, description="Voucher serial (e.g. BEW-VCH-W-1)")
    buyer_name: str = Field(default="Unknown", alias="company_name", description="Client buyer company name")
    job_date_display: str = Field(default="-", description="Formatted start date")
    delivery_date_display: str = Field(default="-", description="Formatted delivery date")
    pending_amount: float = Field(default=0.0, description="Outstanding balance")
    total_cost: float = Field(default=0.0, description="Total manufacturing cost")
    parts_count: int = Field(default=0, ge=0, description="Total parts count")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    parts: List[WorkOrderPartResponse] = Field(default_factory=list, description="Consumed components")
    documents: List[WorkOrderDocumentResponse] = Field(default_factory=list, description="Attached drawings and docs")


WorkOrder = WorkOrderResponse
