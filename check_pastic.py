import pandas as pd
import re

df = pd.read_excel('Pastic_Industrial_Database.xlsx')

def parse_other(text):
    text = str(text) if pd.notna(text) else ''
    
    # Extract address
    addr_match = re.search(r'Address:\s*(.*?)(?:Brand specification:|Estab Year:|Phone:|$)', text, re.IGNORECASE)
    address = addr_match.group(1).strip() if addr_match else ''
    
    # Extract phone
    phone_match = re.search(r'Phone:\s*([\d\+\-\s\(\),\.]+?)(?:\s{2,}|$)', text, re.IGNORECASE)
    phone = phone_match.group(1).strip() if phone_match else ''
    
    return address, phone

# Test
for i in range(5):
    a, p = parse_other(df.iloc[i]['OTHER'])
    print(f"Name: {df.iloc[i]['INDNAME']}")
    print(f"  Address: {a}")
    print(f"  Phone: {p}")
    print()
