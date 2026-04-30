import pandas as pd
import re
import os
import glob

def normalize_company_name(name):
    if pd.isna(name): return ""
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    name = name.replace('pvtltd', '').replace('limited', '').replace('pvt', '').replace('ltd', '')
    return name

def clean_str(val):
    """Clean a value to a safe single-line string."""
    if pd.isna(val): return ''
    s = str(val).replace('\n', ' ').replace('\r', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# ─── Load existing company set ───────────────────────────────────────────────
existing_companies = set()
existing_csvs = glob.glob('*_directory_complete*.csv')
for csv_file in existing_csvs:
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(csv_file, encoding='cp1252')
        except Exception:
            continue
    except Exception:
        continue
    if 'Company Name' in df.columns:
        for c in df['Company Name'].dropna():
            norm = normalize_company_name(c)
            if norm:
                existing_companies.add(norm)

print(f"Existing companies loaded: {len(existing_companies)}")

new_data = {}  # target_csv -> list of row dicts
added_total = 0
dup_total = 0

def try_add(target_csv, comp_name, address, name, phone, email, sector, speciality):
    global added_total, dup_total
    comp_name = clean_str(comp_name)
    if not comp_name: return
    norm = normalize_company_name(comp_name)
    if not norm: return
    if norm in existing_companies:
        dup_total += 1
        return
    if target_csv not in new_data:
        new_data[target_csv] = []
    new_data[target_csv].append({
        'Mship No': '',
        'Company Name': comp_name,
        'Address': clean_str(address),
        'Name': clean_str(name),
        'Ph (Off)': clean_str(phone),
        'Email': clean_str(email),
        'Business Sector(s)': clean_str(sector),
        'Business Speciality': clean_str(speciality),
    })
    added_total += 1
    existing_companies.add(norm)

# ─── 1. Pastic Industrial Database ───────────────────────────────────────────
def parse_pastic_other(text):
    text = clean_str(text)
    addr_match = re.search(r'Address:\s*(.*?)(?:Brand specification:|Estab Year:|Phone:|$)', text, re.IGNORECASE)
    address = addr_match.group(1).strip() if addr_match else ''
    phone_match = re.search(r'Phone:\s*([\d\+\-\s\(\),\.]+?)(?:\s{2,}|$)', text, re.IGNORECASE)
    phone = phone_match.group(1).strip() if phone_match else ''
    return address, phone

df_pastic = pd.read_excel('Pastic_Industrial_Database.xlsx')
print(f"\nPastic Industrial Database: {len(df_pastic)} rows")
for _, row in df_pastic.iterrows():
    comp_name = clean_str(row.get('INDNAME', ''))
    sector = clean_str(row.get('INDSECTOR', ''))
    address, phone = parse_pastic_other(row.get('OTHER', ''))
    # Map sector to closest existing directory
    sector_lower = sector.lower()
    if 'textile' in sector_lower or 'apparel' in sector_lower:
        target = 'textiles_directory_complete.csv'
    elif 'chemical' in sector_lower:
        target = 'chemical_directory_complete.csv'
    elif 'food' in sector_lower:
        target = 'food_directory_complete.csv'
    elif 'auto' in sector_lower or 'automobile' in sector_lower:
        target = 'autoparts_directory_complete.csv'
    elif 'electric' in sector_lower:
        target = 'electronics_directory_complete.csv'
    elif 'rubber' in sector_lower or 'plastic' in sector_lower:
        target = 'pvc_directory_complete.csv'
    elif 'pharma' in sector_lower or 'medicine' in sector_lower:
        target = 'medicine_directory_complete.csv'
    elif 'carpet' in sector_lower:
        target = 'carpets_directory_complete.csv'
    elif 'engineering' in sector_lower or 'machinery' in sector_lower:
        target = 'engineering_directory_complete.csv'
    elif 'printing' in sector_lower:
        target = 'printing_directory_complete.csv'
    elif 'agriculture' in sector_lower or 'agribusiness' in sector_lower:
        target = 'agricultural_directory_complete.csv'
    elif 'leather' in sector_lower:
        target = 'leather_directory_complete.csv'
    else:
        target = 'pastic_industrial_directory_complete.csv'
    try_add(target, comp_name, address, '', phone, '', sector, '')

pastic_added = added_total
print(f"  Added from Pastic: {pastic_added}, Duplicates: {dup_total}")

# ─── 2. WCCI Lahore ───────────────────────────────────────────────────────────
prev_count = added_total
df_wcci = pd.read_excel('WCCI-Lahore-company-list.xlsx')
print(f"\nWCCI Lahore: {len(df_wcci)} rows")
for _, row in df_wcci.iterrows():
    comp_name = clean_str(row.get('Company', ''))
    address = clean_str(row.get('Address', ''))
    name = clean_str(row.get('Rep. Name', ''))
    phone = clean_str(str(row.get('Telephone No', '')) + ' ' + str(row.get('Mob No', '')))
    email = clean_str(row.get('E-mail', ''))
    try_add('wcci_lahore_directory_complete.csv', comp_name, address, name, phone, email, 'Business', '')
print(f"  Added from WCCI: {added_total - prev_count}")

# ─── 3. Industrial Directory Kasur ───────────────────────────────────────────
prev_count = added_total
df_kasur = pd.read_excel('Industrial_Directory_Kasur.xlsx')
print(f"\nIndustrial Directory Kasur: {len(df_kasur)} rows")

def parse_kasur_details(details_text):
    """Parse: NAME  ADDRESS  PHONE  PRODUCT"""
    text = clean_str(details_text)
    # Extract phone (common formats: digits with dashes, starts with 0)
    phone_match = re.search(r'(?:^|[\s,])(\d[\d\-\s]{6,15})(?:\s|,|$)', text)
    phone = phone_match.group(1).strip() if phone_match else ''
    # Remove phone from text to get name+address
    text_no_phone = text.replace(phone, '').strip() if phone else text
    # Split on first space after typical suffix to get name vs address
    return text_no_phone, phone

for _, row in df_kasur.iterrows():
    details = clean_str(row.get('Details', ''))
    product = clean_str(row.get('Product', ''))
    if not details: continue
    # Try to extract name as first part before address keywords
    name_match = re.match(r'^(.*?(?:PVT|LTD|LIMITED|CORP|MILLS|INDUSTRIES|ENTERPRISES|BROTHERS|SONS|CO\.|CO,)\b\.?)\s+(.*)', details, re.IGNORECASE)
    if name_match:
        comp_name = name_match.group(1).strip()
        rest = name_match.group(2).strip()
    else:
        # Split at first number (start of address like "44-KM")
        parts = re.split(r'\s+(?=\d)', details, maxsplit=1)
        comp_name = parts[0].strip() if parts else details
        rest = parts[1].strip() if len(parts) > 1 else ''
    
    phone_match = re.search(r'(\d[\d\-\+\s]{6,15})', rest)
    phone = phone_match.group(1).strip() if phone_match else ''
    address = rest.replace(phone, '').strip() if phone else rest
    
    # Map product to sector
    prod_lower = product.lower()
    if 'auto' in prod_lower or 'car' in prod_lower or 'tyre' in prod_lower:
        target = 'autoparts_directory_complete.csv'
    elif 'textile' in prod_lower or 'yarn' in prod_lower or 'fabric' in prod_lower:
        target = 'textiles_directory_complete.csv'
    elif 'leather' in prod_lower or 'shoe' in prod_lower or 'footwear' in prod_lower:
        target = 'leather_directory_complete.csv'
    elif 'chemical' in prod_lower or 'dye' in prod_lower:
        target = 'chemical_directory_complete.csv'
    elif 'food' in prod_lower or 'rice' in prod_lower or 'flour' in prod_lower:
        target = 'food_directory_complete.csv'
    elif 'steel' in prod_lower or 'iron' in prod_lower or 'metal' in prod_lower:
        target = 'steel_directory_complete.csv'
    else:
        target = 'kasur_industrial_directory_complete.csv'
    
    try_add(target, comp_name, f"Kasur - {address}", '', phone, '', product, '')
print(f"  Added from Kasur: {added_total - prev_count}")

# ─── Write to CSVs ────────────────────────────────────────────────────────────
print(f"\nTotal new entries: {added_total}")
print(f"Total duplicates skipped: {dup_total}")

cols = ['Mship No', 'Company Name', 'Address', 'Name', 'Ph (Off)', 'Email', 'Business Sector(s)', 'Business Speciality']

for target_csv, rows in new_data.items():
    df_new = pd.DataFrame(rows)
    for c in cols:
        if c not in df_new.columns:
            df_new[c] = ''
    df_new = df_new[cols]
    
    if os.path.exists(target_csv):
        try:
            df_existing = pd.read_csv(target_csv, encoding='utf-8')
        except UnicodeDecodeError:
            df_existing = pd.read_csv(target_csv, encoding='cp1252')
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(target_csv, index=False, encoding='utf-8', lineterminator='\n')
    else:
        df_new.to_csv(target_csv, index=False, encoding='utf-8', lineterminator='\n')
    print(f"  Saved {len(rows)} rows to {target_csv}")

print("\nDone.")
