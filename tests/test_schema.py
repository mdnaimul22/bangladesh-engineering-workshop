"""Tests for src/schema — Domain-driven Pydantic data contracts following FastAPI/Pydantic standards."""
import pytest
from datetime import date
from pydantic import ValidationError

from src.schema import (
    PaymentStatus,
    WorkOrderStatus,
    StockMovementType,
    Pagination,
    OperationResult,
    Shop,
    ShopCreate,
    ShopUpdate,
    ShopResponse,
    Category,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    Tag,
    TagCreate,
    TagResponse,
    Buyer,
    BuyerCreate,
    BuyerUpdate,
    BuyerResponse,
    BuyerContact,
    BuyerContactCreate,
    BuyerContactResponse,
    BuyerProfile,
    RawMaterial,
    RawMaterialCreate,
    RawMaterialUpdate,
    RawMaterialResponse,
    RawMaterialCategory,
    RawMaterialCategoryCreate,
    RawMaterialCategoryResponse,
    StockMovement,
    StockMovementCreate,
    StockMovementResponse,
    SupplierMaterialRate,
    SupplierMaterialRateCreate,
    SupplierMaterialRateResponse,
    Purchase,
    PurchaseCreate,
    PurchaseUpdate,
    PurchaseResponse,
    PurchaseItem,
    PurchaseItemCreate,
    PurchaseItemResponse,
    SupplierPurchase,
    Sale,
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SaleItem,
    SaleItemCreate,
    SaleItemResponse,
    WorkOrder,
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderResponse,
    WorkOrderPart,
    WorkOrderPartCreate,
    WorkOrderPartResponse,
    WorkOrderDocument,
    WorkOrderDocumentCreate,
    WorkOrderDocumentResponse,
    AnalyticsLog,
    AnalyticsLogCreate,
    AnalyticsLogResponse,
    VisitorMessage,
    VisitorMessageCreate,
    VisitorMessageResponse,
)


def test_common_pagination_meta():
    """Verify Pagination calculates correctly and enforces page boundaries."""
    meta = Pagination(page=2, per_page=10, total_pages=5, total_items=48, has_prev=True, has_next=True)
    assert meta.page == 2
    assert meta.total_items == 48
    assert meta.has_prev is True

    with pytest.raises(ValidationError):
        Pagination(page=0)  # page must be >= 1


def test_operation_result():
    """Verify standard operation outcome schema."""
    res = OperationResult(success=True, message="Deleted successfully")
    assert res.success is True
    assert res.error_code is None


def test_shop_schemas():
    """Verify Shop, Category, and Tag Create/Update/Response schemas and bilingual alias support."""
    # Category with legacy alias 'name_english'
    cat_payload = {"name": "লেদ ওয়ার্কশপ", "name_english": "Lathe Workshop"}
    cat_create = CategoryCreate.model_validate(cat_payload)
    assert cat_create.name == "লেদ ওয়ার্কশপ"
    assert cat_create.name_en == "Lathe Workshop"

    cat_resp = CategoryResponse(id=1, **cat_create.model_dump())
    assert cat_resp.id == 1

    # Tag Create and Response
    tag_create = TagCreate(name="Gear Cutting", name_bn="গিয়ার কাটিং")
    tag_resp = TagResponse(id=5, shop_count=12, **tag_create.model_dump())
    assert tag_resp.shop_count == 12

    # Shop Create
    shop_create = ShopCreate(
        name="Bismillah Engineering",
        category_id=1,
        proprietor="Haji Abdul",
        mobile="01711000000",
        tag_ids=[5]
    )
    assert shop_create.name == "Bismillah Engineering"
    assert shop_create.tag_ids == [5]

    # Shop Update (partial)
    shop_update = ShopUpdate(mobile="01811000000")
    assert shop_update.name is None
    assert shop_update.mobile == "01811000000"

    # Shop Response
    shop_resp = ShopResponse(
        id=101,
        name=shop_create.name,
        category_id=1,
        category_name="লেদ ওয়ার্কশপ",
        category_name_english="Lathe Workshop",
        tags=[tag_resp]
    )
    assert shop_resp.id == 101
    assert shop_resp.category_name_en == "Lathe Workshop"
    assert len(shop_resp.tags) == 1
    assert Shop == ShopResponse


