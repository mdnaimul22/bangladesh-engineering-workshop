"""Tests for src/routers — HTTP endpoint smoke tests."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCoreRoutes:
    """Verify core (static) routes respond."""

    def test_about_page(self, client):
        resp = client.get('/about')
        assert resp.status_code in (200, 302)

    def test_services_page(self, client):
        resp = client.get('/our-services')
        assert resp.status_code in (200, 302)


class TestShopRoutes:
    """Verify shop routes respond."""

    def test_home_page(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_shop_list(self, client):
        resp = client.get('/shops')
        assert resp.status_code == 200

    def test_shop_detail_invalid(self, client):
        """Non-existent shop should redirect or return error."""
        resp = client.get('/shops/999999')
        assert resp.status_code in (302, 404)

    def test_new_shop_get(self, client):
        resp = client.get('/shops/new')
        assert resp.status_code == 200

    def test_search_api(self, client):
        resp = client.get('/api/search?q=test')
        assert resp.status_code == 200


class TestBuyerRoutes:
    """Verify buyer routes respond."""

    def test_buyer_list(self, client):
        resp = client.get('/buyers')
        assert resp.status_code == 200

    def test_new_buyer_get(self, client):
        resp = client.get('/buyers/new')
        assert resp.status_code == 200

    def test_buyer_detail_invalid(self, client):
        resp = client.get('/buyers/999999')
        assert resp.status_code in (302, 404)


class TestInventoryRoutes:
    """Verify inventory routes respond."""

    def test_inventory_list(self, client):
        resp = client.get('/inventory')
        assert resp.status_code == 200

    def test_new_inventory_get(self, client):
        resp = client.get('/inventory/new')
        assert resp.status_code == 200


class TestPurchaseRoutes:
    """Verify purchase routes respond."""

    def test_purchase_list(self, client):
        resp = client.get('/purchases')
        assert resp.status_code == 200

    def test_new_purchase_get(self, client):
        resp = client.get('/purchases/new')
        assert resp.status_code == 200


class TestSalesRoutes:
    """Verify sales routes respond."""

    def test_sale_list(self, client):
        resp = client.get('/sales')
        assert resp.status_code == 200

    def test_new_sale_get(self, client):
        resp = client.get('/sales/new')
        assert resp.status_code == 200


class TestWorkOrderRoutes:
    """Verify work order routes respond."""

    def test_work_order_list(self, client):
        resp = client.get('/work-orders')
        assert resp.status_code == 200

    def test_new_work_order_get(self, client):
        resp = client.get('/work-orders/new')
        assert resp.status_code == 200


class TestLanguageRoute:
    """Verify language switching."""

    def test_set_language_bn(self, client):
        resp = client.get('/set_lang/bn')
        assert resp.status_code == 302  # redirect

    def test_set_language_en(self, client):
        resp = client.get('/set_lang/en')
        assert resp.status_code == 302

    def test_set_language_invalid(self, client):
        resp = client.get('/set_lang/fr')
        assert resp.status_code == 302  # still redirects, just doesn't set


class TestErrorHandlers:
    """Verify error handlers respond correctly."""

    def test_404_html(self, client):
        resp = client.get('/nonexistent-page-xyz')
        assert resp.status_code == 404

    def test_404_api(self, client):
        resp = client.get('/api/nonexistent-xyz')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data is not None
        assert 'error' in data

    def test_405_api(self, client):
        """POST to a GET-only endpoint should return 405."""
        resp = client.post('/api/search')
        assert resp.status_code == 405
