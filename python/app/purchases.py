from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from database import db, Shop, SupplierPurchase, SupplierPurchaseItem
from flask_babel import _
from werkzeug.utils import secure_filename
import os
import uuid
import datetime
from python.app.utils import allowed_file

purchases_bp = Blueprint('purchases', __name__)

@purchases_bp.route('/purchases')
def purchase_list():
    """List all supplier purchases"""
    purchases = db.get_all_supplier_purchases()
    return render_template('purchase/purchase_list.html', purchases=purchases, supplier=None)

@purchases_bp.route('/shops/<int:shop_id>/purchases')
def shop_purchases(shop_id):
    """List purchases from a specific supplier"""
    supplier = db.get_shop_by_id(shop_id)
    if not supplier:
        flash(_('দোকান খুঁজে পাওয়া যায়নি!'), 'error')
        return redirect(url_for('shops.shop_list'))
    purchases = db.get_supplier_purchases(shop_id)
    return render_template('purchase/purchase_list.html', purchases=purchases, supplier=supplier)

@purchases_bp.route('/purchases/new', methods=['GET', 'POST'])
def new_purchase():
    """Log a new purchase voucher"""
    shops = db.get_all_shops()
    preselected_supplier_id = request.args.get('supplier_id', type=int)

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        if not supplier_id:
            flash(_('Supplier is required!'), 'error')
            return render_template('purchase/purchase_form.html', action='add', purchase={}, shops=shops, preselected_supplier_id=preselected_supplier_id)

        purchase_date = datetime.datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date() if request.form.get('purchase_date') else None

        voucher_path = ''
        if 'voucher_file' in request.files:
            file = request.files['voucher_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"voucher_{uuid.uuid4()}_{filename}"
                voucher_folder = current_app.config['PURCHASE_VOUCHER_FOLDER']
                os.makedirs(voucher_folder, exist_ok=True)
                file.save(os.path.join(voucher_folder, unique_filename))
                voucher_path = f"purchase_voucher/{unique_filename}"

        product_names = request.form.getlist('product_name')
        specifications = request.form.getlist('specification')
        quantities = request.form.getlist('quantity')
        units = request.form.getlist('unit')
        rates = request.form.getlist('rate_per_unit')
        stock_statuses = request.form.getlist('stock_status')

        items = []
        for i in range(len(product_names)):
            if not product_names[i]:
                continue
            qty = float(quantities[i] or 0) if i < len(quantities) else 0
            rate = float(rates[i] or 0) if i < len(rates) else 0
            items.append({
                'product_name': product_names[i],
                'specification': specifications[i] if i < len(specifications) else '',
                'quantity': qty,
                'unit': units[i] if i < len(units) else '',
                'rate_per_unit': rate,
                'total_amount': qty * rate,
                'stock_status': stock_statuses[i] if i < len(stock_statuses) else 'IN_STOCK'
            })

        purchase_data = {
            'supplier_id': supplier_id,
            'purchase_date': purchase_date,
            'voucher_no': request.form.get('voucher_no'),
            'voucher_file_path': voucher_path,
            'payment_status': request.form.get('payment_status'),
            'paid_amount': request.form.get('paid_amount'),
            'notes': request.form.get('notes'),
            'items': items
        }

        purchase_id = db.add_supplier_purchase(purchase_data)
        flash(_('Purchase saved successfully!'), 'success')
        return redirect(url_for('purchases.purchase_detail', purchase_id=purchase_id))

    return render_template('purchase/purchase_form.html', action='add', purchase={}, shops=shops, preselected_supplier_id=preselected_supplier_id)

@purchases_bp.route('/purchases/<purchase_id>')
def purchase_detail(purchase_id):
    """View purchase voucher details"""
    purchase = db.get_supplier_purchase_by_id(purchase_id)
    if not purchase:
        flash(_('Purchase not found!'), 'error')
        return redirect(url_for('purchases.purchase_list'))
    return render_template('purchase/purchase_detail.html', purchase=purchase)

@purchases_bp.route('/purchases/<purchase_id>/edit', methods=['GET', 'POST'])
def edit_purchase(purchase_id):
    """Update purchase voucher details"""
    purchase = db.get_supplier_purchase_by_id(purchase_id)
    if not purchase:
        flash(_('Purchase not found!'), 'error')
        return redirect(url_for('purchases.purchase_list'))

    shops = db.get_all_shops()

    if request.method == 'POST':
        purchase_date = datetime.datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date() if request.form.get('purchase_date') else None

        voucher_path = purchase.get('voucher_file_path') or ''
        if 'voucher_file' in request.files:
            file = request.files['voucher_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"voucher_{uuid.uuid4()}_{filename}"
                voucher_folder = current_app.config['PURCHASE_VOUCHER_FOLDER']
                os.makedirs(voucher_folder, exist_ok=True)
                file.save(os.path.join(voucher_folder, unique_filename))
                voucher_path = f"purchase_voucher/{unique_filename}"

        product_names = request.form.getlist('product_name')
        specifications = request.form.getlist('specification')
        quantities = request.form.getlist('quantity')
        units = request.form.getlist('unit')
        rates = request.form.getlist('rate_per_unit')
        stock_statuses = request.form.getlist('stock_status')

        items = []
        for i in range(len(product_names)):
            if not product_names[i]:
                continue
            qty = float(quantities[i] or 0) if i < len(quantities) else 0
            rate = float(rates[i] or 0) if i < len(rates) else 0
            items.append({
                'product_name': product_names[i],
                'specification': specifications[i] if i < len(specifications) else '',
                'quantity': qty,
                'unit': units[i] if i < len(units) else '',
                'rate_per_unit': rate,
                'total_amount': qty * rate,
                'stock_status': stock_statuses[i] if i < len(stock_statuses) else 'IN_STOCK'
            })

        purchase_data = {
            'supplier_id': request.form.get('supplier_id') or purchase.get('supplier_id'),
            'purchase_date': purchase_date,
            'voucher_no': request.form.get('voucher_no'),
            'voucher_file_path': voucher_path,
            'payment_status': request.form.get('payment_status'),
            'paid_amount': request.form.get('paid_amount'),
            'notes': request.form.get('notes'),
            'items': items
        }

        db.update_supplier_purchase(purchase_id, purchase_data)
        flash(_('Purchase updated successfully!'), 'success')
        return redirect(url_for('purchases.purchase_detail', purchase_id=purchase_id))

    return render_template('purchase/purchase_form.html', action='edit', purchase=purchase, shops=shops, preselected_supplier_id=purchase.get('supplier_id'))

@purchases_bp.route('/purchases/<purchase_id>/delete', methods=['POST'])
def delete_purchase(purchase_id):
    """Delete purchase record"""
    if db.delete_supplier_purchase(purchase_id):
        flash(_('Purchase deleted successfully!'), 'success')
    else:
        flash(_('Error deleting purchase!'), 'error')
    return redirect(url_for('purchases.purchase_list'))
