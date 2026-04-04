from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from database import db, Shop, Category, Tag, ShopTag
from flask_babel import _
import os
import datetime
from python.app.utils import allowed_file

shops_bp = Blueprint('shops', __name__)

@shops_bp.route('/')
def index():
    """Home page with search"""
    query = request.args.get('q', '')
    categories = db.get_all_categories()
    
    if query:
        shops = db.search_shops(query)
    else:
        shops = db.get_all_shops(limit=20)
    
    total_shops = db.get_shops_count()
    
    return render_template('index.html', 
                         shops=shops, 
                         categories=categories,
                         query=query,
                         total_shops=total_shops)

@shops_bp.route('/shops')
def shop_list():
    """List all shops with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    shops = db.get_all_shops(limit=per_page, offset=offset)
    total = db.get_shops_count()
    total_pages = (total + per_page - 1) // per_page
    
    categories = db.get_all_categories()
    
    return render_template('shop/shop_list.html',
                         shops=shops,
                         categories=categories,
                         page=page,
                         total_pages=total_pages,
                         total=total)

@shops_bp.route('/category/<int:category_id>')
def category_shops(category_id):
    """List shops in a category"""
    shops = db.get_shops_by_category(category_id)
    categories = db.get_all_categories()
    current_category = next((c for c in categories if c['id'] == category_id), None)
    
    return render_template('shop/shop_list.html',
                         shops=shops,
                         categories=categories,
                         current_category=current_category,
                         page=1,
                         total_pages=1,
                         total=len(shops))

@shops_bp.route('/shops/<int:shop_id>')
def shop_detail(shop_id):
    """View single shop details"""
    shop = db.get_shop_by_id(shop_id)
    if not shop:
        flash(_('দোকান খুঁজে পাওয়া যায়নি!'), 'error')
        return redirect(url_for('shops.index'))
    
    return render_template('shop/shop_detail.html', shop=shop)

@shops_bp.route('/shops/new', methods=['GET', 'POST'])
def new_shop():
    """Add new shop"""
    categories = db.get_all_categories()
    
    if request.method == 'POST':
        # Handle file upload
        visiting_card_filename = None
        if 'visiting_card' in request.files:
            file = request.files['visiting_card']
            if file and file.filename and allowed_file(file.filename):
                filename = os.path.basename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                visiting_card_folder = os.path.join(upload_folder, 'visiting_card')
                os.makedirs(visiting_card_folder, exist_ok=True)
                file.save(os.path.join(visiting_card_folder, filename))
                visiting_card_filename = f"visiting_card/{filename}"

        category_id = request.form.get('category_id')
        new_category_name = request.form.get('new_category_name', '').strip()
        
        if category_id == 'new' and new_category_name:
            category_id = db.add_category(new_category_name)
        else:
            try:
                category_id = int(category_id) if category_id else None
            except ValueError:
                category_id = None
        
        shop_data = {
            'category_id': category_id,
            'serial_no': request.form.get('serial_no', ''),
            'name': request.form.get('name', ''),
            'proprietor': request.form.get('proprietor', ''),
            'address': request.form.get('address', ''),
            'mobile': request.form.get('mobile', ''),
            'transaction_status': request.form.get('transaction_status', ''),
            'whatsapp': request.form.get('whatsapp', ''),
            'email_web': request.form.get('email_web', ''),
            'products': request.form.get('products', ''),
            'visiting_card': visiting_card_filename
        }
        
        if not shop_data['name']:
            flash(_('প্রতিষ্ঠানের নাম আবশ্যক!'), 'error')
            return render_template('shop/shop_form.html', categories=categories, shop=shop_data, action='add')
        
        shop_id = db.add_shop(shop_data)
        
        tags_input = request.form.get('tags', '')
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag_id = db.add_tag(tag_name)
                db.add_shop_tag(shop_id, tag_id)
                
        flash(_('দোকান সফলভাবে যোগ করা হয়েছে!'), 'success')
        return redirect(url_for('shops.shop_detail', shop_id=shop_id))
    
    return render_template('shop/shop_form.html', categories=categories, shop={}, action='add')

@shops_bp.route('/shops/<int:shop_id>/edit', methods=['GET', 'POST'])
def edit_shop(shop_id):
    """Edit existing shop"""
    shop = db.get_shop_by_id(shop_id)
    if not shop:
        flash(_('দোকান খুঁজে পাওয়া যায়নি!'), 'error')
        return redirect(url_for('shops.index'))
    
    categories = db.get_all_categories()
    
    if request.method == 'POST':
        visiting_card_filename = None
        if 'visiting_card' in request.files:
            file = request.files['visiting_card']
            if file and file.filename and allowed_file(file.filename):
                filename = os.path.basename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                visiting_card_folder = os.path.join(upload_folder, 'visiting_card')
                os.makedirs(visiting_card_folder, exist_ok=True)
                file.save(os.path.join(visiting_card_folder, filename))
                visiting_card_filename = f"visiting_card/{filename}"

        category_id = request.form.get('category_id')
        new_category_name = request.form.get('new_category_name', '').strip()
        
        if category_id == 'new' and new_category_name:
            category_id = db.add_category(new_category_name)
        else:
            try:
                category_id = int(category_id) if category_id else None
            except ValueError:
                category_id = None
                
        shop_data = {
            'category_id': category_id,
            'serial_no': request.form.get('serial_no', ''),
            'name': request.form.get('name', ''),
            'proprietor': request.form.get('proprietor', ''),
            'address': request.form.get('address', ''),
            'mobile': request.form.get('mobile', ''),
            'transaction_status': request.form.get('transaction_status', ''),
            'whatsapp': request.form.get('whatsapp', ''),
            'email_web': request.form.get('email_web', ''),
            'products': request.form.get('products', '')
        }

        if visiting_card_filename:
            shop_data['visiting_card'] = visiting_card_filename
        
        if not shop_data['name']:
            flash(_('প্রতিষ্ঠানের নাম আবশ্যক!'), 'error')
            return render_template('shop/shop_form.html', categories=categories, shop=shop_data, action='edit', shop_id=shop_id)
        
        db.update_shop(shop_id, shop_data)
        
        tags_input = request.form.get('tags', '')
        if tags_input:
            existing_tags = db.get_shop_tags(shop_id)
            for t in existing_tags:
                db.remove_shop_tag(shop_id, t['id'])
            
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag_id = db.add_tag(tag_name)
                db.add_shop_tag(shop_id, tag_id)
        
        flash(_('দোকানের তথ্য সফলভাবে আপডেট করা হয়েছে!'), 'success')
        return redirect(url_for('shops.shop_detail', shop_id=shop_id))
    
    return render_template('shop/shop_form.html', categories=categories, shop=shop, action='edit', shop_id=shop_id)

@shops_bp.route('/shops/<int:shop_id>/delete', methods=['POST'])
def delete_shop(shop_id):
    """Delete a shop with password protection"""
    DELETE_PASSWORD = "admin123"
    
    submitted_password = request.form.get('delete_password', '')
    if submitted_password != DELETE_PASSWORD:
        flash(_('পাসওয়ার্ড ভুল! ডিলিট করা যায়নি।'), 'error')
        return redirect(url_for('shops.shop_detail', shop_id=shop_id))
    
    if db.delete_shop(shop_id):
        flash(_('দোকান সফলভাবে মুছে ফেলা হয়েছে!'), 'success')
    else:
        flash(_('দোকান মুছে ফেলতে সমস্যা হয়েছে!'), 'error')
    
    return redirect(url_for('shops.index'))

@shops_bp.route('/api/search')
def api_search():
    """API endpoint for search"""
    query = request.args.get('q', '')
    shops = db.search_shops(query) if query else []
    return jsonify(shops)

@shops_bp.route('/api/shops')
def api_shops():
    """API endpoint for all shops"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    shops = db.get_all_shops(limit=per_page, offset=offset)
    total = db.get_shops_count()
    
    return jsonify({
        'shops': shops,
        'total': total,
        'page': page,
        'per_page': per_page
    })

