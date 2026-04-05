from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db, InventoryItem, Shop
from flask_babel import _
from sqlalchemy import or_
import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
def inventory_list():
    """List all inventory items"""
    inventory = db.get_all_inventory()
    return render_template('inventory/inventory_list.html', inventory=inventory)

@inventory_bp.route('/inventory/new', methods=['GET', 'POST'])
def new_inventory():
    """Add new inventory item"""
    shops = db.get_all_shops()
    
    if request.method == 'POST':
        data = {
            'shop_id': request.form.get('shop_id'),
            'material_name': request.form.get('material_name'),
            'quantity': request.form.get('quantity'),
            'cost': request.form.get('cost'),
            'tags': request.form.get('tags'),
            'purchase_date': datetime.datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date() if request.form.get('purchase_date') else None
        }
        
        if not data['shop_id'] or not data['material_name']:
            flash(_('Shop and Material Name are required!'), 'error')
            return render_template('inventory/inventory_form.html', shops=shops)

        db.add_inventory(data)
        flash(_('Inventory added successfully!'), 'success')
        return redirect(url_for('inventory.inventory_list'))

    return render_template('inventory/inventory_form.html', shops=shops)

@inventory_bp.route('/inventory/<int:item_id>/delete', methods=['POST'])
def delete_inventory(item_id):
    if db.delete_inventory(item_id):
        flash(_('Inventory item deleted successfully!'), 'success')
    else:
        flash(_('Error deleting inventory item!'), 'error')
    return redirect(url_for('inventory.inventory_list'))

@inventory_bp.route('/api/inventory/search')
def api_inventory_search():
    """API endpoint for searching inventory items"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
        
    items = InventoryItem.query.filter(
        or_(
            InventoryItem.material_name.ilike(f'%{query}%'),
            InventoryItem.tags.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    results = []
    for item in items:
        # Include source shop info
        results.append({
            'id': item.id,
            'name': item.material_name,
            'qty': item.quantity,
            'tags': item.tags,
            'shop_name': item.shop.name if item.shop else 'Unknown',
            'cost': item.cost
        })
    return jsonify(results)
