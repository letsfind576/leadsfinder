import urllib.request
from bs4 import BeautifulSoup
import json
import csv
import time
import os

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'}
MAX_BUSINESSES_TO_TEST = None # Scrape full

output_file = 'textile_directory_complete.csv'

def get_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def clean_text(text):
    if not text: return ''
    return text.strip().replace('\r', '').replace('\n', ' ')

def scrape_details():
    if not os.path.exists('business_urls.json'):
        print("business_urls.json not found! Run scrape_listings.py first.")
        return
        
    with open('business_urls.json', 'r', encoding='utf-8') as f:
        businesses = json.load(f)
        
    print(f"Loaded {len(businesses)} Business URLs. Testing first {MAX_BUSINESSES_TO_TEST or len(businesses)}...")
    businesses = businesses[:MAX_BUSINESSES_TO_TEST] if MAX_BUSINESSES_TO_TEST else businesses
    
    extracted_data = []
    
    for count, b in enumerate(businesses):
        url = b['url']
        subcategory = b['subcategory']
        print(f"[{count+1}/{len(businesses)}] Extracting: {url}")
        
        html = get_html(url)
        if not html: continue
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Scrape precise details from the page
        data = {
            'Mship No': '',
            'Company Name': '',
            'Address': '',
            'Name': '',
            'Ph (Off)': '',
            'Email': '',
            'Business Sector(s)': getattr(soup.find('title'), 'text', '').split('|')[0].strip() if soup.find('title') else subcategory,
            'Business Speciality': subcategory.replace('-', ' ').title(),
            'City': '',
            'Directory': 'UrduPoint Web'
        }
        
        # Urdupoint business details are usually in `div` tables or `ul` lists
        try:
            # H1 contains the company name
            h1 = soup.find('h1')
            if h1: data['Company Name'] = clean_text(h1.text)
            
            # Contact info is usually in paragraphs or generic detail blocks
            text_blocks = soup.find_all(['p', 'div', 'li', 'span'])
            for block in text_blocks:
                t = block.text.lower()
                if 'address:' in t or 'location:' in t:
                    data['Address'] = clean_text(block.text.split(':', 1)[-1])
                elif 'phone:' in t or 'ph:' in t or 'contact:' in t:
                    data['Ph (Off)'] = clean_text(block.text.split(':', 1)[-1])
                elif 'email:' in t:
                    data['Email'] = clean_text(block.text.split(':', 1)[-1])
                elif 'city:' in t:
                    data['City'] = clean_text(block.text.split(':', 1)[-1])
                    
        except Exception as ex:
            print(f"Parsing error for {url}: {ex}")
            
        extracted_data.append(data)
        time.sleep(1)
        
    # Write to CSV
    keys = ['Mship No', 'Company Name', 'Address', 'Name', 'Ph (Off)', 'Email', 'Business Sector(s)', 'Business Speciality', 'City', 'Directory']
    output_file = 'urdupoint_directory_complete.csv'
    
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(extracted_data)
        
    print(f"Saved {len(extracted_data)} business records to {output_file}.")
    print("Run this file with `MAX_BUSINESSES_TO_TEST = None` to scrape all.")

if __name__ == '__main__':
    scrape_details()
