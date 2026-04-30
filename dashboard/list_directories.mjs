import fs from 'fs';
import Papa from 'papaparse';

const content = fs.readFileSync('public/data.csv', 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

const directories = new Set();
parsed.data.forEach(row => directories.add(row['Directory']));
console.log('Available directories:');
console.log(Array.from(directories).join(', '));
