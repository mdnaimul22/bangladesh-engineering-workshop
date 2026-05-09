"""Work Order routes — thin HTTP wrapper over work_order service."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_babel import _
import src.services.work_order_svc as work_order_svc
from src.helpers.exceptions import ValidationError
from src.config import setup_logger, Settings

logger = setup_logger(Settings.LOG_DIR / "routers.log", name="bew.routers.work_orders")

work_orders_bp = Blueprint('work_orders', __name__)


@work_orders_bp.route('/work-orders')
def work_order_list():
    """Master list of all production jobs"""
    work_orders = work_order_svc.list_all()
    page = request.args.get('page', 1, type=int)
    from src.helpers.utils import paginate_list
    work_orders, meta = paginate_list(work_orders, page, per_page=10)
    return render_template('work_orders/work_order_list.html', work_orders=work_orders, meta=meta)


@work_orders_bp.route('/work-orders/new', methods=['GET', 'POST'])
def new_work_order():
    """Create a new work order"""
    companies = work_order_svc.get_buyers()
    suppliers = work_order_svc.get_suppliers()

    pre_selected_buyer_id = request.args.get('buyer_id', type=int)
    work_order = {'company_id': pre_selected_buyer_id} if pre_selected_buyer_id else {}

    if request.method == 'POST':
        try:
            work_order_id = work_order_svc.create(request.form, request.files)
            flash(_('Work order created successfully!'), 'success')
            return redirect(url_for('work_orders.work_order_detail', work_order_id=work_order_id))
        except ValidationError as e:
            flash(_(str(e)), 'error')
            return render_template('work_orders/work_order_form.html', action='add',
                                   work_order={}, companies=companies, suppliers=suppliers)

    return render_template('work_orders/work_order_form.html', action='add',
                           work_order=work_order, companies=companies, suppliers=suppliers)


@work_orders_bp.route('/work-orders/<work_order_id>')
def work_order_detail(work_order_id):
    """View job specs, parts, and costs"""
    work_order = work_order_svc.get(work_order_id)
    if not work_order:
        flash(_('Work order not found!'), 'error')
        return redirect(url_for('work_orders.work_order_list'))
    return render_template('work_orders/work_order_detail.html', work_order=work_order)


@work_orders_bp.route('/work-orders/<work_order_id>/edit', methods=['GET', 'POST'])
def edit_work_order(work_order_id):
    """Modify production job details"""
    work_order = work_order_svc.get(work_order_id)
    if not work_order:
        flash(_('Work order not found!'), 'error')
        return redirect(url_for('work_orders.work_order_list'))

    companies = work_order_svc.get_buyers()
    suppliers = work_order_svc.get_suppliers()

    if request.method == 'POST':
        try:
            work_order_svc.update(work_order_id, request.form, request.files)
            flash(_('Work order updated successfully!'), 'success')
            return redirect(url_for('work_orders.work_order_detail', work_order_id=work_order_id))
        except ValidationError as e:
            flash(_(str(e)), 'error')

    return render_template('work_orders/work_order_form.html', action='edit',
                           work_order=work_order, companies=companies, suppliers=suppliers)


@work_orders_bp.route('/work-orders/<work_order_id>/delete', methods=['POST'])
def delete_work_order(work_order_id):
    """Remove production job record"""
    password = request.form.get('delete_password', '')
    try:
        if work_order_svc.delete(work_order_id, password):
            flash(_('Work order deleted successfully!'), 'success')
        else:
            flash(_('Error deleting work order!'), 'error')
    except ValidationError as e:
        flash(_(str(e)), 'error')
    return redirect(url_for('work_orders.work_order_list'))
