import fs from 'fs';
import Papa from 'papaparse';

const content = fs.readFileSync('public/data.csv', 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

const foodCompanies = new Set();
const foodServicesCompanies = new Set();

parsed.data.forEach(row => {
    if (!row['Company Name']) return;
    const name = row['Company Name'].trim().toUpperCase();
    if (row['Directory'] === 'Food') {
        foodCompanies.add(name);
    } else if (row['Directory'] === 'Food Services') {
        foodServicesCompanies.add(name);
    }
});

const common = [];
for (const company of foodCompanies) {
    if (foodServicesCompanies.has(company)) {
        common.push(company);
    }
}

let out = `Food companies total: ${foodCompanies.size}\n`;
out += `Food Services companies total: ${foodServicesCompanies.size}\n`;
out += `Common companies: ${common.length}\n`;
if (common.length > 0) {
    out += 'List of common companies:\n';
    common.forEach(c => out += ' - ' + c + '\n');
}

fs.writeFileSync('overlap.txt', out);
console.log('Done writing overlap.txt');
