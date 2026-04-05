import os
import json

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_contact_info(value):
    """Detect if contact info is email, website, or text"""
    if not value:
        return {'type': 'text', 'value': '-'}
    
    value_lower = value.lower()
    
    # Check for email
    if '@' in value and any(x in value_lower for x in ['gmail', 'yahoo', 'hotmail', 'mail']):
        return {'type': 'email', 'value': value}
    
    # Check for website
    if '.com' in value_lower or 'http' in value_lower or 'www.' in value_lower:
        return {'type': 'web', 'value': value}
        
    return {'type': 'text', 'value': value}

def expand_designation(value):
    if not value:
        return ""
        
    # mapping of abbreviations to full titles
    mappings = {
        'pm': 'Production Manager',
        'p.m': 'Production Manager',
        'p.m.': 'Production Manager',
        
        'md': 'Managing Director',
        'm.d': 'Managing Director',
        'm.d.': 'Managing Director',
        
        'dgm': 'Deputy General Manager',
        'd.g.m': 'Deputy General Manager',
        'd.g.m.': 'Deputy General Manager',
        
        'gm': 'General Manager',
        'g.m': 'General Manager',
        'g.m.': 'General Manager',
        
        'ceo': 'Chief Executive Officer',
        'c.e.o': 'Chief Executive Officer',
        'c.e.o.': 'Chief Executive Officer',
        
        'cfo': 'Chief Financial Officer',
        'c.f.o': 'Chief Financial Officer',
        'c.f.o.': 'Chief Financial Officer',
        
        'coo': 'Chief Operating Officer',
        'c.o.o': 'Chief Operating Officer',
        'c.o.o.': 'Chief Operating Officer',
        
        'hr': 'Human Resources',
        'h.r': 'Human Resources',
        'h.r.': 'Human Resources',
        
        'agm': 'Assistant General Manager',
        'a.g.m': 'Assistant General Manager',
        'a.g.m.': 'Assistant General Manager',
        
        'mgr': 'Manager',
        'asst': 'Assistant',
        'sr': 'Senior',
        'jr': 'Junior',
        'exec': 'Executive',
        'dir': 'Director',
        'vp': 'Vice President',
        'v.p': 'Vice President',
        'v.p.': 'Vice President'
    }
    
    lower_val = value.lower().strip()
    if lower_val in mappings:
        return mappings[lower_val]
        
    return value
