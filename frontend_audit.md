# Frontend Audit: Bangladesh Engineering Workshop

## 📊 Current State — The Chaos Map

### CSS Files (18 files, 3,231 lines total)

| Layer | File | Lines | Loaded By |
|:---|:---|---:|:---|
| **Global (base.html)** | `style.css` (master importer) | 27 | Every page |
| ↳ | `variables.css` (design tokens) | 203 | `@import` chain |
| ↳ | `base.css` (resets) | 54 | `@import` chain |
| ↳ | `header.css` (nav) | 197 | `@import` chain |
| ↳ | `layout.css` (hero, search, sidebar) | 376 | `@import` chain |
| ↳ | `shop_list.css` | 230 | `@import` chain |
| ↳ | `shop_form.css` | 128 | `@import` chain |
| ↳ | `shop_detail.css` | 156 | `@import` chain |
| ↳ | `footer.css` | 245 | `@import` chain |
| ↳ | `responsive-table.css` | 96 | `@import` chain |
| ↳ | `extra.css` (utility leftovers) | 96 | `@import` chain |
| **Also Global** | `buttons.css` | 144 | `<link>` in base.html |
| **Per-Page** | `css/buyer/buyer_detail.css` | 329 | `<link>` in template |
| | `css/buyer/buyer_form.css` | 92 | `<link>` in template |
| | `css/buyer/buyer_list.css` | 96 | `<link>` in template |
| | `css/work_order/work_order_detail.css` | 324 | `<link>` in template |
| | `css/work_order/work_order_form.css` | 345 | `<link>` in template |
| | `css/work_order/work_order_list.css` | 94 | `<link>` in template |

### Inline `style=""` Attributes (500+ total)

| Template | Count | Severity |
|:---|---:|:---:|
| `work_orders/work_order_detail.html` | **80** | 🔴 Critical |
| `purchase/purchase_form.html` | **42** | 🔴 Critical |
| `about.html` | **31** | 🟡 Medium |
| `purchase/purchase_detail.html` | **29** | 🟡 Medium |
| `sales/sale_detail.html` | **26** | 🟡 Medium |
| `sales/sale_list.html` | **18** | 🟡 Medium |
| All `service_page/*.html` (×7) | **~17 each** | 🟡 Medium |
| `shop/shop_detail.html` | **17** | 🟡 Medium |
| Others | <10 each | 🟢 Low |

### Embedded `<style>` Blocks (5 templates)

| Template | Purpose |
|:---|:---|
| `shop/shop_form.html` | Tag autocomplete, gallery upload styling |
| `purchase/purchase_form.html` | Dynamic item rows styling |
| `sales/sale_form.html` | Item row styling |
| `inventory/inventory_form.html` | Autocomplete dropdown |
| `test_pdf_modal.html` | PDF preview modal |

### Inline `<script>` Blocks (679 lines total)

| Template | Lines | Purpose |
|:---|---:|:---|
| `shop/shop_form.html` | 162 | Tag CRUD, gallery upload, category toggle |
| `buyer/buyer_form.html` | 129 | Dynamic contact rows, mobile add/remove |
| `work_orders/work_order_form.html` | 128 | Dynamic parts, file upload, cost calc |
| `work_orders/work_order_detail.html` | 90 | PDF preview, print, tab switching |
| `purchase/purchase_form.html` | 55 | Dynamic purchase items |
| `sales/sale_form.html` | 37 | Inventory search, item rows |
| `shop/shop_detail.html` | 12 | Gallery lightbox |
| `inventory/inventory_form.html` | 4 | Autocomplete |

### Global JS

| File | Lines | Purpose |
|:---|---:|:---|
| `static/script.js` | 180 | Sidebar toggle, theme switch, flash auto-dismiss, search |

---

## 🔍 Root Problems Identified

1. **CSS @import waterfall** — `style.css` chains 10 `@import` calls. Each is a **blocking HTTP request** (not bundled). On slow connections, this creates visible FOUC (Flash of Unstyled Content).

2. **No CSS for purchases, sales, inventory** — These templates have **zero external CSS files**. All styling is done via 500+ inline `style=""` attributes, making them unmaintainable.

3. **Inconsistent loading** — Some CSS uses `{% block extra_css %}`, some uses raw `<link>` outside the block, some uses `<style>` blocks. No single pattern.

4. **JS scattered across templates** — 679 lines of inline JS split into 8 templates. No shared utility functions. Duplicated patterns (e.g., "add row" logic appears in purchase, sale, and work order forms).