def test_buyer_schemas():
    """Verify Buyer and BuyerContact Create/Update/Response schemas."""
    contact_create = BuyerContactCreate(
        name="Rahim Uddin",
        designation="Procurement Manager",
        mobiles=["01711111111", "01911111111"],
        is_primary=True
    )
    buyer_create = BuyerCreate(
        company_name="Square Pharmaceuticals Ltd.",
        address="Dhaka EPZ",
        contacts=[contact_create]
    )
    assert buyer_create.company_name == "Square Pharmaceuticals Ltd."
    assert len(buyer_create.contacts) == 1

    # Partial update
    buyer_update = BuyerUpdate(address="Kachpur, Narayanganj")
    assert buyer_update.company_name is None
    assert buyer_update.address == "Kachpur, Narayanganj"

    # Buyer Response
    buyer_resp = BuyerResponse(
        id=1,
        display_id="BEW-B-1",
        company_name=buyer_create.company_name,
        address=buyer_create.address,
        contacts=[
            BuyerContactResponse(
                id=10,
                buyer_id=1,
                name=contact_create.name,
                designation=contact_create.designation,
                mobiles=contact_create.mobiles,
                mobile_display="01711111111, 01911111111",
                is_primary=True
            )
        ]
    )
    assert buyer_resp.display_id == "BEW-B-1"
    assert buyer_resp.contacts[0].mobile_display == "01711111111, 01911111111"
    assert Buyer == BuyerResponse


def test_inventory_and_materials_schemas():
    """Verify RawMaterial, Category, StockMovement, and MaterialRate schemas."""
    cat_create = RawMaterialCategoryCreate(name="Alloy Steel", name_bn="অ্যালয় স্টিল")
    cat_resp = RawMaterialCategoryResponse(id=1, material_count=5, **cat_create.model_dump())
    assert cat_resp.material_count == 5

    mat_create = RawMaterialCreate(
        name="EN8 Carbon Steel Bar",
        category_id=1,
        name_bn="ইএন৮ কার্বন স্টিল",
        default_unit="kg",
        min_stock_level=50.0
    )
    mat_resp = RawMaterialResponse(
        id=1,
        display_id="BEW-ITEM-1",
        current_stock=120.5,
        category_name="Alloy Steel",
        **mat_create.model_dump()
    )
    assert mat_resp.current_stock == 120.5
    assert RawMaterial == RawMaterialResponse

    # Stock movement validation
    movement_create = StockMovementCreate(
        raw_material_id=1,
        movement_type=StockMovementType.IN,
        quantity=50.0,
        rate_per_unit=180.0,
        total_amount=9000.0,
        movement_date=date(2026, 9, 7)
    )
    assert movement_create.quantity == 50.0
    with pytest.raises(ValidationError):
        StockMovementCreate(raw_material_id=1, movement_type=StockMovementType.IN, quantity=-5.0)


def test_purchase_schemas():
    """Verify clean domain Purchase and PurchaseItem Create/Update/Response schemas."""
    item_create = PurchaseItemCreate(
        product_name="Mild Steel Plate 10mm",
        specification="10mm x 4ft x 8ft",
        quantity=5.0,
        weight=250.0,
        rate_per_unit=140.0,
        total_amount=35000.0
    )
    purchase_create = PurchaseCreate(
        supplier_id=15,
        purchase_date=date(2026, 9, 1),
        voucher_no="VCH-9921",
        paid_amount=20000.0,
        items=[item_create]
    )
    assert purchase_create.supplier_id == 15
    assert len(purchase_create.items) == 1

    purchase_resp = PurchaseResponse(
        id="uuid-9999",
        display_id="BEW-BUY-1",
        supplier_id=15,
        supplier_name="National Steel Corporation",
        total_amount=35000.0,
        paid_amount=20000.0,
        payment_status=PaymentStatus.PARTIAL,
        item_count=1,
        items=[
            PurchaseItemResponse(
                id=1,
                purchase_id="uuid-9999",
                **item_create.model_dump()
            )
        ]
    )
    assert purchase_resp.supplier_name == "National Steel Corporation"
    assert purchase_resp.payment_status == PaymentStatus.PARTIAL
    assert Purchase == PurchaseResponse
    assert SupplierPurchase == PurchaseResponse


