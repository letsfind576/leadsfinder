import urllib.request
from bs4 import BeautifulSoup

req = urllib.request.Request(
    'https://www.urdupoint.com/business/directory.html', 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Let's find categories
        print("Finding categories...")
        # Often categories are in specific lists or divs
        links = soup.find_all('a', href=True)
        cat_links = [l['href'] for l in links if '/business/' in l['href'] and ('category' in l['href'] or 'companies' in l['href'] or '.html' in l['href'])]
        
        # Print first 20 potential category links
        for link in cat_links[:20]:
            print(link)
except Exception as e:
    print("Error:", e)
