from bs4 import BeautifulSoup
import json

with open('cat.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

links = soup.find_all('a', href=True)
hrefs = list(set([l['href'] for l in links if '/business/' in l['href']]))

with open('cat_links.txt', 'w', encoding='utf-8') as f:
    for h in hrefs:
        f.write(h + '\n')
print(f"Saved {len(hrefs)} links to cat_links.txt")