# ==================== TAG API ROUTES ====================

@shops_bp.route('/api/tags')
def api_tags():
    """API endpoint for all tags"""
    tags = db.get_all_tags()
    return jsonify({'tags': tags})

@shops_bp.route('/api/tag/add', methods=['POST'])
def api_add_tag():
    """API endpoint to add a new tag"""
    data = request.get_json() or request.form
    name = data.get('name', '').strip()
    name_bn = data.get('name_bn', '').strip()
    
    if not name:
        return jsonify({'error': 'Tag name is required'}), 400
    
    tag_id = db.add_tag(name, name_bn)
    return jsonify({'id': tag_id, 'name': name, 'name_bn': name_bn})

@shops_bp.route('/api/tag/delete/<int:tag_id>', methods=['POST', 'DELETE'])
def api_delete_tag(tag_id):
    """API endpoint to delete a tag"""
    if db.delete_tag(tag_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Tag not found'}), 404

@shops_bp.route('/api/shop/<int:shop_id>/tags')
def api_shop_tags(shop_id):
    """API endpoint to get tags for a shop"""
    tags = db.get_shop_tags(shop_id)
    return jsonify({'shop_id': shop_id, 'tags': tags})

@shops_bp.route('/api/shop/<int:shop_id>/tag/add', methods=['POST'])
def api_add_shop_tag(shop_id):
    """API endpoint to add a tag to a shop"""
    data = request.get_json() or request.form
    tag_id = data.get('tag_id')
    
    if not tag_id:
        return jsonify({'error': 'tag_id is required'}), 400
    
    try:
        shop_tag_id = db.add_shop_tag(shop_id, int(tag_id))
        return jsonify({'success': True, 'shop_tag_id': shop_tag_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@shops_bp.route('/api/shop/<int:shop_id>/tag/remove', methods=['POST', 'DELETE'])
def api_remove_shop_tag(shop_id):
    """API endpoint to remove a tag from a shop"""
    data = request.get_json() or request.form
    tag_id = data.get('tag_id')
    
    if not tag_id:
        return jsonify({'error': 'tag_id is required'}), 400
    
    if db.remove_shop_tag(shop_id, int(tag_id)):
        return jsonify({'success': True})
    return jsonify({'error': 'Tag not found on shop'}), 404

@shops_bp.route('/search/tag/<tag_name>')
def search_by_tag(tag_name):
    """Search shops by tag"""
    shops = db.search_shops_by_tag(tag_name)
    return render_template('shop/shop_list.html',
                         shops=shops,
                         categories=db.get_all_categories(),
                         current_tag=tag_name,
                         page=1,
                         total_pages=1,
                         total=len(shops))
