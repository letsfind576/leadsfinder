from bs4 import BeautifulSoup
import json

with open('directory.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

links = soup.find_all('a', href=True)
b_links = [l['href'] for l in links if '/business/directory/' in l['href']]
unique_links = list(set(b_links))

categories = []
for l in links:
    href = l['href']
    if '/business/directory/' in href:
        categories.append({'name': l.text.strip(), 'url': href})

with open('categories_list.json', 'w', encoding='utf-8') as f:
    json.dump(categories, f, indent=2)

print(f"Saved {len(categories)} explicit category links to categories_list.json")
