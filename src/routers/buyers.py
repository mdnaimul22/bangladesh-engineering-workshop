"""Buyer routes — thin HTTP wrapper over buyer service."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_babel import _
import src.services.buyer_svc as buyer_svc
from src.helpers.exceptions import ValidationError
from src.config import setup_logger, Settings

logger = setup_logger(Settings.LOG_DIR / "routers.log", name="bew.routers.buyers")

buyers_bp = Blueprint('buyers', __name__)


@buyers_bp.route('/buyers')
def buyer_list():
    """List all buyers with search functionality"""
    query = request.args.get('q', '').strip()
    buyers = buyer_svc.list_all(query)
    return render_template('buyer/buyer_list.html', buyers=buyers, search_query=query)


@buyers_bp.route('/buyers/new', methods=['GET', 'POST'])
def new_buyer():
    """Add new buyer"""
    if request.method == 'POST':
        try:
            buyer_id = buyer_svc.create(request.form)
            flash(_('Buyer added successfully!'), 'success')
            return redirect(url_for('buyers.buyer_list'))
        except ValidationError as e:
            flash(_(str(e)), 'error')
            return render_template('buyer/buyer_form.html', buyer=request.form, action='add')

    return render_template('buyer/buyer_form.html', buyer={}, action='add')


@buyers_bp.route('/buyers/<int:buyer_id>')
def buyer_detail(buyer_id):
    """View buyer profile dashboard"""
    try:
        buyer = buyer_svc.get_profile(buyer_id)
    except Exception:
        flash(_('Buyer not found!'), 'error')
        return redirect(url_for('buyers.buyer_list'))
    return render_template('buyer/buyer_detail.html', buyer=buyer)


@buyers_bp.route('/buyers/<int:buyer_id>/edit', methods=['GET', 'POST'])
def edit_buyer(buyer_id):
    """Edit existing buyer"""
    try:
        buyer = buyer_svc.get(buyer_id)
    except Exception:
        flash(_('Buyer not found!'), 'error')
        return redirect(url_for('buyers.buyer_list'))

    if request.method == 'POST':
        try:
            buyer_svc.update(buyer_id, request.form)
            flash(_('Buyer updated successfully!'), 'success')
        except ValidationError as e:
            flash(_(str(e)), 'error')
            return render_template('buyer/buyer_form.html', buyer=request.form, action='edit', buyer_id=buyer_id), 422

        return redirect(url_for('buyers.buyer_list'))

    return render_template('buyer/buyer_form.html', buyer=buyer, action='edit', buyer_id=buyer_id)


@buyers_bp.route('/buyers/<int:buyer_id>/delete', methods=['POST'])
def delete_buyer(buyer_id):
    """Delete buyer with safety check"""
    password = request.form.get('delete_password', '')
    try:
        success, reason = buyer_svc.delete(buyer_id, password)

        if success:
            flash(_('Buyer deleted successfully!'), 'success')
        elif reason in ('has_sales', 'has_work_orders'):
            flash(_('Cannot delete buyer with existing orders. Delete orders first.'), 'error')
        elif reason == 'not_found':
            flash(_('Buyer not found!'), 'error')
        else:
            flash(_('Error deleting buyer!'), 'error')
    except ValidationError as e:
        flash(_(str(e)), 'error')
        return redirect(url_for('buyers.buyer_detail', buyer_id=buyer_id))

    return redirect(url_for('buyers.buyer_list'))
