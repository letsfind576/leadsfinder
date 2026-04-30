import fs from 'fs';
import Papa from 'papaparse';

const content = fs.readFileSync('public/data.csv', 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

const foodMatches = parsed.data.filter(r => r.Directory && r.Directory.startsWith('Food'));
const uniqueDirs = new Set(foodMatches.map(r => r.Directory));
console.log('Unique directories starting with Food:', Array.from(uniqueDirs));

for (const dir of uniqueDirs) {
    const count = parsed.data.filter(r => r.Directory === dir).length;
    console.log(`Directory '${dir}' has ${count} rows.`);
}
