from functools import wraps
from flask import session, redirect, url_for, flash
from flask_babel import _

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash(_('Please log in to access the dashboard.'), 'warning')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function
