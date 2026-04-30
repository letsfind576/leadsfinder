import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

function main() {
    const parentDir = path.join(process.cwd(), '..');
    const files = fs.readdirSync(parentDir).filter(f => f.endsWith('.csv') && f.includes('directory'));
    
    let combinedData = [];
    
    for (const f of files) {
        // Extract a clean directory name, e.g. "agricultural_directory_complete.csv" -> "Agricultural"
        let dirName = f.replace('_directory_complete', '').replace('.csv', '').replace(/ \d+$/, '');
        dirName = dirName.charAt(0).toUpperCase() + dirName.slice(1);
        if (dirName.includes('_')) {
            dirName = dirName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        }
        if (dirName.includes('-')) {
            dirName = dirName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        }
        
        console.log(`Processing: ${f} as Directory: ${dirName}`);
        
        const filePath = path.join(parentDir, f);
        const content = fs.readFileSync(filePath, 'utf8');
        
        const parsed = Papa.parse(content, {
            header: true,
            skipEmptyLines: true
        });
        
        if (parsed.errors.length > 0) {
            console.error(`Errors in ${f}:`, parsed.errors);
        }
        
        const validRows = parsed.data.filter(row => row['Company Name'] && row['Company Name'].trim() !== '');
        
        validRows.forEach(row => {
            // Strip embedded newlines/carriage returns from all fields to prevent CSV parsing issues
            for (const key of Object.keys(row)) {
                if (typeof row[key] === 'string') {
                    row[key] = row[key].replace(/[\r\n]+/g, ' ').replace(/\s{2,}/g, ' ').trim();
                }
            }
            row['Directory'] = dirName;
            combinedData.push(row);
        });
    }
    
    console.log(`Total combined rows: ${combinedData.length}`);
    
    const csvOut = Papa.unparse(combinedData);
    fs.writeFileSync(path.join(process.cwd(), 'public', 'data.csv'), csvOut);
    console.log("Saved unified data to public/data.csv");
}

main();
