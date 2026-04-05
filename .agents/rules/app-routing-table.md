---
trigger: always_on
---

## APP Routing Table

| URL Pattern | Endpoint (app.py) | Template Location | Description |
| :--- | :--- | :--- | :--- |
| URL Pattern | Endpoint (app.py) | Template Location | Description |
| :--- | :--- | :--- | :--- |
| `/` | `shops.index` | `index.html` | Home page with search |
| `/shops` | `shops.shop_list` | `shop/shop_list.html` | Browse all shops |
| `/shops/new` | `shops.new_shop` | `shop/shop_form.html` | Add a new shop |
| `/shops/<id>` | `shops.shop_detail` | `shop/shop_detail.html` | Detailed shop information |
| `/shops/<id>/edit` | `shops.edit_shop` | `shop/shop_form.html` | Modify shop details |
| `/shops/<id>/purchases` | `purchases.shop_purchases` | `purchase/purchase_list.html` | Purchases from a specific shop |
| `/buyers` | `buyers.buyer_list` | `buyer/buyer_list.html` | List of all buyer companies |
| `/buyers/new` | `buyers.new_buyer` | `buyer/buyer_form.html` | Register a new client/buyer |
| `/buyers/<id>` | `buyers.buyer_detail` | `buyer/buyer_detail.html` | Client profile & transaction history |
| `/buyers/<id>/edit` | `buyers.edit_buyer` | `buyer/buyer_form.html` | Update client information |
| `/inventory` | `inventory.inventory_list` | `inventory/inventory_list.html` | Raw material stock list |
| `/inventory/new` | `inventory.new_inventory` | `inventory/inventory_form.html` | Add materials to inventory |
| `/purchases` | `purchases.purchase_list` | `purchase/purchase_list.html` | All supplier purchase records |
| `/purchases/new` | `purchases.new_purchase` | `purchase/purchase_form.html` | Log a new purchase voucher |
| `/purchases/<purchase_id>` | `purchases.purchase_detail` | `purchase/purchase_detail.html` | View purchase voucher details |
| `/work-orders` | `work_orders.work_order_list` | `work_orders/work_order_list.html` | Master list of all production jobs |
| `/work-orders/new` | `work_orders.new_work_order` | `work_orders/work_order_form.html` | Create a new work order |
| `/work-orders/<uuid>` | `work_orders.work_order_detail` | `work_orders/work_order_detail.html` | Job specs, parts, and costs |
| `/sales` | `sales.sale_list` | `sales/sale_list.html` | Record of all material/product sales |
| `/sales/new` | `sales.new_sale` | `sales/sale_form.html` | Create a new sales entry |
| `/sales/<id>` | `sales.sale_detail` | `sales/sale_detail.html` | Invoice/Sale detailed view |

## 🛠️ Utilities & Support

| URL Pattern | Endpoint (app.py) | Purpose |
| :--- | :--- | :--- |
| `/category/<id>` | `shops.category_shops` | Filters shops by category |
| `/about-us` | `about` | Workshop introduction |
| `/set_lang/<lang>` | `set_language` | Switches between Bengali/English |
| `/shop_img/<file>` | `shop_img` | Serves uploaded images/vouchers |
| `/` (Search Logic) | `shops.index` | Handles global keywords/semantic search |

## File Structure
Read Rules project_structure.md