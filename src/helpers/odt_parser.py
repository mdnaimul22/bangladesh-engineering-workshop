import xml.etree.ElementTree as ET
import json
import re
import unicodedata
from zipfile import ZipFile

from src.config import setup_logger, Settings, exists, write_json, get_abs_path

logger = setup_logger(
    Settings.LOG_DIR / "helper.log",
    name="bew.helpers.odt_parser"
)

# Bengali to English number mapping
BENGALI_DIGITS = '০১২৩৪৫৬৭৮৯'

def normalize_text(text):
    if not text:
        return ""
    return unicodedata.normalize('NFC', text)

def bengali_to_english_num(text):
    for i, d in enumerate(BENGALI_DIGITS):
        text = text.replace(d, str(i))
    return text

def normalize_mobile(mobile_text):
    clean = re.sub(r'[^\d০-৯\-,\s]', '', mobile_text)
    return clean.strip()

def parse_odt(odt_rel_path: str):
    base_dir = odt_rel_path.rsplit('/', 1)[0]
    extract_dir = f"{base_dir}/extracted_odt"
    content_xml_path = f"{extract_dir}/content.xml"
    
    if not exists(content_xml_path):
        with ZipFile(get_abs_path(odt_rel_path), 'r') as zip_ref:
            zip_ref.extractall(get_abs_path(extract_dir))
    
    tree = ET.parse(content_xml_path)
    root = tree.getroot()
    
    ns = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    }
    
    categories_list = []
    
    def get_cell_text(cell):
        texts = []
        for p in cell.findall('.//text:p', ns):
            if p.text: texts.append(p.text)
            for child in p:
                if child.tail: texts.append(child.tail)
        return normalize_text(" ".join(texts).strip())

    logger.info("Scanning for categories in Index tables...")
    tables = root.findall('.//table:table', ns)
    
    for table in tables:
        rows = table.findall('.//table:table-row', ns)
        if not rows: 
            continue
            
        header_cells = rows[0].findall('.//table:table-cell', ns)
        header_text = " ".join([get_cell_text(c) for c in header_cells])
        
        if "ক্যাটেগরি" in header_text and "সিরিয়াল" in header_text:
            for row in rows[1:]:
                cells = row.findall('.//table:table-cell', ns)
                if len(cells) >= 2:
                    cat_id_text = bengali_to_english_num(get_cell_text(cells[0]))
                    cat_name = get_cell_text(cells[1])
                    
                    cat_id_match = re.search(r'\d+', cat_id_text)
                    if cat_id_match and cat_name:
                        cat_id = int(cat_id_match.group())
                        if not any(c[0] == cat_id for c in categories_list):
                            categories_list.append((cat_id, cat_name, "")) # English name empty
                            logger.debug(f"Found Category {cat_id}: {cat_name}")

    if not categories_list:
        logger.warning("No dynamic categories found. Falling back to basics or manual check needed.")
    
    categories_list.sort(key=lambda x: x[0])
    logger.info(f"Total Categories Found: {len(categories_list)}")

    categories = {}
    for serial, name_bn, name_en in categories_list:
        categories[serial] = {
            "id": serial,
            "name": normalize_text(name_bn),
            "name_english": name_en
        }
    
    shops = []
    current_category_id = None
    current_category_name = None
    
    cat_map = {c[1]: c[0] for c in categories_list} # Name -> ID
    
    for table in tables:
        rows = table.findall('.//table:table-row', ns)
        
        for row in rows:
            cells = row.findall('.//table:table-cell', ns)
            row_text = []
            full_row_text = ""
            
            for cell in cells:
                cell_text = get_cell_text(cell)
                if cell_text:
                    row_text.append(cell_text)
            
            full_row_text = " ".join(row_text)
            
            if not full_row_text.strip():
                continue

            matched_cat = False
            
            cleaned_row_text = bengali_to_english_num(full_row_text)
            
            for cat_id, cat_name, _ in categories_list:

                if len(full_row_text) < 100:
                    if cat_name in full_row_text:
                        has_mobile = re.search(r'\d{5,}', cleaned_row_text)
                        if not has_mobile:
                            current_category_id = cat_id
                            current_category_name = cat_name
                            matched_cat = True
                            break
            
            if matched_cat:
                continue

            if len(cells) >= 5:
                header_text = row_text
                
                if ('সিরিয়াল' in header_text or 'নং' in header_text) and \
                   ('প্রতিষ্ঠান' in header_text or 'মোবাইল' in header_text or 'প্রোপাইটার' in header_text):
                    continue

            if len(cells) >= 5:
                cell_texts = []
                for cell in cells:
                    t = ""
                    for p in cell.findall('.//text:p', ns):
                        if p.text: t += p.text + " "
                        for c in p:
                            if c.text: t += c.text + " "
                            if c.tail: t += c.tail + " "
                    cell_texts.append(normalize_text(t.strip()))
                
                if 'সিরিয়াল' in cell_texts[0] or 'প্রতিষ্ঠান' in cell_texts[1]:
                    continue
                    
                if len(cell_texts[1]) > 0:
                    shop = {
                        "serial_no": cell_texts[0] if len(cell_texts) > 0 else "",
                        "name": cell_texts[1] if len(cell_texts) > 1 else "",
                        "proprietor": cell_texts[2] if len(cell_texts) > 2 else "",
                        "address": cell_texts[3] if len(cell_texts) > 3 else "",
                        "mobile": normalize_mobile(cell_texts[4]) if len(cell_texts) > 4 else "",
                        "transaction_status": cell_texts[5] if len(cell_texts) > 5 else "",
                        "whatsapp": cell_texts[6] if len(cell_texts) > 6 else "",
                        "email_web": cell_texts[7] if len(cell_texts) > 7 else "",
                        "products": cell_texts[8] if len(cell_texts) > 8 else "",
                        "category_id": current_category_id,
                        "category_name": current_category_name
                    }
                    shops.append(shop)

    return {
        "categories": list(categories.values()),
        "shops": shops
    }

def main():
    odt_rel_path = "src/helpers/shop_details.odt"
    
    logger.info("Parsing ODT file...")
    data = parse_odt(odt_rel_path)
    
    logger.info(f"Found {len(data['categories'])} categories")
    logger.info(f"Found {len(data['shops'])} shops")
    
    # Check category coverage
    shops_with_cat = sum(1 for s in data['shops'] if s['category_id'])
    logger.info(f"Shops with category: {shops_with_cat} / {len(data['shops'])}")
    
    # Save to JSON
    output_rel_path = "src/helpers/shops_data.json"
    write_json(output_rel_path, data)
    
    logger.info(f"Data saved to {output_rel_path}")

if __name__ == '__main__':
    main()
