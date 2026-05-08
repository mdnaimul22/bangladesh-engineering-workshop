"""Core routes — static pages (About, Services)."""
from flask import Blueprint, render_template, redirect, url_for

core_bp = Blueprint('core', __name__)


@core_bp.route('/about-us')
@core_bp.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')


@core_bp.route('/our-services')
def services():
    """Services page"""
    return render_template('service/services.html')


@core_bp.route('/services/<service_alias>')
def service_detail(service_alias):
    """Dynamic Service Detail Page"""
    try:
        return render_template(f'service_page/{service_alias}.html')
    except Exception:
        return redirect(url_for('core.services'))
