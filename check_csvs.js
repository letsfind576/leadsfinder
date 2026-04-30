const fs = require('fs');

const files = fs.readdirSync('.').filter(f => f.endsWith('.csv') && f.includes('directory'));
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    const firstLine = content.split('\n')[0].replace(/\r/g, '').trim();
    console.log(`${f} -> ${firstLine}`);
}