def test_sale_schemas():
    """Verify Sale and SaleItem Create/Update/Response schemas."""
    item_create = SaleItemCreate(
        product_name="Finished Spur Gear 40T",
        quantity=2.0,
        unit_price=8500.0,
        total_price=17000.0
    )
    sale_create = SaleCreate(
        buyer_id=1,
        sale_date=date(2026, 9, 2),
        total_amount=17000.0,
        items=[item_create]
    )
    assert sale_create.buyer_id == 1

    sale_resp = SaleResponse(
        id=5,
        display_id="BEW-TRX-5",
        buyer_id=1,
        buyer_name="Square Pharmaceuticals Ltd.",
        total_amount=17000.0,
        item_count=1,
        items=[
            SaleItemResponse(
                id=1,
                sale_id=5,
                **item_create.model_dump()
            )
        ]
    )
    assert sale_resp.buyer_name == "Square Pharmaceuticals Ltd."
    assert Sale == SaleResponse


def test_work_order_schemas():
    """Verify WorkOrder, Parts, Documents with pure domain buyer_id and company_id alias."""
    doc_create = WorkOrderDocumentCreate(
        file_path="uploads/drawings/dwg_001.pdf",
        document_type="Drawing",
        notes="Shaft blueprint rev 2"
    )
    part_create = WorkOrderPartCreate(
        part_name="Hardened Pin 25mm",
        qty=4.0,
        price=1200.0
    )
    # Validate that buyer_id accepts both 'buyer_id' and 'company_id' alias
    wo_create_by_alias = WorkOrderCreate.model_validate({
        "company_id": 1,
        "job_name": "Turbine Impeller Machining",
        "quoted_price": 50000.0,
        "parts": [part_create.model_dump()],
        "documents": [doc_create.model_dump()]
    })
    assert wo_create_by_alias.buyer_id == 1
    assert wo_create_by_alias.job_name == "Turbine Impeller Machining"

    wo_resp = WorkOrderResponse(
        id="uuid-wo-1",
        display_id="BEW-WO-1",
        company_id=1,
        company_name="Square Pharmaceuticals Ltd.",
        job_name=wo_create_by_alias.job_name,
        status=WorkOrderStatus.IN_PROGRESS,
        quoted_price=50000.0,
        paid_amount=20000.0,
        pending_amount=30000.0,
        parts=[WorkOrderPartResponse(id=1, work_order_id="uuid-wo-1", **part_create.model_dump())],
        documents=[WorkOrderDocumentResponse(id=1, work_order_id="uuid-wo-1", **doc_create.model_dump())]
    )
    assert wo_resp.buyer_id == 1
    assert wo_resp.buyer_name == "Square Pharmaceuticals Ltd."
    assert wo_resp.status == WorkOrderStatus.IN_PROGRESS
    assert len(wo_resp.parts) == 1
    assert WorkOrder == WorkOrderResponse


def test_analytics_and_visitor_schemas():
    """Verify VisitorMessage and AnalyticsLog schemas."""
    msg_create = VisitorMessageCreate(
        name="Engr. Farhan",
        email="farhan@textilemill.com",
        phone="01811223344",
        subject="Boiler repair quotation",
        message="Need quotation for boiler shaft turning."
    )
    msg_resp = VisitorMessageResponse(id=1, ip_address="192.168.1.50", **msg_create.model_dump())
    assert msg_resp.id == 1
    assert msg_resp.name == "Engr. Farhan"

    log_create = AnalyticsLogCreate(ip_address="127.0.0.1", page_url="/shops/search")
    log_resp = AnalyticsLogResponse(id=10, **log_create.model_dump())
    assert log_resp.id == 10
