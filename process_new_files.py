import os
import pandas as pd
import glob
import re
import difflib

def normalize_company_name(name):
    if pd.isna(name): return ""
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    name = name.replace('pvtltd', '').replace('limited', '').replace('pvt', '').replace('ltd', '')
    return name

def main():
    existing_companies = set()
    
    # Load all existing companies to avoid duplicates
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

    print(f"Loaded {len(existing_companies)} existing companies.")
    
    new_data = {'chemical_directory_complete.csv': [], 'focal_persons_directory_complete.csv': []}
    added_count = 0
    duplicate_count = 0

    def add_row(target_csv, comp_name, address, name, phone, email, sector, speciality):
        nonlocal added_count, duplicate_count
        norm = normalize_company_name(comp_name)
        if not norm: return
        if norm in existing_companies:
            duplicate_count += 1
            return
        
        new_row = {
            'Company Name': comp_name,
            'Address': address,
            'Name': name,
            'Ph (Off)': phone,
            'Email': email,
            'Business Sector(s)': sector,
            'Business Speciality': speciality
        }
        new_data[target_csv].append(new_row)
        added_count += 1
        existing_companies.add(norm)

    # Process pcdma CSV files (3 rows per record)
    pcdma_csvs = glob.glob('pcdma*.csv')
    for f in pcdma_csvs:
        try:
            # First read as headerless to ensure we get all data
            df = pd.read_csv(f, header=None)
            
            # The data has chunks of 3 rows per record
            # We iterate by 3
            for i in range(1, len(df), 3):
                if i + 2 >= len(df):
                    break
                row1 = df.iloc[i]
                row2 = df.iloc[i+1]
                row3 = df.iloc[i+2]
                
                comp_name = str(row1[2]) if not pd.isna(row1[2]) else ""
                
                addr_parts = []
                if not pd.isna(row2[2]): addr_parts.append(str(row2[2]))
                if not pd.isna(row3[2]): addr_parts.append(str(row3[2]))
                address = " ".join(addr_parts)
                
                phone_parts = []
                if not pd.isna(row1[3]): phone_parts.append(str(row1[3]))
                if not pd.isna(row2[3]): phone_parts.append(str(row2[3]))
                phone = " ".join(phone_parts)
                
                name = str(row1[4]) if not pd.isna(row1[4]) else ""
                email = str(row3[3]) if not pd.isna(row3[3]) and "N/A" not in str(row3[3]) else ""
                if email.lower() == 'nan': email = ''
                
                add_row('chemical_directory_complete.csv', comp_name, address, name, phone, email, 'Chemicals', '')
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    # Process pcdma71.xlsx
    if os.path.exists('pcdma71.xlsx'):
        df71 = pd.read_excel('pcdma71.xlsx')
        for _, row in df71.iterrows():
            comp_name = str(row.get('Company Name', ''))
            name = str(row.get('Contact Person', ''))
            phone = str(row.get('Phone', '')) + " " + str(row.get('Mobile', ''))
            phone = phone.strip()
            email = str(row.get('Email', ''))
            if email.lower() == 'nan': email = ''
            address = str(row.get('Address', ''))
            
            add_row('chemical_directory_complete.csv', comp_name, address, name, phone, email, 'Chemicals', '')

    # Process Focal_Persons_List.xlsx
    if os.path.exists('Focal_Persons_List.xlsx'):
        df_fp = pd.read_excel('Focal_Persons_List.xlsx')
        for _, row in df_fp.iterrows():
            comp_name = str(row.get('Organization', ''))
            name = str(row.get('FP Name', ''))
            phone = str(row.get('FP Phone', '')) + " " + str(row.get('FP Cell', ''))
            phone = phone.strip()
            email = str(row.get('FP Email', ''))
            if email.lower() == 'nan': email = ''
            
            add_row('focal_persons_directory_complete.csv', comp_name, '', name, phone, email, 'Organizations', '')

    print(f"Duplicates skipped: {duplicate_count}")
    print(f"New entries to add: {added_count}")

    # Write to CSVs
    for target_csv, rows in new_data.items():
        if not rows: continue
        df_new = pd.DataFrame(rows)
        cols = ['Mship No', 'Company Name', 'Address', 'Name', 'Ph (Off)', 'Email', 'Business Sector(s)', 'Business Speciality']
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
            df_combined.to_csv(target_csv, index=False, encoding='utf-8')
        else:
            df_new.to_csv(target_csv, index=False, encoding='utf-8')
            
    print("Data successfully processed and saved to CSVs.")

if __name__ == '__main__':
    main()
