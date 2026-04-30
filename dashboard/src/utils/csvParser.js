import Papa from 'papaparse';

// Extract city from physical address explicitly
function determineCity(address) {
  if (!address) return 'Unknown';
  const a = address.toUpperCase();
  if (a.includes('LAHORE')) return 'Lahore';
  if (a.includes('KASUR')) return 'Kasur';
  if (a.includes('SHEIKHUPURA')) return 'Sheikhupura';
  if (a.includes('FAISALABAD')) return 'Faisalabad';
  if (a.includes('MULTAN')) return 'Multan';
  if (a.includes('KARACHI')) return 'Karachi';
  return 'Other';
}

function analyzeCompanyProfile(row) {
  const name = (row['Company Name'] || '').toUpperCase();
  const sector = ((row['Business Sector(s)'] || '') + ' ' + (row['Business Speciality'] || '')).toUpperCase();
  
  // 1. Analyze True Energy Intensity based on manufacturing profile
  // Heavy machinery: Spinning (Motors), Weaving (Looms), Dyeing/Finishing (Boilers)
  if (sector.includes('SPINNING') || sector.includes('WEAVING') || sector.includes('DYEING') || 
      sector.includes('PROCESSING') || sector.includes('SYNTHETIC') || name.includes('MILLS')) {
    row['Energy Intensity'] = 'High';
  } 
  // Medium scale: Garment factories, Hosiery, Knitting (hundreds of sewing machines)
  else if (sector.includes('GARMENTS') || sector.includes('APPAREL') || sector.includes('HOSIERY') || 
           sector.includes('KNITWEAR') || sector.includes('STITCHING')) {
    row['Energy Intensity'] = 'Medium';
  } 
  // Low scale: Trading, Retail, small boutiques, embroidery services
  else if (sector.includes('TRADER') || sector.includes('TRADING') || sector.includes('EMBROIDERY') || 
           sector.includes('LACE') || sector.includes('BOUTIQUE') || sector.includes('SHOP') || 
           name.includes('TRADERS') || name.includes('STORE')) {
    row['Energy Intensity'] = 'Low';
  } else {
    row['Energy Intensity'] = 'Medium'; // Conservative median Default
  }
  
  // 2. Real ICP (Ideal Customer Profile) Fit Score Engine
  // High scores indicate a high likelihood of budgets for energy optimization projects.
  // Large corporate scales (Ltd, Corporations, Mills)
  if (name.includes('LTD') || name.includes('LIMITED') || name.includes('MILLS') || name.includes('CORPORATION') || name.includes('GROUP')) {
    row['ICP Fit Score'] = 5;
    row['Tier'] = 'Tier 1';
  } 
  // Established Industries
  else if (name.includes('INDUSTRIES') || name.includes('INTERNATIONAL') || name.includes('FABRICS') || name.includes('SONS')) {
    row['ICP Fit Score'] = 4;
    row['Tier'] = 'Tier 2';
  } 
  // Medium Enterprises
  else if (name.includes('ENTERPRISES') || name.includes('TEXTILES') || name.includes('BROTHERS')) {
    row['ICP Fit Score'] = 3;
    row['Tier'] = 'Tier 3';
  } 
  // Very Small retail/solo business (Unlikely to need heavy enterprise products)
  else if (name.includes('TRADERS') || name.includes('SHOP') || name.includes('BOUTIQUE') || name.includes('TAILERS')) {
    row['ICP Fit Score'] = 1;
    row['Tier'] = 'Tier 3';
  } else {
    row['ICP Fit Score'] = 2; // Default for unlabeled small proprietors
    row['Tier'] = 'Tier 3';
  }
  
  // 3. Attach Location
  row['City'] = determineCity(row['Address']);
  return row;
}

export const parseCSV = async (csvPath) => {
  return new Promise((resolve, reject) => {
    Papa.parse(csvPath, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const enhancedData = results.data.map(analyzeCompanyProfile);
        resolve(enhancedData);
      },
      error: (error) => {
        reject(error);
      }
    });
  });
};
