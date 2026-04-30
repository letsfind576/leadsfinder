import fs from 'fs';
import Papa from 'papaparse';

const content = fs.readFileSync('../food_services_directory_complete.csv', 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

console.log('Headers parsed:', parsed.meta.fields);
if (parsed.data.length > 0) {
    console.log('First row keys:', Object.keys(parsed.data[0]));
    console.log('First row Company Name:', parsed.data[0]['Company Name']);
}
