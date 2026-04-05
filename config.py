import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DB_NAME = 'shop_details.db'
DB_PATH = os.path.join(BASE_DIR, DB_NAME)
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'

# Search model artifacts directory
MODELS_DIR = os.path.join(BASE_DIR, 'python', 'classifire')

# Uploads directory
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'shop_img')
SALES_VOUCHER_FOLDER = os.path.join(UPLOAD_FOLDER, 'sales_voucher')
PURCHASE_VOUCHER_FOLDER = os.path.join(UPLOAD_FOLDER, 'purchase_voucher')
WORK_ORDER_FOLDER = os.path.join(UPLOAD_FOLDER, 'work_orders')
GALLERY_FOLDER = os.path.join(UPLOAD_FOLDER, 'gallery')

# Ensure directories exist
for d in [MODELS_DIR, UPLOAD_FOLDER, SALES_VOUCHER_FOLDER, PURCHASE_VOUCHER_FOLDER, WORK_ORDER_FOLDER, GALLERY_FOLDER]:
    if not os.path.exists(d):
        os.makedirs(d)
