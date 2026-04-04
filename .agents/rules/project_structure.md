---
trigger: always_on
---

# Project Structure

**Root:** `/home/ubuntu/bd_business_dir`

```
bd_business_dir/
├── python/
│   ├── app/
│   │   ├── /python/app/__init__.py
│   │   ├── /python/app/buyers.py  # database
│   │   ├── /python/app/core.py
│   │   ├── /python/app/inventory.py  # database
│   │   ├── /python/app/purchases.py  # database, python.app.utils
│   │   ├── /python/app/sales.py  # database, python.app.utils
│   │   ├── /python/app/shops.py  # database, python.app.utils
│   │   ├── /python/app/utils.py
│   │   └── /python/app/work_orders.py  # database, python.app.utils
│   ├── classifire/
│   │   ├── /python/classifire/shop_ids.pkl
│   │   ├── /python/classifire/tfidf_matrix.pkl
│   │   └── /python/classifire/tfidf_vectorizer.pkl
│   ├── /python/search_engine.py
│   ├── /python/semantic_search.py  # config, search_engine
│   ├── /python/train.py  # config, semantic_search
│   └── /python/word_frequency.py  # search_engine
├── shop_img/
│   ├── gallery/
│   ├── purchase_voucher/
│   ├── sales_voucher/
│   ├── visiting_card/
│   └── work_orders/
├── static/                      # Static assets (CSS, JS, Images)
│   ├── css/                     # Stylesheets (Standardized & Modular)
│   │   ├── variables.css        # Design tokens (colors, spacing)
│   │   ├── base.css             # CSS resets and basic element styles
│   │   ├── layout.css           # Main structure (Navbar, Grid, Containers)
│   │   ├── header.css           # Header & Navigation specific styles
│   │   ├── footer.css           # Footer & Social links styles
│   │   ├── buttons.css          # Interactive element styling
│   │   ├── shop_list.css        # Directory-specific view styles
│   │   ├── shop_detail.css      # Shop profile specific styles
│   │   └── extra.css            # Utility and helper classes
│   ├── img/                     # Image Assets (Icons, Hero images, placeholders)
│   ├── uploads/                 # Dynamic uploads (Vouchers, visiting cards)
│   └── script.js                # Core UI interactions & Dynamic DOM logic
│
├── templates/                   # Jinja2 HTML Templates
│   ├── base.html                # Master layout (Navbar & Sidebar included)
│   ├── index.html               # Homepage / Global Search
│   ├── about.html               # Workshop Profile page
│   ├── buyer/                   # CLIENT MANAGEMENT
│   │   ├── buyer_list.html      # Company directory
│   │   ├── buyer_detail.html    # Profile & transaction history
│   │   └── buyer_form.html      # Registration & Edit form
│   ├── shop/                    # SUPPLIER MANAGEMENT
│   │   ├── shop_list.html       # Browse all shops/vendors
│   │   ├── shop_detail.html     # Vendor profile & stock link
│   │   └── shop_form.html       # Vendor registration & Edit
│   ├── inventory/               # RAW MATERIAL LOGS
│   │   ├── inventory_list.html  # Current stock levels
│   │   └── inventory_form.html  # Material entry form
│   ├── purchase/                # SUPPLIER VOUCHERS
│   │   ├── purchase_list.html   # Purchase history
│   │   ├── purchase_detail.html # Voucher details & items
│   │   └── purchase_form.html   # New purchase entry
│   ├── work_orders/             # PRODUCTION JOBS
│   │   ├── work_order_list.html # Active & completed jobs
│   │   ├── work_order_detail.html# Job specs & material cost
│   │   └── work_order_form.html # Order creation & editing
│   ├── sales/                   # CUSTOMER INVOICES
│   │   ├── sale_list.html       # Sales history
│   │   ├── sale_detail.html     # Invoice detail view
│   │   └── sale_form.html       # New sale recording
│   ├── service/                 # WORKSHOP SERVICES
│   │   ├── services.html        # General workshop services list
│   │   └── service_detail.html  # Specific service overview
│   └── service_page/            # SEO LANDING PAGES- These are static, highly detailed pages designed for SEO and client education about specific workshop capabilities (e.g., Lathe Work, Crane Repair).
│       ├── heavy_engineering.html
│       ├── metal_components.html
│       ├── earthmoving-repair.html
│       └── ... (and other specific service pages)
├── translations/
│   ├── bn/
│   │   └── LC_MESSAGES/
│   │       ├── /translations/bn/LC_MESSAGES/messages.mo
│   │       └── /translations/bn/LC_MESSAGES/messages.po
│   └── en/
│       └── LC_MESSAGES/
│           ├── /translations/en/LC_MESSAGES/messages.mo
│           └── /translations/en/LC_MESSAGES/messages.po
├── /app.py  # config, database, python.app.buyers, python.app.inventory, python.app.purchases, python.app.sales +3 more
├── /babel.cfg
├── /config.py
├── /database.py  # app, search_engine, semantic_search
├── /messages.pot
├── /odt_parser.py
├── /shop_details.db
├── /shops_data.json
└── /tree.py
```
