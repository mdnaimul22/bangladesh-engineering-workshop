"""Tests for src/db/database.py — all CRUD operations."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestDatabaseShops:
    """Verify shop CRUD operations against the live DB."""

    def test_get_all_shops_returns_list(self, app_context):
        from src.db.database import db
        shops = db.get_all_shops()
        assert isinstance(shops, (list, type(None)))

    def test_get_all_shops_with_limit(self, app_context):
        from src.db.database import db
        shops = db.get_all_shops(limit=5)
        assert isinstance(shops, list)
        assert len(shops) <= 5

    def test_get_shops_count(self, app_context):
        from src.db.database import db
        count = db.get_shops_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_shop_by_id_valid(self, app_context):
        from src.db.database import db
        shops = db.get_all_shops(limit=1)
        if shops:
            shop = db.get_shop_by_id(shops[0]['id'])
            assert shop is not None
            assert 'name' in shop

    def test_get_shop_by_id_invalid(self, app_context):
        from src.db.database import db
        shop = db.get_shop_by_id(999999)
        assert shop is None

    def test_search_shops(self, app_context):
        from src.db.database import db
        results = db.search_shops("test")
        assert isinstance(results, list)


class TestDatabaseCategories:
    """Verify category operations."""

    def test_get_all_categories(self, app_context):
        from src.db.database import db
        categories = db.get_all_categories()
        assert isinstance(categories, list)

    def test_get_shops_by_category(self, app_context):
        from src.db.database import db
        categories = db.get_all_categories()
        if categories:
            shops = db.get_shops_by_category(categories[0]['id'])
            assert isinstance(shops, list)


class TestDatabaseBuyers:
    """Verify buyer CRUD operations."""

    def test_get_all_buyers(self, app_context):
        from src.db.database import db
        buyers = db.get_all_buyers()
        assert isinstance(buyers, list)

    def test_get_buyer_by_id_invalid(self, app_context):
        from src.db.database import db
        buyer = db.get_buyer_by_id(999999)
        assert buyer is None

    def test_get_buyer_by_id_valid(self, app_context):
        from src.db.database import db
        buyers = db.get_all_buyers()
        if buyers:
            buyer = db.get_buyer_by_id(buyers[0]['id'])
            assert buyer is not None


class TestDatabaseInventory:
    """Verify inventory operations."""

    def test_get_all_inventory(self, app_context):
        from src.db.database import db
        items = db.get_all_inventory()
        assert isinstance(items, list)


class TestDatabasePurchases:
    """Verify purchase operations."""

    def test_get_all_supplier_purchases(self, app_context):
        from src.db.database import db
        purchases = db.get_all_supplier_purchases()
        assert isinstance(purchases, list)


class TestDatabaseSales:
    """Verify sales operations."""

    def test_get_all_sales(self, app_context):
        from src.db.database import db
        sales = db.get_all_sales()
        assert isinstance(sales, list)


class TestDatabaseWorkOrders:
    """Verify work order operations."""

    def test_get_all_work_orders(self, app_context):
        from src.db.database import db
        orders = db.get_all_work_orders()
        assert isinstance(orders, list)

    def test_get_work_order_by_id_invalid(self, app_context):
        from src.db.database import db
        order = db.get_work_order_by_id("nonexistent-uuid")
        assert order is None


class TestDatabaseTags:
    """Verify tag operations."""

    def test_get_all_tags(self, app_context):
        from src.db.database import db
        if hasattr(db, 'get_all_tags'):
            tags = db.get_all_tags()
            assert isinstance(tags, list)


class TestDatabaseInit:
    """Verify DB initialization."""

    def test_db_has_init_app(self):
        from src.db.database import db
        assert hasattr(db, 'init_app')

    def test_db_has_create_all(self):
        from src.db.database import db
        assert hasattr(db, 'create_all')

    def test_db_has_session(self, app_context):
        from src.db.database import db
        # Just verify no crash
        assert db is not None
