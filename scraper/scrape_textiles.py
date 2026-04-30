"""
All-in-one scraper for UrduPoint Textiles Directory.
Stages:
  1. Fetch subcategories from the Textiles main category page
  2. For each subcategory, paginate and collect all business detail URLs
  3. Visit each business detail page and extract all available information
  4. Save everything to textile_directory_complete.csv with incremental writes
"""
import urllib.request
from bs4 import BeautifulSoup
import json
import csv
import time
import os
import re

BASE = 'https://www.urdupoint.com'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
TEXTILES_URL = f'{BASE}/business/directory/42/textiles.html'
OUTPUT_CSV = 'textile_directory_complete.csv'
DELAY = 0.8  # seconds between requests

CSV_FIELDS = [
    'Company Name', 'Contact Person', 'Address', 'City', 'Phone', 'Fax',
    'Mobile', 'Email', 'Website', 'Business Sector', 'Business Speciality',
    'Products/Services', 'Description', 'Source URL', 'Directory'
]

def get_html(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read()
        except Exception as e:
            print(f"  [Retry {attempt+1}/{retries}] Error: {e}")
            time.sleep(2)
    return None

def full_url(href):
    if href.startswith('http'): return href
    return BASE + href

def clean(text):
    if not text: return ''
    return re.sub(r'\s+', ' ', text).strip()

# ─── STAGE 1: Get all textile subcategory URLs ───────────────────────
def get_subcategories():
    print("=" * 60)
    print("STAGE 1: Fetching Textile subcategories...")
    print("=" * 60)
    
    html = get_html(TEXTILES_URL)
    if not html:
        print("FATAL: Could not fetch textiles page!")
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    
    subcats = set()
    for link in links:
        href = link['href']
        furl = full_url(href)
        # Subcategories are like /business/directory/NNN/name.html (7 parts when split)
        if '/business/directory/' in href and '/city/' not in href and '/detail/' not in href and 'submit' not in href:
            if furl != TEXTILES_URL and len(furl.split('/')) == 7:
                subcats.add(furl)
    
    subcats = sorted(subcats)
    print(f"Found {len(subcats)} textile subcategories")
    return subcats

# ─── STAGE 2: Collect all business detail URLs from subcategories ────
def get_business_urls(subcategories):
    print("\n" + "=" * 60)
    print("STAGE 2: Collecting business URLs from subcategories...")
    print("=" * 60)
    
    all_urls = []  # list of (url, subcategory_name)
    
    for i, sc_url in enumerate(subcategories):
        sc_name = sc_url.split('/')[-1].replace('.html', '')
        print(f"\n[{i+1}/{len(subcategories)}] {sc_name}")
        
        page = 1
        prev_links = set()
        
        while True:
            paged = f"{sc_url}?page={page}" if page > 1 else sc_url
            html = get_html(paged)
            if not html:
                break
            
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)
            detail_links = set()
            for link in links:
                href = link['href']
                if '/business/directory/detail/' in href:
                    detail_links.add(full_url(href))
            
            if not detail_links or detail_links == prev_links:
                break  # no new results = end of pagination
            
            for dl in detail_links:
                all_urls.append((dl, sc_name))
            
            prev_links = detail_links
            page += 1
            time.sleep(DELAY)
        
        time.sleep(DELAY)
    
    # Deduplicate by URL, keeping first subcategory
    seen = {}
    unique = []
    for url, sc in all_urls:
        if url not in seen:
            seen[url] = sc
            unique.append((url, sc))
    
    print(f"\nTotal unique business URLs: {len(unique)}")
    
    # Save checkpoint
    with open('textile_business_urls.json', 'w', encoding='utf-8') as f:
        json.dump([{'url': u, 'subcategory': s} for u, s in unique], f, indent=2)
    print("Saved checkpoint: textile_business_urls.json")
    
    return unique

