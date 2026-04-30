import urllib.request
from bs4 import BeautifulSoup

url = 'https://www.urdupoint.com/business/directory/1316/neon-sign-mfrs.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'})

try:
    with urllib.request.urlopen(req) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        
        links = soup.find_all('a', href=True)
        business_links = [l['href'] for l in links if '/business/directory/detail/' in l['href'] or '/detail/' in l['href']]
        unique_b = list(set(business_links))
        
        print(f"Found {len(unique_b)} business links on subcategory page 1")
        for b in unique_b[:10]:
            print(b)
except Exception as e:
    print("Error:", e)
