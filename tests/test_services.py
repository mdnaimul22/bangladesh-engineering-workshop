"""Tests for src/services — business logic layer."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestShopService:
    """Verify shop service functions."""

    def test_list_all(self, app_context):
        import src.services.shop as svc
        shops, total = svc.list_all(limit=5)
        assert isinstance(shops, list)
        assert isinstance(total, int)

    def test_get_categories(self, app_context):
        import src.services.shop as svc
        cats = svc.get_categories()
        assert isinstance(cats, list)

    def test_search_empty(self, app_context):
        import src.services.shop as svc
        result = svc.search("")
        assert result == []

    def test_get_nonexistent(self, app_context):
        import src.services.shop as svc
        from src.helpers.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            svc.get(999999)

    def test_create_validation(self, app_context):
        """Creating shop without name should raise ValidationError."""
        import src.services.shop as svc
        from src.helpers.exceptions import ValidationError
        from werkzeug.datastructures import MultiDict
        with pytest.raises(ValidationError):
            svc.create(MultiDict({'name': '', 'category_id': '1'}))


class TestBuyerService:
    """Verify buyer service functions."""

    def test_list_all(self, app_context):
        import src.services.buyer as svc
        result = svc.list_all()
        assert isinstance(result, list)

    def test_get_nonexistent(self, app_context):
        import src.services.buyer as svc
        from src.helpers.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            svc.get(999999)

    def test_list_all_nonexistent_query_returns_empty(self, app_context):
        """Searching for a non-existent buyer query must return [] rather than all buyers."""
        import src.services.buyer as svc
        result = svc.list_all("NonExistentBuyerQuery12345XYZ")
        assert result == []


class TestInventoryService:
    """Verify inventory service functions."""

    def test_list_all(self, app_context):
        import src.services.inventory as svc
        result = svc.list_all()
        assert isinstance(result, list)


class TestPurchaseService:
    """Verify purchase service functions."""

    def test_list_all(self, app_context):
        import src.services.purchase as svc
        result = svc.list_all()
        assert isinstance(result, list)

    def test_get_nonexistent(self, app_context):
        import src.services.purchase as svc
        result = svc.get("nonexistent-id")
        assert result is None


class TestSaleService:
    """Verify sale service functions."""

    def test_list_all(self, app_context):
        import src.services.sale as svc
        result = svc.list_all()
        assert isinstance(result, list)

    def test_get_nonexistent(self, app_context):
        import src.services.sale as svc
        result = svc.get(999999)
        assert result is None


class TestWorkOrderService:
    """Verify work order service functions."""

    def test_list_all(self, app_context):
        import src.services.work_order as svc
        result = svc.list_all()
        assert isinstance(result, list)

    def test_create_validation(self, app_context):
        """Creating work order without company should raise ValidationError."""
        import src.services.work_order as svc
        from src.helpers.exceptions import ValidationError
        from werkzeug.datastructures import MultiDict
        with pytest.raises(ValidationError):
            svc.create(MultiDict({'company_id': ''}))

    def test_get_buyers(self, app_context):
        import src.services.work_order as svc
        buyers = svc.get_buyers()
        assert isinstance(buyers, list)

    def test_get_suppliers(self, app_context):
        import src.services.work_order as svc
        suppliers = svc.get_suppliers()
        assert isinstance(suppliers, list)

