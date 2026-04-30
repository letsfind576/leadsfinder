import fs from 'fs';
import Papa from 'papaparse';

const content = fs.readFileSync('public/data.csv', 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

const foodServices = parsed.data.filter(r => r.Directory === 'Food Services');
console.log(`Found ${foodServices.length} raw Food Services rows.`);
if (foodServices.length > 0) {
    console.log('Sample row:');
    console.log(JSON.stringify(foodServices[0], null, 2));
}