5. **No icon system** — Uses Google Material Icons CDN which is fine, but icon usage is done via raw `<span class="material-icons">` everywhere.

---

## 🎯 Migration Strategy Options

### Option A: Vanilla CSS Consolidation (Lowest Risk)
> Stay with current vanilla CSS, but consolidate everything

- **Effort:** Medium (~2-3 days)
- **Risk:** Low
- **Result:** Clean but still manual, still no utility classes

**What it does:**
- Merge all 18 CSS files into 3: `tokens.css`, `components.css`, `pages.css`
- Extract all inline `style=""` into CSS classes
- Extract all `<style>` blocks into the CSS files
- Keep `script.js` as global, extract inline JS into per-page `.js` files

### Option B: Tailwind CSS + Alpine.js (Recommended)
> Modern utility-first CSS with lightweight JS framework

- **Effort:** High (~5-7 days, phased)
- **Risk:** Medium
- **Result:** Professional, maintainable, industry-standard

**What it does:**
- Tailwind CSS v3 (CDN or build) replaces all CSS files
- Alpine.js replaces all inline `<script>` blocks
- `variables.css` design tokens → `tailwind.config.js`
- Dark mode via Tailwind's `dark:` variant (already have `[data-theme='dark']`)
- Zero custom CSS needed for 90% of layouts

**Why this is best:**
- Your templates are already "utility-heavy" — most inline styles are `margin`, `padding`, `display`, `color` — exactly what Tailwind provides
- Alpine.js handles the DOM manipulation (show/hide, dynamic rows) without React's complexity
- No build step needed (CDN mode for both)
- Your existing `variables.css` token system maps cleanly to Tailwind's `extend` config

### Option C: React CDN (You Mentioned)
> ❌ **Not Recommended**

- **Effort:** Extreme (~2-3 weeks)
- **Risk:** Very High
- **Result:** Overkill for server-rendered Jinja templates

**Problems:**
- Babel-in-browser is development-only — unusable in production
- React CDN + Jinja2 templating is an architectural conflict (two rendering engines fighting)
- D3, tree-sitter, jsrsasign, jszip from your message are **not needed** for this app
- You'd need to rewrite every template as a React component

---

## ✅ Recommended Plan: Tailwind CSS + Alpine.js (Phased)

### Phase 1: Foundation (Day 1)
- [ ] Add Tailwind CSS CDN + config to `base.html`
- [ ] Add Alpine.js CDN to `base.html`
- [ ] Keep all existing CSS as-is (backward compatible)
- [ ] Verify nothing breaks

### Phase 2: Core Layout (Day 2)
- [ ] Convert `base.html` (navbar, sidebar, footer) to Tailwind
- [ ] Remove `header.css`, `footer.css`, `layout.css`
- [ ] Convert `script.js` → Alpine.js directives (`x-data`, `x-show`, `@click`)

### Phase 3: List Pages (Day 3)
- [ ] Convert all `*_list.html` templates (shop, buyer, inventory, purchase, sale, work_order)
- [ ] Remove `shop_list.css`, `buyer_list.css`, `work_order_list.css`
- [ ] Standardize table/card layouts with Tailwind grid

### Phase 4: Form Pages (Day 4-5)
- [ ] Convert all `*_form.html` templates
- [ ] Extract inline JS into Alpine.js `x-data` components
- [ ] Remove `shop_form.css`, `buyer_form.css`, `work_order_form.css`
- [ ] Eliminate all `<style>` blocks

### Phase 5: Detail Pages (Day 6)
- [ ] Convert all `*_detail.html` templates
- [ ] Remove `shop_detail.css`, `buyer_detail.css`, `work_order_detail.css`
- [ ] Service pages (SEO landing pages) — convert inline styles to Tailwind

### Phase 6: Cleanup (Day 7)
- [ ] Delete all old CSS files
- [ ] Remove `variables.css`, `base.css`, `style.css`, `buttons.css`, `extra.css`
- [ ] Final regression test all 33 templates
- [ ] Run Lighthouse performance audit

### End State File Structure
```
static/
├── css/
│   └── custom.css       ← Only truly custom styles (if any remain)
├── js/
│   └── app.js           ← Alpine.js global stores/components (minimal)
├── img/                  ← Unchanged
└── robots.txt
```

---

> [!IMPORTANT]
> **Decision needed:** Before starting, confirm:
> 1. **Tailwind + Alpine.js** — এটাই কি যাবে? নাকি Option A (vanilla consolidation)?
> 2. **CDN mode** (no build step) নাকি **build mode** (npm, PostCSS, purge)?
> 3. Phase 1 থেকে শুরু করবো?

