const fs = require('fs');
const Papa = require('papaparse');

const content = fs.readFileSync('public/data.csv', 'utf8');
const parsed = Papa.parse(content, { header: true, skipEmptyLines: true });

const foodCompanies = new Set();
const foodServicesCompanies = new Set();

parsed.data.forEach(row => {
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

console.log(`Food companies total: ${foodCompanies.size}`);
console.log(`Food Services companies total: ${foodServicesCompanies.size}`);
console.log(`Common companies: ${common.length}`);
if (common.length > 0) {
    console.log('List of common companies:');
    common.slice(0, 10).forEach(c => console.log(' - ' + c));
    if (common.length > 10) console.log('...and more.');
}
