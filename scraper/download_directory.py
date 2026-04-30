import urllib.request
import os

req = urllib.request.Request(
    'https://www.urdupoint.com/business/directory.html', 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read()
        with open('directory.html', 'wb') as f:
            f.write(html)
        print(f"Saved directory.html ({len(html)} bytes)")
except Exception as e:
    print("Error:", e)
