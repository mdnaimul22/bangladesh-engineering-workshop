"""Inventory service — business logic for raw material inventory management."""
import datetime
from sqlalchemy import or_
from src.config import setup_logger, Settings
from src.db.database import db, InventoryItem
from src.helpers.exceptions import ValidationError
from src.helpers.auth import verify_delete_password

logger = setup_logger(Settings.LOG_DIR / "services.log", name="bew.services.inventory")


def list_all():
    """Return all inventory items."""
    return db.get_all_inventory()


def create(form_data) -> int:
    """Create a new inventory item from form data.

    Args:
        form_data: Flask request.form object.

    Returns:
        The new item's ID.

    Raises:
        ValidationError: If required fields are missing.
    """
    shop_id = form_data.get('shop_id')
    material_name = form_data.get('material_name')

    if not shop_id or not material_name:
        raise ValidationError("Shop and Material Name are required!")

    purchase_date = None
    raw_date = form_data.get('purchase_date')
    if raw_date:
        try:
            purchase_date = datetime.datetime.strptime(raw_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

    data = {
        'shop_id': shop_id,
        'material_name': material_name,
        'quantity': form_data.get('quantity'),
        'cost': form_data.get('cost'),
        'tags': form_data.get('tags'),
        'purchase_date': purchase_date,
    }

    item_id = db.add_inventory(data)
    logger.info(f"Created inventory item #{item_id}: {material_name}")
    return item_id


def remove(item_id: int, password: str = '') -> bool:
    """Delete an inventory item.

    Args:
        item_id: The item to delete.
        password: Admin password for delete verification.

    Returns:
        True if deleted.

    Raises:
        ValidationError: If password check fails.
    """
    verify_delete_password(password)

    if db.delete_inventory(item_id):
        logger.info(f"Deleted inventory item #{item_id}")
        return True
    return False


def search(query: str):
    """Search inventory items by name or tags."""
    if not query:
        return []

    items = InventoryItem.query.filter(
        or_(
            InventoryItem.material_name.ilike(f'%{query}%'),
            InventoryItem.tags.ilike(f'%{query}%')
        )
    ).limit(20).all()

    return [{
        'id': item.id,
        'name': item.material_name,
        'qty': item.quantity,
        'tags': item.tags,
        'shop_name': item.shop.name if item.shop else 'Unknown',
        'cost': item.cost,
    } for item in items]


def list_shops():
    """Return all shops for the inventory form dropdown."""
    return db.get_all_shops()
