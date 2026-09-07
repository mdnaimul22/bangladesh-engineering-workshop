"""Inventory routes — thin HTTP wrapper over inventory service."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import _
from src.services import inventory as inventory_service
from src.helpers.exceptions import ValidationError
from src.config import setup_logger, Settings

from src.helpers.auth_middleware import admin_required

logger = setup_logger(Settings.LOG_DIR / "routers.log", name="bew.routers.inventory")

inventory_bp = Blueprint('inventory', __name__, url_prefix='/dashboard')

@inventory_bp.before_request
@admin_required
def before_request():
    pass


@inventory_bp.route('/inventory')
def inventory_list():
    """List all inventory items"""
    query = request.args.get('q', '').strip()
    inventory = inventory_service.list_all(query)
    page = request.args.get('page', 1, type=int)
    from src.helpers.utils import paginate_list
    inventory, meta = paginate_list(inventory, page, per_page=10)
    return render_template('dashboard/inventory/inventory_list.html', inventory=inventory, meta=meta, search_query=query)


@inventory_bp.route('/inventory/new', methods=['GET', 'POST'])
def new_inventory():
    """Add new inventory item"""
    shops = inventory_service.list_shops()

    if request.method == 'POST':
        try:
            inventory_service.create(request.form)
            flash(_('Inventory added successfully!'), 'success')
            return redirect(url_for('inventory.inventory_list'))
        except ValidationError as e:
            flash(_(str(e)), 'error')
            return render_template('dashboard/inventory/inventory_form.html', shops=shops)

    return render_template('dashboard/inventory/inventory_form.html', shops=shops)


@inventory_bp.route('/inventory/<int:item_id>/delete', methods=['POST'])
def delete_inventory(item_id):
    """Delete inventory item"""
    password = request.form.get('delete_password', '')
    try:
        if inventory_service.remove(item_id, password):
            flash(_('Inventory item deleted successfully!'), 'success')
        else:
            flash(_('Error deleting inventory item!'), 'error')
    except ValidationError as e:
        flash(_(str(e)), 'error')
    return redirect(url_for('inventory.inventory_list'))


@inventory_bp.route('/api/inventory/search')
def api_inventory_search():
    """API endpoint for searching inventory items"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    results = inventory_service.search(query)
    return jsonify(results)

