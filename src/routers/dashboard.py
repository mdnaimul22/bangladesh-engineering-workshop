from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.db.database import db
from src.helpers.auth_middleware import admin_required

dashboard_bp = Blueprint('dashboard_home', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@admin_required
def index():
    stats = db.get_visit_stats()
    # Add other stats like total buyers, shops, work orders etc.
    stats['total_buyers'] = len(db.get_all_buyers())
    stats['total_shops'] = db.get_shops_count()
    stats['total_sales'] = db.get_sales_count()
    
    return render_template('dashboard/index.html', stats=stats)

@dashboard_bp.route('/messages')
@admin_required
def messages():
    msgs = db.get_all_messages()
    return render_template('dashboard/messages/list.html', messages=msgs)

@dashboard_bp.route('/messages/<int:msg_id>/read', methods=['POST'])
@admin_required
def mark_read(msg_id):
    db.mark_message_read(msg_id)
    flash("Message marked as read.", "success")
    return redirect(url_for('dashboard_home.messages'))
