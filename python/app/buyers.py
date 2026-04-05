from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db, Buyer, BuyerContact, WorkOrder
from flask_babel import _
import json
import datetime

buyers_bp = Blueprint('buyers', __name__)

@buyers_bp.route('/buyers')
def buyer_list():
    """List all buyers with search functionality"""
    query = request.args.get('q', '').strip()
    
    if query:
        from sqlalchemy import or_
        # Search by company name OR contact name
        buyers_query = Buyer.query.filter(
            or_(
                Buyer.company_name.ilike(f'%{query}%'),
                Buyer.contacts.any(BuyerContact.name.ilike(f'%{query}%'))
            )
        ).order_by(Buyer.company_name).all()
        
        if buyers_query:
            buyers = [b.to_dict() for b in buyers_query]
        else:
            # Fallback to all buyers if no matches found
            buyers = db.get_all_buyers()
    else:
        buyers = db.get_all_buyers()
        
    return render_template('buyer/buyer_list.html', buyers=buyers, search_query=query)

@buyers_bp.route('/buyers/new', methods=['GET', 'POST'])
def new_buyer():
    """Add new buyer"""
    if request.method == 'POST':
        buyer_data = {
            'company_name': request.form.get('company_name'),
            'address': request.form.get('address'),
            'contacts': []
        }
        
        # Parse dynamic contacts
        names = request.form.getlist('contact_name')
        designations = request.form.getlist('contact_designation')
        whatsapps = request.form.getlist('contact_whatsapp')
        emails = request.form.getlist('contact_email')
        
        for i in range(len(names)):
            if names[i].strip():
                # Get mobiles for this specific contact
                mobiles = request.form.getlist(f'contact_mobiles_{i}[]')
                # Filter out empty mobiles
                mobiles = [m.strip() for m in mobiles if m.strip()]
                
                primary_index = request.form.get('primary_contact_index')
                
                buyer_data['contacts'].append({
                    'name': names[i].strip(),
                    'designation': designations[i].strip() if i < len(designations) else '',
                    'mobiles': mobiles,
                    'whatsapp': whatsapps[i].strip() if i < len(whatsapps) else '',
                    'email': emails[i].strip() if i < len(emails) else '',
                    'is_primary': str(i) == primary_index
                })
        
        if not buyer_data['company_name']:
            flash(_('Company name is required!'), 'error')
            return render_template('buyer/buyer_form.html', buyer=buyer_data, action='add')
            
        buyer_id = db.add_buyer(buyer_data)
        flash(_('Buyer added successfully!'), 'success')
        return redirect(url_for('buyers.buyer_list'))
        
    return render_template('buyer/buyer_form.html', buyer={}, action='add')

@buyers_bp.route('/buyers/<int:buyer_id>')
def buyer_detail(buyer_id):
    """View buyer profile dashboard"""
    buyer = db.get_buyer_profile(buyer_id)
    if not buyer:
        flash(_('Buyer not found!'), 'error')
        return redirect(url_for('buyers.buyer_list'))
    return render_template('buyer/buyer_detail.html', buyer=buyer)

@buyers_bp.route('/buyers/<int:buyer_id>/edit', methods=['GET', 'POST'])
def edit_buyer(buyer_id):
    """Edit existing buyer"""
    buyer = db.get_buyer_by_id(buyer_id)
    if not buyer:
        flash(_('Buyer not found!'), 'error')
        return redirect(url_for('buyers.buyer_list'))
        
    if request.method == 'POST':
        buyer_data = {
            'company_name': request.form.get('company_name'),
            'address': request.form.get('address'),
            'contacts': []
        }
        
        # Parse dynamic contacts
        names = request.form.getlist('contact_name')
        designations = request.form.getlist('contact_designation')
        whatsapps = request.form.getlist('contact_whatsapp')
        emails = request.form.getlist('contact_email')
        
        for i in range(len(names)):
            if names[i].strip():
                # Get mobiles for this specific contact
                mobiles = request.form.getlist(f'contact_mobiles_{i}[]')
                mobiles = [m.strip() for m in mobiles if m.strip()]
                
                primary_index = request.form.get('primary_contact_index')
                
                buyer_data['contacts'].append({
                    'name': names[i].strip(),
                    'designation': designations[i].strip() if i < len(designations) else '',
                    'mobiles': mobiles,
                    'whatsapp': whatsapps[i].strip() if i < len(whatsapps) else '',
                    'email': emails[i].strip() if i < len(emails) else '',
                    'is_primary': str(i) == primary_index
                })
                
        if not buyer_data['company_name']:
            flash(_('Company name is required!'), 'error')
            return render_template('buyer/buyer_form.html', buyer=buyer_data, action='edit', buyer_id=buyer_id)
            
        if db.update_buyer(buyer_id, buyer_data):
            flash(_('Buyer updated successfully!'), 'success')
        else:
            flash(_('Error updating buyer.'), 'error')
        return redirect(url_for('buyers.buyer_list'))
        
    return render_template('buyer/buyer_form.html', buyer=buyer, action='edit', buyer_id=buyer_id)

@buyers_bp.route('/buyers/<int:buyer_id>/delete', methods=['POST'])
def delete_buyer(buyer_id):
    """Delete buyer with safety check and translation-friendly messages"""
    success, reason = db.delete_buyer(buyer_id)
    if success:
        flash(_('Buyer deleted successfully!'), 'success')
    else:
        if reason == 'has_sales' or reason == 'has_work_orders':
            flash(_('এই বায়ারের সেল ওর্ডার আছে। আপনি সেল ওর্ডার ডিলিট না করে বায়ার ডিলিট করতে পারবেন না।'), 'error')
        elif reason == 'not_found':
            flash(_('Buyer not found!'), 'error')
        else:
            flash(_('Error deleting buyer!'), 'error')
    return redirect(url_for('buyers.buyer_list'))
