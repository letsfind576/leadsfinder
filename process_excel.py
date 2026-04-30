import os
import pandas as pd
import glob
import re
import difflib
import math

def normalize_company_name(name):
    if not isinstance(name, str):
        return ""
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    name = name.replace('pvtltd', '').replace('limited', '').replace('pvt', '').replace('ltd', '')
    return name

def parse_name_address(text):
    text = str(text).strip()
    # Attempt to split at common suffixes
    match = re.search(r'(.*? (?:PVT|LTD|LIMITED|CORP|MILLS|FACTORY|ENTERPRISES|INDUSTRIES|SONS|BROTHERS)\b\.?)(.*)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    # Fallback: split by first comma if exists
    if ',' in text:
        parts = text.split(',', 1)
        return parts[0].strip(), parts[1].strip()
    # Otherwise, return whole as name
    return text, ""

def sanitize_dir_name(name):
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    name = name.strip('_')
    return name

def main():
    existing_csvs = glob.glob('*_directory_complete*.csv')
    existing_companies = set()
    dir_mapping = {}

    for csv_file in existing_csvs:
        base_name = re.sub(r'_directory_complete.*\.csv$', '', csv_file)
        dir_mapping[base_name] = csv_file
        
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

    print(f"Loaded {len(existing_companies)} existing companies.")
    print(f"Found {len(dir_mapping)} existing directories.")
    
    excel_file = 'Industrial Directory Lahore.xlsx'
    df_excel = pd.read_excel(excel_file)
    
    # Identify header row
    # The true header is where 'Unnamed: 1' == 'NAME AND ADDRESS OF UNIT'
    header_idx = df_excel.index[df_excel['Unnamed: 1'] == 'NAME AND ADDRESS OF UNIT'].tolist()
    if header_idx:
        df_excel = df_excel.iloc[header_idx[0]+1:].reset_index(drop=True)
    
    # Columns map: 1: Name&Address, 2: Phone, 3: Industry, 7: Product
    added_count = 0
    duplicate_count = 0
    
    # Dictionary to hold new rows per directory
    new_data = {}
    
    for idx, row in df_excel.iterrows():
        raw_name = str(row.get('Unnamed: 1', ''))
        if raw_name == 'nan' or not raw_name.strip():
            continue
            
        industry = str(row.get('Unnamed: 3', ''))
        if industry == 'nan' or not industry.strip():
            continue
            
        norm_name = normalize_company_name(raw_name)
        if norm_name in existing_companies:
            duplicate_count += 1
            continue
            
        # Parse fields
        company_name, address = parse_name_address(raw_name)
        phone = str(row.get('Unnamed: 2', ''))
        if phone == 'nan': phone = ''
        product = str(row.get('Unnamed: 7', ''))
        if product == 'nan': product = ''
        
        # Match directory
        sanitized_ind = sanitize_dir_name(industry)
        # Try to find a close match in existing directories
        matches = difflib.get_close_matches(sanitized_ind, dir_mapping.keys(), n=1, cutoff=0.7)
        
        if matches:
            target_csv = dir_mapping[matches[0]]
            # Ensure the exact filename isn't just a prefix if we can avoid it, but get_close_matches handles it
        else:
            # We must create a new directory file
            # E.g., 'ac_refrigerator_deep_freezer_directory_complete.csv'
            # Let's truncate long names to avoid OS errors
            short_ind = sanitized_ind[:40]
            target_csv = f"{short_ind}_directory_complete.csv"
            dir_mapping[short_ind] = target_csv
            
        if target_csv not in new_data:
            new_data[target_csv] = []
            
        new_row = {
            'Mship No': f'NEW-{added_count+1}',
            'Company Name': company_name,
            'Address': address,
            'Name': '',
            'Ph (Off)': phone,
            'Email': '',
            'Business Sector(s)': industry,
            'Business Speciality': product
        }
        new_data[target_csv].append(new_row)
        added_count += 1
        existing_companies.add(norm_name)
        
    print(f"Duplicates skipped: {duplicate_count}")
    print(f"New entries to add: {added_count}")
    
    # Write to CSVs
    for target_csv, rows in new_data.items():
        df_new = pd.DataFrame(rows)
        # Ensure correct column order
        cols = ['Mship No', 'Company Name', 'Address', 'Name', 'Ph (Off)', 'Email', 'Business Sector(s)', 'Business Speciality']
        for c in cols:
            if c not in df_new.columns:
                df_new[c] = ''
        df_new = df_new[cols]
        
        if os.path.exists(target_csv):
            # Append
            try:
                df_existing = pd.read_csv(target_csv, encoding='utf-8')
            except UnicodeDecodeError:
                df_existing = pd.read_csv(target_csv, encoding='cp1252')
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(target_csv, index=False, encoding='utf-8')
        else:
            # Create new
            df_new.to_csv(target_csv, index=False, encoding='utf-8')
            
    print("Data successfully processed and saved to CSVs.")

if __name__ == '__main__':
    main()
