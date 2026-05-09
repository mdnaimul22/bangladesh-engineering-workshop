"""Inventory routes — thin HTTP wrapper over inventory service."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import _
import src.services.inventory_svc as inventory_svc
from src.helpers.exceptions import ValidationError
from src.config import setup_logger, Settings

logger = setup_logger(Settings.LOG_DIR / "routers.log", name="bew.routers.inventory")

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/inventory')
def inventory_list():
    """List all inventory items"""
    inventory = inventory_svc.list_all()
    page = request.args.get('page', 1, type=int)
    from src.helpers.utils import paginate_list
    inventory, meta = paginate_list(inventory, page, per_page=10)
    return render_template('inventory/inventory_list.html', inventory=inventory, meta=meta)


@inventory_bp.route('/inventory/new', methods=['GET', 'POST'])
def new_inventory():
    """Add new inventory item"""
    shops = inventory_svc.list_shops()

    if request.method == 'POST':
        try:
            inventory_svc.create(request.form)
            flash(_('Inventory added successfully!'), 'success')
            return redirect(url_for('inventory.inventory_list'))
        except ValidationError as e:
            flash(_(str(e)), 'error')
            return render_template('inventory/inventory_form.html', shops=shops)

    return render_template('inventory/inventory_form.html', shops=shops)


@inventory_bp.route('/inventory/<int:item_id>/delete', methods=['POST'])
def delete_inventory(item_id):
    """Delete inventory item"""
    password = request.form.get('delete_password', '')
    try:
        if inventory_svc.remove(item_id, password):
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
    results = inventory_svc.search(query)
    return jsonify(results)
