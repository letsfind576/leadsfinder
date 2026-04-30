import urllib.request

req = urllib.request.Request(
    'https://www.urdupoint.com/business/directory.html', 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'}
)

try:
    with urllib.request.urlopen(req) as response:
        print("Status Code:", response.getcode())
except Exception as e:
    print("Error:", e)
