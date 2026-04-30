import fs from 'fs';
import Papa from 'papaparse';

const content = fs.readFileSync('public/data.csv', 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

const dirs = new Set();
parsed.data.forEach(row => dirs.add(row['Directory']));
for (const dir of dirs) {
    if (dir && dir.includes('Food')) {
        console.log(`Found string: "${dir}" (length: ${dir.length})`);
    }
}
