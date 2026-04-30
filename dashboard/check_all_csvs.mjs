import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

const parentDir = path.join(process.cwd(), '..');
const files = fs.readdirSync(parentDir).filter(f => f.endsWith('.csv') && f.includes('directory'));

for (const f of files) {
    const filePath = path.join(parentDir, f);
    const content = fs.readFileSync(filePath, 'utf8');
    const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });
    
    if (parsed.data.length === 0) continue;
    
    // Check if Company Name exists
    const row = parsed.data[0];
    const hasCompany = !!row['Company Name'];
    
    if (!hasCompany) {
        console.log(`\nFile ${f} is missing 'Company Name'. Keys:`, Object.keys(row).map(k => JSON.stringify(k)).join(', '));
    }
}
