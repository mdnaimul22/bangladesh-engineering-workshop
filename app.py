import os
import sys
import uuid
import config
import datetime
from sqlalchemy import or_
from flask_babel import Babel, _
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_from_directory, jsonify

basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.append(basedir)

python_dir = os.path.join(basedir, 'python')
if python_dir not in sys.path:
    sys.path.append(python_dir)

from database import db, Shop, Category, Tag, ShopTag

from python.app.sales import sales_bp
from python.app.shops import shops_bp
from python.app.buyers import buyers_bp
from python.app.purchases import purchases_bp
from python.app.inventory import inventory_bp
from python.app.work_orders import work_orders_bp
from python.app.utils import allowed_file, expand_designation, parse_contact_info

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shop_img')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-please-change'
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER if hasattr(config, 'UPLOAD_FOLDER') else UPLOAD_FOLDER
app.config['SALES_VOUCHER_FOLDER'] = config.SALES_VOUCHER_FOLDER
app.config['PURCHASE_VOUCHER_FOLDER'] = config.PURCHASE_VOUCHER_FOLDER
app.config['WORK_ORDER_FOLDER'] = config.WORK_ORDER_FOLDER
app.config['GALLERY_FOLDER'] = config.GALLERY_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SALES_VOUCHER_FOLDER'], exist_ok=True)
os.makedirs(app.config['PURCHASE_VOUCHER_FOLDER'], exist_ok=True)
os.makedirs(app.config['WORK_ORDER_FOLDER'], exist_ok=True)
os.makedirs(app.config['GALLERY_FOLDER'], exist_ok=True)
VISITING_CARD_FOLDER = os.path.join(app.config['UPLOAD_FOLDER'], 'visiting_card')
os.makedirs(VISITING_CARD_FOLDER, exist_ok=True)

app.config['BABEL_DEFAULT_LOCALE'] = 'bn'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

def get_locale():
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(['bn', 'en'])

babel = Babel(app, locale_selector=get_locale)

db.init_app(app)
app.register_blueprint(buyers_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(shops_bp)
app.register_blueprint(work_orders_bp)
app.register_blueprint(purchases_bp)
app.register_blueprint(sales_bp)

with app.app_context():
    db.create_all()
    from sqlalchemy import text
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT visiting_card FROM shops LIMIT 1"))
    except Exception:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE shops ADD COLUMN visiting_card VARCHAR(5000)"))
            conn.commit()
            print("Migration: Added 'visiting_card' column to shops table.")

    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT hard_copy_path FROM work_orders LIMIT 1"))
    except Exception:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE work_orders ADD COLUMN hard_copy_path VARCHAR(5000)"))
            conn.commit()
            print("Migration: Added 'hard_copy_path' column to work_orders table.")

@app.context_processor
def inject_categories():
    """categories available to all templates"""
    return dict(categories=db.get_all_categories())

app.add_template_filter(parse_contact_info)

app.add_template_filter(expand_designation)

@app.route('/shop_img/<path:filename>')
def shop_img(filename):
    """Serve visiting card images from shop_img folder"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/set_lang/<lang_code>')
def set_language(lang_code):
    if lang_code in ['en', 'bn']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    """Home page with search - Redirects to shops blueprint"""
    return redirect(url_for('shops.index', **request.args))

@app.route('/about-us')
def about():
    """About Us page"""
    return render_template('about.html')

@app.route('/our-services')
def services():
    """Services page"""
    return render_template('service/services.html')

@app.route('/services/<service_alias>')
def service_detail(service_alias):
    """Dynamic Service Detail Page"""
    try:
        return render_template(f'service_page/{service_alias}.html')
    except Exception:
        return redirect(url_for('services'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5020)
