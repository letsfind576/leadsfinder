import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

const parentDir = path.join(process.cwd(), '..');
const f = 'food_services_directory_complete.csv';
const filePath = path.join(parentDir, f);
const content = fs.readFileSync(filePath, 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

console.log(`Total parsed rows: ${parsed.data.length}`);
const validRows = parsed.data.filter(row => row['Company Name'] && row['Company Name'].trim() !== '');
console.log(`Total valid rows: ${validRows.length}`);
if (validRows.length > 0) {
    console.log(`First valid Company Name: "${validRows[0]['Company Name']}"`);
}
