import fs from 'fs';

async function testFetch() {
    console.log("Fetching UrduPoint directory...");
    const response = await fetch('https://www.urdupoint.com/business/directory.html', {
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
    });
    
    console.log("Status:", response.status);
    if (!response.ok) return;
    
    const text = await response.text();
    fs.writeFileSync('urdupoint.html', text);
    console.log(`Saved ${text.length} bytes to urdupoint.html`);
}

testFetch();
