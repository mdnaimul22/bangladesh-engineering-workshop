from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from database import db, Buyer, InventoryItem, Sale, SaleItem
from flask_babel import _
from werkzeug.utils import secure_filename
import os
import uuid
import datetime
from python.app.utils import allowed_file

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales')
def sale_list():
    """Record of all material/product sales"""
    sales = db.get_all_sales()
    return render_template('sales/sale_list.html', sales=sales)

@sales_bp.route('/sales/new', methods=['GET', 'POST'])
def new_sale():
    """Create a new sales entry"""
    buyers = db.get_all_buyers()
    inventory_items = db.get_all_inventory()
    
    if request.method == 'POST':
        # Handle Voucher Upload
        voucher_filename = None
        if 'voucher_image' in request.files:
            file = request.files['voucher_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"voucher_{uuid.uuid4()}_{filename}"
                voucher_folder = current_app.config['SALES_VOUCHER_FOLDER']
                os.makedirs(voucher_folder, exist_ok=True)
                file.save(os.path.join(voucher_folder, unique_filename))
                voucher_filename = f"sales_voucher/{unique_filename}"
        
        # Parse Items
        items = []
        product_names = request.form.getlist('product_name')
        quantities = request.form.getlist('quantity')
        unit_prices = request.form.getlist('unit_price')
        weights = request.form.getlist('weight')
        inventory_links = request.form.getlist('inventory_link_id')
        
        for i in range(len(product_names)):
            if product_names[i]:
                items.append({
                    'product_name': product_names[i],
                    'quantity': float(quantities[i] or 0) if i < len(quantities) else 0,
                    'unit_price': float(unit_prices[i] or 0) if i < len(unit_prices) else 0,
                    'weight': float(weights[i] or 0) if i < len(weights) else 0,
                    'inventory_link_id': inventory_links[i] if i < len(inventory_links) and inventory_links[i] else None
                })
        
        sale_date = request.form.get('sale_date')
        parsed_date = datetime.datetime.strptime(sale_date, '%Y-%m-%d').date() if sale_date else datetime.date.today()
        
        sale_data = {
            'buyer_id': request.form.get('buyer_id'),
            'sale_date': parsed_date,
            'voucher_image': voucher_filename,
            'items': items
        }
        
        sale_id = db.add_sale(sale_data)
        flash(_('Sale created successfully!'), 'success')
        return redirect(url_for('sales.sale_detail', sale_id=sale_id))
        
    pre_selected_buyer_id = request.args.get('buyer_id', type=int)
    sale = {'buyer_id': pre_selected_buyer_id} if pre_selected_buyer_id else {}
    
    return render_template('sales/sale_form.html', buyers=buyers, inventory=inventory_items, sale=sale, action='add')

@sales_bp.route('/sales/<int:sale_id>/edit', methods=['GET', 'POST'])
def edit_sale(sale_id):
    """Modify existing sales entry"""
    sale = db.get_sale_by_id(sale_id)
    if not sale:
        flash(_('Sale record not found!'), 'error')
        return redirect(url_for('sales.sale_list'))
    
    buyers = db.get_all_buyers()
    inventory_items = db.get_all_inventory()
    
    if request.method == 'POST':
        voucher_filename = sale.get('voucher_image')
        if 'voucher_image' in request.files:
            file = request.files['voucher_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"voucher_{uuid.uuid4()}_{filename}"
                voucher_folder = current_app.config['SALES_VOUCHER_FOLDER']
                os.makedirs(voucher_folder, exist_ok=True)
                file.save(os.path.join(voucher_folder, unique_filename))
                voucher_filename = f"sales_voucher/{unique_filename}"
        
        items = []
        product_names = request.form.getlist('product_name')
        quantities = request.form.getlist('quantity')
        unit_prices = request.form.getlist('unit_price')
        weights = request.form.getlist('weight')
        inventory_links = request.form.getlist('inventory_link_id')
        
        for i in range(len(product_names)):
            if product_names[i]:
                items.append({
                    'product_name': product_names[i],
                    'quantity': float(quantities[i] or 0) if i < len(quantities) else 0,
                    'unit_price': float(unit_prices[i] or 0) if i < len(unit_prices) else 0,
                    'weight': float(weights[i] or 0) if i < len(weights) else 0,
                    'inventory_link_id': inventory_links[i] if i < len(inventory_links) and inventory_links[i] else None
                })
        
        sale_date = request.form.get('sale_date')
        parsed_date = datetime.datetime.strptime(sale_date, '%Y-%m-%d').date() if sale_date else datetime.date.today()
        
        sale_data = {
            'buyer_id': request.form.get('buyer_id'),
            'sale_date': parsed_date,
            'voucher_image': voucher_filename,
            'items': items
        }
        
        db.update_sale(sale_id, sale_data)
        flash(_('Sale record updated successfully!'), 'success')
        return redirect(url_for('sales.sale_detail', sale_id=sale_id))
        
    return render_template('sales/sale_form.html', buyers=buyers, inventory=inventory_items, sale=sale, action='edit')

@sales_bp.route('/sales/<int:sale_id>')
def sale_detail(sale_id):
    """Invoice/Sale detailed view"""
    sale = db.get_sale_by_id(sale_id)
    if not sale:
        flash(_('Sale not found!'), 'error')
        return redirect(url_for('sales.sale_list'))
        
    return render_template('sales/sale_detail.html', sale=sale)

@sales_bp.route('/sales/<int:sale_id>/delete', methods=['POST'])
def delete_sale(sale_id):
    """Remove sales record"""
    if db.delete_sale(sale_id):
        flash(_('Sale deleted successfully!'), 'success')
    else:
        flash(_('Error deleting sale!'), 'error')
    return redirect(url_for('sales.sale_list'))
