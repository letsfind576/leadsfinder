import fs from 'fs';
import Papa from 'papaparse';

const csvFile = fs.readFileSync('public/data.csv', 'utf8');
const parsed = Papa.parse(csvFile, { header: true });
const data = parsed.data.filter(row => row['Company Name'] && row['Company Name'].trim() !== '');

async function enrichCompany(company) {
    const query = `${company['Company Name']} ${company['Address']}`;
    try {
        const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/100'
            }
        });
        const html = await response.text();
        
        // Basic extraction of the first search result snippet
        const snippetMatch = html.match(/<a class="result__snippet[^>]*>(.*?)<\/a>/);
        if (snippetMatch && snippetMatch[1]) {
            let text = snippetMatch[1].replace(/<[^>]+>/g, '').trim();
            // Decode basic html entities
            text = text.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
            return text;
        }
    } catch (e) {
        console.error('Error fetching for', company['Company Name'], e.message);
    }
    return '';
}

async function main() {
    console.log("Starting enrichment for companies. Note: doing all 1200 at once might hit rate limits.");
    console.log("We'll enrich a sample batch initially, you can adjust the bounds of this loop to process more over time.");
    
    // Enrich the first 15 as a demonstration (avoiding long runtimes/bans)
    const limit = Math.min(15, data.length);
    for (let i = 0; i < limit; i++) {
        const company = data[i];
        console.log(`Enriching ${i+1}/${limit}: ${company['Company Name']}`);
        const details = await enrichCompany(company);
        company['Digital Footprint'] = details || 'No footprint found.';
        
        // Wait 1.5 seconds to respect rate limits
        await new Promise(r => setTimeout(r, 1500));
    }
    
    // For the rest, add empty or un-enriched placeholders
    for (let i = limit; i < data.length; i++) {
        data[i]['Digital Footprint'] = 'Pending enrichment...';
    }

    const csvOut = Papa.unparse(data);
    fs.writeFileSync('public/enriched_data.csv', csvOut);
    console.log("Saved enriched data to public/enriched_data.csv");
}

main();
