import urllib.request
from bs4 import BeautifulSoup
import json
import time
import os

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'}
MAX_SUBCATEGORIES_TO_TEST = None # Scrape all subcategories

def get_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_listings():
    if not os.path.exists('subcategories.json'):
        print("subcategories.json not found! Run scrape_directories.py first.")
        return
        
    with open('subcategories.json', 'r', encoding='utf-8') as f:
        subcats = json.load(f)
        
    print(f"Loaded {len(subcats)} Subcategories. Testing first {MAX_SUBCATEGORIES_TO_TEST or len(subcats)}...")
    subcats = subcats[:MAX_SUBCATEGORIES_TO_TEST] if MAX_SUBCATEGORIES_TO_TEST else subcats
    
    all_business_links = []
    
    for sc_url in subcats:
        print(f"Processing Subcategory: {sc_url}")
        page = 1
        previous_b_links = set()
        
        while True:
            paged_url = f"{sc_url.split('.html')[0]}.html?page={page}" if page > 1 else sc_url
            print(f" -> Fetching page {page}")
            html = get_html(paged_url)
            if not html: break
            
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)
            
            b_links = set([l['href'] for l in links if '/business/directory/detail/' in l['href']])
            
            if len(b_links) == 0 or b_links == previous_b_links:
                break # No more businesses or we are looping page 1
                
            previous_b_links = b_links
            
            for b in b_links:
                full_url = 'https://www.urdupoint.com' + b if not b.startswith('http') else b
                all_business_links.append({"subcategory": sc_url.split('/')[-1].replace('.html',''), "url": full_url})
                
            # Check if there is a 'Next' pagination link
            next_link = [l for l in links if l.text.strip().lower() == 'next' or 'rel="next"' in str(l)]
            if not next_link and page > 1:
                # Basic assumption: if page > 1 and no next link, we reached the end
                try:
                    # Let's just keep going until b_links is 0, which is perfectly robust.
                    pass
                except: pass
                
            page += 1
            time.sleep(1) # Be polite
            
    # Deduplicate based on URL
    unique_businesses = {b['url']: b for b in all_business_links}.values()
    unique_list = list(unique_businesses)
    
    print(f"Total Business URLs extracted: {len(unique_list)}")
    with open('business_urls.json', 'w', encoding='utf-8') as f:
        json.dump(unique_list, f, indent=2)

if __name__ == '__main__':
    scrape_listings()
