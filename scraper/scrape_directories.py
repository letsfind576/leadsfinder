import urllib.request
from bs4 import BeautifulSoup
import json
import time
import os

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'}
MAX_MAIN_CATEGORIES_TO_TEST = 2 # Set to None for full scrape

def get_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_directories():
    print("Fetching main directory page...")
    html = get_html('https://www.urdupoint.com/business/directory.html')
    if not html: return
    
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    
    # Override to target ONLY textiles
    main_cats = ['https://www.urdupoint.com/business/directory/42/textiles.html']
    
    print(f"Targeting only Textile category...")
    
    all_subcategories = []
    
    for count, mc_url in enumerate(main_cats):
        if not mc_url.startswith('http'): 
            mc_url = 'https://www.urdupoint.com' + mc_url
            
        print(f"Fetching Main Category {count+1}/{len(main_cats)}: {mc_url}")
        mc_html = get_html(mc_url)
        if not mc_html: continue
        
        mc_soup = BeautifulSoup(mc_html, 'html.parser')
        mc_links = mc_soup.find_all('a', href=True)
        
        # Subcategories look like /business/directory/1316/neon-sign-mfrs.html
        sub_cats = [l['href'] for l in mc_links if '/business/directory/' in l['href'] and ('/directory/detail/' not in l['href']) and ('/city/' not in l['href'])]
        # Filter strictly those with numeric IDs that are subcategories
        sub_cats = list(set([l for l in sub_cats if len(l.split('/')) == 7 and l != mc_url.replace('https://www.urdupoint.com', '') and l != mc_url]))
        
        for sc in sub_cats:
            full_sc = 'https://www.urdupoint.com' + sc if not sc.startswith('http') else sc
            all_subcategories.append(full_sc)
            
        time.sleep(1) # Be polite
        
    all_subcategories = list(set(all_subcategories))
    print(f"Total Subcategories extracted: {len(all_subcategories)}")
    
    with open('subcategories.json', 'w', encoding='utf-8') as f:
        json.dump(all_subcategories, f, indent=2)

if __name__ == '__main__':
    scrape_directories()
