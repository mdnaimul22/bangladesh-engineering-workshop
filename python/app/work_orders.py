from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from database import db, Buyer, Shop, WorkOrder, WorkOrderPart
from flask_babel import _
from werkzeug.utils import secure_filename
import os
import uuid
import datetime
from python.app.utils import allowed_file

work_orders_bp = Blueprint('work_orders', __name__)

@work_orders_bp.route('/work-orders')
def work_order_list():
    """Master list of all production jobs"""
    work_orders = db.get_all_work_orders()
    return render_template('work_orders/work_order_list.html', work_orders=work_orders)

@work_orders_bp.route('/work-orders/new', methods=['GET', 'POST'])
def new_work_order():
    """Create a new work order"""
    companies = db.get_all_buyers()
    suppliers = db.get_all_shops()
    
    # Pre-select buyer if buyer_id is provided in the query string
    pre_selected_buyer_id = request.args.get('buyer_id', type=int)
    work_order = {'company_id': pre_selected_buyer_id} if pre_selected_buyer_id else {}

    if request.method == 'POST':
        company_id = request.form.get('company_id')
        if not company_id:
            flash(_('Company is required!'), 'error')
            return render_template('work_orders/work_order_form.html', action='add', work_order={}, companies=companies, suppliers=suppliers)

        job_date = datetime.datetime.strptime(request.form.get('job_date'), '%Y-%m-%d').date() if request.form.get('job_date') else None
        delivery_date = datetime.datetime.strptime(request.form.get('delivery_date'), '%Y-%m-%d').date() if request.form.get('delivery_date') else None

        part_names = request.form.getlist('part_name')
        supplier_ids = request.form.getlist('supplier_id')
        voucher_file_paths = request.form.getlist('voucher_file_path')
        measurements = request.form.getlist('measurement')
        units = request.form.getlist('unit')
        qtys = request.form.getlist('qty')
        weights = request.form.getlist('weight')
        prices = request.form.getlist('price')

        parts = []
        for i in range(len(part_names)):
            if not part_names[i]:
                continue

            voucher_path = voucher_file_paths[i] if i < len(voucher_file_paths) else ''
            file = request.files.get(f'voucher_file_{i}')
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                voucher_folder = current_app.config['PURCHASE_VOUCHER_FOLDER']
                os.makedirs(voucher_folder, exist_ok=True)
                
                # Check for collision
                if os.path.exists(os.path.join(voucher_folder, filename)):
                    flash(_('File with name "%(name)s" already exists in vouchers. Please rename and re-upload.', name=filename), 'error')
                    return redirect(request.url)
                    
                file.save(os.path.join(voucher_folder, filename))
                voucher_path = f"purchase_voucher/{filename}"

            parts.append({
                'part_name': part_names[i],
                'supplier_id': supplier_ids[i] if i < len(supplier_ids) and supplier_ids[i] else None,
                'voucher_no': '',
                'voucher_file_path': voucher_path,
                'measurement': measurements[i] if i < len(measurements) else '',
                'unit': units[i] if i < len(units) else '',
                'qty': qtys[i] if i < len(qtys) else 0,
                'weight': weights[i] if i < len(weights) else 0,
                'price': prices[i] if i < len(prices) else 0
            })

        # Handle Hard Copy Scan
        hard_copy_path = request.form.get('hard_copy_path', '')
        hard_copy_file = request.files.get('hard_copy_file')
        if hard_copy_file and hard_copy_file.filename and allowed_file(hard_copy_file.filename):
            filename = secure_filename(hard_copy_file.filename)
            upload_folder = current_app.config['WORK_ORDER_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Check for collision
            if os.path.exists(os.path.join(upload_folder, filename)):
                flash(_('File with name "%(name)s" already exists in work orders. Please rename and re-upload.', name=filename), 'error')
                return redirect(request.url)
                
            hard_copy_file.save(os.path.join(upload_folder, filename))
            hard_copy_path = f"work_orders/{filename}"

        # Handle Gallery Documents
        doc_types = request.form.getlist('doc_type')
        doc_notes = request.form.getlist('doc_notes')
        doc_file_paths = request.form.getlist('doc_file_path')

        documents = []
        for i in range(len(doc_types)):
            doc_path = doc_file_paths[i] if i < len(doc_file_paths) else ''
            file = request.files.get(f'gallery_file_{i}')
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['GALLERY_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                
                # Check for collision
                if os.path.exists(os.path.join(upload_folder, filename)):
                    flash(_('File with name "%(name)s" already exists in gallery. Please rename and re-upload.', name=filename), 'error')
                    return redirect(request.url)
                    
                file.save(os.path.join(upload_folder, filename))
                doc_path = f"gallery/{filename}"
            
            if doc_path:
                documents.append({
                    'file_path': doc_path,
                    'document_type': doc_types[i] if i < len(doc_types) else 'Other',
                    'notes': doc_notes[i] if i < len(doc_notes) else ''
                })

        data = {
            'company_id': company_id,
            'job_date': job_date,
            'job_name': request.form.get('job_name'),
            'job_description': request.form.get('job_description'),
            'status': request.form.get('status'),
            'quoted_price': request.form.get('quoted_price'),
            'delivery_date': delivery_date,
            'labor_cost': request.form.get('labor_cost'),
            'material_cost': request.form.get('material_cost'),
            'total_cost': request.form.get('total_cost'),
            'hard_copy_path': hard_copy_path,
            'parts': parts,
            'documents': documents
        }

        work_order_id = db.add_work_order(data)
        flash(_('Work order created successfully!'), 'success')
        return redirect(url_for('work_orders.work_order_detail', work_order_id=work_order_id))

    return render_template('work_orders/work_order_form.html', action='add', work_order={}, companies=companies, suppliers=suppliers)

@work_orders_bp.route('/work-orders/<work_order_id>')
def work_order_detail(work_order_id):
    """View job specs, parts, and costs"""
    work_order = db.get_work_order_by_id(work_order_id)
    if not work_order:
        flash(_('Work order not found!'), 'error')
        return redirect(url_for('work_orders.work_order_list'))
    return render_template('work_orders/work_order_detail.html', work_order=work_order)

@work_orders_bp.route('/work-orders/<work_order_id>/edit', methods=['GET', 'POST'])
def edit_work_order(work_order_id):
    """Modify production job details"""
    work_order = db.get_work_order_by_id(work_order_id)
    if not work_order:
        flash(_('Work order not found!'), 'error')
        return redirect(url_for('work_orders.work_order_list'))

    companies = db.get_all_buyers()
    suppliers = db.get_all_shops()

    if request.method == 'POST':
        job_date = datetime.datetime.strptime(request.form.get('job_date'), '%Y-%m-%d').date() if request.form.get('job_date') else None
        delivery_date = datetime.datetime.strptime(request.form.get('delivery_date'), '%Y-%m-%d').date() if request.form.get('delivery_date') else None

        part_names = request.form.getlist('part_name')
        supplier_ids = request.form.getlist('supplier_id')
        voucher_file_paths = request.form.getlist('voucher_file_path')
        measurements = request.form.getlist('measurement')
        units = request.form.getlist('unit')
        qtys = request.form.getlist('qty')
        weights = request.form.getlist('weight')
        prices = request.form.getlist('price')

        parts = []
        for i in range(len(part_names)):
            if not part_names[i]:
                continue

            voucher_path = voucher_file_paths[i] if i < len(voucher_file_paths) else ''
            file = request.files.get(f'voucher_file_{i}')
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                voucher_folder = current_app.config['PURCHASE_VOUCHER_FOLDER']
                os.makedirs(voucher_folder, exist_ok=True)
                
                # Check for collision - strictly only for NEW uploads
                if os.path.exists(os.path.join(voucher_folder, filename)):
                    flash(_('File with name "%(name)s" already exists in vouchers. Please rename and re-upload.', name=filename), 'error')
                    return redirect(request.url)
                
                # Delete old file if being replaced
                old_path = request.form.getlist('voucher_file_path')[i] if i < len(request.form.getlist('voucher_file_path')) else ''
                if old_path and old_path != f"purchase_voucher/{filename}":
                    full_old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_path)
                    if os.path.exists(full_old_path):
                        os.remove(full_old_path)
                    
                file.save(os.path.join(voucher_folder, filename))
                voucher_path = f"purchase_voucher/{filename}"

            parts.append({
                'part_name': part_names[i],
                'supplier_id': supplier_ids[i] if i < len(supplier_ids) and supplier_ids[i] else None,
                'voucher_no': '',
                'voucher_file_path': voucher_path,
                'measurement': measurements[i] if i < len(measurements) else '',
                'unit': units[i] if i < len(units) else '',
                'qty': qtys[i] if i < len(qtys) else 0,
                'weight': weights[i] if i < len(weights) else 0,
                'price': prices[i] if i < len(prices) else 0
            })

        # Handle Hard Copy Scan
        hard_copy_path = request.form.get('hard_copy_path', '')
        hard_copy_file = request.files.get('hard_copy_file')
        if hard_copy_file and hard_copy_file.filename and allowed_file(hard_copy_file.filename):
            filename = secure_filename(hard_copy_file.filename)
            upload_folder = current_app.config['WORK_ORDER_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Check for collision
            if os.path.exists(os.path.join(upload_folder, filename)):
                flash(_('File with name "%(name)s" already exists in work orders. Please rename and re-upload.', name=filename), 'error')
                return redirect(request.url)
            
            # Delete old hard copy if being replaced
            old_hard_copy = request.form.get('hard_copy_path')
            if old_hard_copy and old_hard_copy != f"work_orders/{filename}":
                full_old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_hard_copy)
                if os.path.exists(full_old_path):
                    os.remove(full_old_path)
                
            hard_copy_file.save(os.path.join(upload_folder, filename))
            hard_copy_path = f"work_orders/{filename}"

        # Handle Gallery Documents
        doc_types = request.form.getlist('doc_type')
        doc_notes = request.form.getlist('doc_notes')
        doc_file_paths = request.form.getlist('doc_file_path')
        
        documents = []
        for i in range(len(doc_types)):
            doc_path = doc_file_paths[i] if i < len(doc_file_paths) else ''
            file = request.files.get(f'gallery_file_{i}')
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['GALLERY_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                
                # Check for collision
                if os.path.exists(os.path.join(upload_folder, filename)):
                    flash(_('File with name "%(name)s" already exists in gallery. Please rename and re-upload.', name=filename), 'error')
                    return redirect(request.url)

                # Delete old gallery file if being replaced
                old_doc_path = request.form.getlist('doc_file_path')[i] if i < len(request.form.getlist('doc_file_path')) else ''
                if old_doc_path and old_doc_path != f"gallery/{filename}":
                    full_old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_doc_path)
                    if os.path.exists(full_old_path):
                        os.remove(full_old_path)
                    
                file.save(os.path.join(upload_folder, filename))
                doc_path = f"gallery/{filename}"
            
            if doc_path:
                documents.append({
                    'file_path': doc_path,
                    'document_type': doc_types[i] if i < len(doc_types) else 'Other',
                    'notes': doc_notes[i] if i < len(doc_notes) else ''
                })

        data = {
            'company_id': request.form.get('company_id'),
            'job_date': job_date,
            'job_name': request.form.get('job_name'),
            'job_description': request.form.get('job_description'),
            'status': request.form.get('status'),
            'quoted_price': request.form.get('quoted_price'),
            'delivery_date': delivery_date,
            'labor_cost': request.form.get('labor_cost'),
            'material_cost': request.form.get('material_cost'),
            'total_cost': request.form.get('total_cost'),
            'hard_copy_path': hard_copy_path,
            'parts': parts,
            'documents': documents
        }

        db.update_work_order(work_order_id, data)
        flash(_('Work order updated successfully!'), 'success')
        return redirect(url_for('work_orders.work_order_detail', work_order_id=work_order_id))

    return render_template('work_orders/work_order_form.html', action='edit', work_order=work_order, companies=companies, suppliers=suppliers)

@work_orders_bp.route('/work-orders/<work_order_id>/delete', methods=['POST'])
def delete_work_order(work_order_id):
    """Remove production job record"""
    if db.delete_work_order(work_order_id):
        flash(_('Work order deleted successfully!'), 'success')
    else:
        flash(_('Error deleting work order!'), 'error')
    return redirect(url_for('work_orders.work_order_list'))