# ─── STAGE 3: Extract details from each business page ───────────────
def extract_business_detail(url, subcategory):
    html = get_html(url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    data = {field: '' for field in CSV_FIELDS}
    data['Directory'] = 'Textiles'
    data['Business Speciality'] = subcategory.replace('-', ' ').title()
    data['Source URL'] = url
    
    # Company name from h1
    h1 = soup.find('h1')
    if h1:
        data['Company Name'] = clean(h1.text)
    
    # Business sector from title
    title = soup.find('title')
    if title:
        data['Business Sector'] = clean(title.text.split('|')[0]) if '|' in title.text else clean(title.text)
    
    # Try to find structured table data (common on UrduPoint detail pages)
    # Look for table rows or dt/dd pairs
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = clean(cells[0].text).lower().rstrip(':')
                value = clean(cells[1].text)
                map_field(data, label, value)
    
    # Also scan all text blocks for label: value patterns
    all_text_elements = soup.find_all(['p', 'div', 'li', 'span', 'dd', 'td'])
    for elem in all_text_elements:
        text = elem.text.strip()
        if ':' in text and len(text) < 500:
            parts = text.split(':', 1)
            label = parts[0].strip().lower()
            value = parts[1].strip() if len(parts) > 1 else ''
            map_field(data, label, value)
    
    # Try to extract email from mailto links
    mailto = soup.find('a', href=re.compile(r'^mailto:'))
    if mailto:
        data['Email'] = clean(mailto['href'].replace('mailto:', ''))
    
    # Try to extract phone from tel links
    tel = soup.find('a', href=re.compile(r'^tel:'))
    if tel:
        phone = clean(tel['href'].replace('tel:', ''))
        if not data['Phone']:
            data['Phone'] = phone
    
    return data

def map_field(data, label, value):
    if not value or len(value) > 300:
        return
    
    label = label.strip().lower().rstrip(':')
    
    if label in ('address', 'location', 'office address', 'registered address'):
        if not data['Address']:
            data['Address'] = value
    elif label in ('city', 'town'):
        if not data['City']:
            data['City'] = value
    elif label in ('phone', 'ph', 'telephone', 'tel', 'phone no', 'ph (off)', 'landline', 'off'):
        if not data['Phone']:
            data['Phone'] = value
    elif label in ('fax', 'fax no'):
        if not data['Fax']:
            data['Fax'] = value
    elif label in ('mobile', 'cell', 'mobile no', 'cell no', 'mobile phone'):
        if not data['Mobile']:
            data['Mobile'] = value
    elif label in ('email', 'e-mail', 'email address', 'e-mail address'):
        if not data['Email']:
            data['Email'] = value
    elif label in ('website', 'web', 'url', 'web site', 'homepage'):
        if not data['Website']:
            data['Website'] = value
    elif label in ('contact person', 'contact', 'name', 'person', 'representative'):
        if not data['Contact Person']:
            data['Contact Person'] = value
    elif label in ('products', 'services', 'products/services', 'product'):
        if not data['Products/Services']:
            data['Products/Services'] = value
    elif label in ('description', 'about', 'details', 'company profile', 'business description'):
        if not data['Description']:
            data['Description'] = value

def scrape_details(business_urls):
    print("\n" + "=" * 60)
    print("STAGE 3: Extracting business details...")
    print("=" * 60)
    
    total = len(business_urls)
    
    # Write CSV header
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
    
    extracted = 0
    
    for i, (url, subcategory) in enumerate(business_urls):
        print(f"[{i+1}/{total}] {url.split('/')[-1][:50]}")
        
        data = extract_business_detail(url, subcategory)
        if data:
            # Append to CSV incrementally
            with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                writer.writerow(data)
            extracted += 1
        
        time.sleep(DELAY)
        
        # Progress update every 50
        if (i + 1) % 50 == 0:
            print(f"  ... Progress: {i+1}/{total} processed, {extracted} extracted")
    
    print(f"\n{'=' * 60}")
    print(f"DONE! Extracted {extracted}/{total} businesses to {OUTPUT_CSV}")
    print(f"{'=' * 60}")

# ─── MAIN ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Check for checkpoint (resume from stage 3 if URLs already collected)
    if os.path.exists('textile_business_urls.json'):
        print("Found textile_business_urls.json checkpoint, skipping Stages 1 & 2...")
        with open('textile_business_urls.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        business_urls = [(d['url'], d['subcategory']) for d in data]
        print(f"Loaded {len(business_urls)} business URLs from checkpoint")
    else:
        subcategories = get_subcategories()
        if not subcategories:
            print("No subcategories found, exiting.")
            exit(1)
        business_urls = get_business_urls(subcategories)
    
    scrape_details(business_urls)
