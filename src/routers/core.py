from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_babel import _
from src.db.database import db

core_bp = Blueprint('core', __name__)


@core_bp.route('/about-us')
@core_bp.route('/about')
def about():
    """About Us page"""
    return render_template('web/about.html')


@core_bp.route('/our-services')
def services():
    """Services page"""
    return render_template('web/service/services.html')


@core_bp.route('/services/<service_alias>')
def service_detail(service_alias):
    """Dynamic Service Detail Page"""
    try:
        return render_template(f'web/service_page/{service_alias}.html')
    except Exception:
        return redirect(url_for('core.services'))


@core_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with message form"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message')
        }
        db.add_visitor_message(data)
        flash(_('Thank you for your message! We will get back to you soon.'), 'success')
        return redirect(url_for('shops.index'))
    return render_template('web/contact.html')

