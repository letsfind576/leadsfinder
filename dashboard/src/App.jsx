import React, { useState, useEffect, useMemo } from 'react';
import { Download, RefreshCw, Printer, Moon, Sun, Search, Factory, MapPin, Loader2, Star } from 'lucide-react';
import Papa from 'papaparse';
import { parseCSV } from './utils/csvParser';
import './index.css';

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDirectory, setSelectedDirectory] = useState('All Directories');
  const [selectedSector, setSelectedSector] = useState('All Sectors');
  const [selectedCity, setSelectedCity] = useState('All Cities');
  const [selectedEnergy, setSelectedEnergy] = useState('Any');
  const [selectedICP, setSelectedICP] = useState('Any Score');
  const [selectedSpeciality, setSelectedSpeciality] = useState('All Specialities');
  
  // Theme
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 50;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load the newly combined data.csv
      let parsedData;
      try {
        parsedData = await parseCSV('/data.csv');
      } catch (e) {
        console.error('Failed to load /data.csv', e);
        parsedData = [];
      }
      
      // Filter out empty rows
      const validData = parsedData.filter(row => row['Company Name'] && row['Company Name'].trim() !== '');
      setData(validData);
    } catch (err) {
      console.error('Failed to parse CSV', err);
    } finally {
      setLoading(false);
    }
  };

  // Derive unique categories for dropdowns
  const directories = useMemo(() => ['All Directories', ...Array.from(new Set(data.map(d => d['Directory']).filter(Boolean))).sort()], [data]);
  const sectors = useMemo(() => ['All Sectors', ...Array.from(new Set(data.map(d => d['Business Sector(s)']).filter(Boolean))).sort()], [data]);
  const specialities = useMemo(() => ['All Specialities', ...Array.from(new Set(data.map(d => d['Business Speciality']).filter(Boolean))).sort()], [data]);
  const cities = useMemo(() => ['All Cities', ...Array.from(new Set(data.map(d => d['City']).filter(Boolean))).sort()], [data]);

  const energyOptions = ['Any', 'High', 'Medium', 'Low'];
  const icpOptions = ['Any Score', '1', '2', '3', '4', '5'];

  // Apply filters
  const filteredData = useMemo(() => {
    return data.filter(row => {
      const mDir = selectedDirectory === 'All Directories' || row['Directory'] === selectedDirectory;
      const mSect = selectedSector === 'All Sectors' || row['Business Sector(s)'] === selectedSector;
      const mSpec = selectedSpeciality === 'All Specialities' || row['Business Speciality'] === selectedSpeciality;
      const mCity = selectedCity === 'All Cities' || row['City'] === selectedCity;
      const mEnergy = selectedEnergy === 'Any' || row['Energy Intensity'] === selectedEnergy;
      const mICP = selectedICP === 'Any Score' || String(row['ICP Fit Score']) === selectedICP;
      
      const term = searchQuery.toLowerCase();
      const mSearch = term === '' || 
        (row['Company Name']?.toLowerCase().includes(term)) ||
        (row['Address']?.toLowerCase().includes(term)) ||
        (row['Name']?.toLowerCase().includes(term));
      
      return mDir && mSect && mSpec && mCity && mEnergy && mICP && mSearch;
    });
  }, [data, selectedDirectory, selectedSector, selectedSpeciality, selectedCity, selectedEnergy, selectedICP, searchQuery]);

  // Aggregate Metrics
  const tier1Count = useMemo(() => filteredData.filter(d => d['Tier'] === 'Tier 1').length, [filteredData]);
  const tier2Count = useMemo(() => filteredData.filter(d => d['Tier'] === 'Tier 2').length, [filteredData]);

  // Pagination bounds
  const totalPages = Math.ceil(filteredData.length / rowsPerPage);
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * rowsPerPage;
    return filteredData.slice(start, start + rowsPerPage);
  }, [filteredData, currentPage]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedDirectory, selectedSector, selectedSpeciality, selectedCity, selectedEnergy, selectedICP]);

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedDirectory('All Directories');
    setSelectedSector('All Sectors');
    setSelectedSpeciality('All Specialities');
    setSelectedCity('All Cities');
    setSelectedEnergy('Any');
    setSelectedICP('Any Score');
  };

  const handleToggleTheme = () => {
    setIsDarkMode(prev => {
      const newMode = !prev;
      if (newMode) document.documentElement.setAttribute('data-theme', 'dark');
      else document.documentElement.removeAttribute('data-theme');
      return newMode;
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadCSV = () => {
    if (filteredData.length === 0) return;
    const csvString = Papa.unparse(filteredData);
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'pakistan_industries_export.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderStars = (score) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
        stars.push(
            <Star 
              key={i} 
              size={14} 
              fill={i <= score ? "#F59E0B" : "transparent"} 
              color={i <= score ? "#F59E0B" : "#D1D5DB"}
              style={{ marginRight: '2px' }}
            />
        );
    }
    return <div style={{ display: 'flex', alignItems: 'center' }}>{stars}</div>;
  };

  const getEnergyBadgeClass = (intensity) => {
      if (intensity === 'High') return 'badge badge-red';
      if (intensity === 'Medium') return 'badge badge-orange';
      if (intensity === 'Low') return 'badge badge-green';
      return 'badge badge-blue';
  };

  if (loading) {
    return (
      <div className="dashboard-layout loading-container">
        <Loader2 size={48} className="lucide-spin" style={{ animation: 'spin 2s linear infinite' }} />
        <h2>Loading Industry Data...</h2>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      {/* Header */}
      <header className="header">
        <div>
          <div className="header-title">
            <Factory size={24} /> Pakistan Industries Finder
          </div>
          <div className="header-meta">
            Enfo.ai Sales Prospecting Tool - Identify ideal customers for energy optimization.
          </div>
        </div>
        <div className="header-actions">
          <button className="icon-btn" onClick={loadData} title="Refresh Data"><RefreshCw size={18} /></button>
          <button className="icon-btn" onClick={handleDownloadCSV} title="Download CSV"><Download size={18} /></button>
          <button className="icon-btn" onClick={handlePrint} title="Print"><Printer size={18} /></button>
          <button className="icon-btn" onClick={handleToggleTheme} title="Toggle Theme">
            {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      <div className="dashboard-main">
        {/* Sidebar */}
        <aside className="sidebar">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MapPin size={18} /> Filters
          </h3>
          
          <div className="filter-group">
            <label className="filter-label">Search</label>
            <div style={{ position: 'relative' }}>
              <input 
                type="text" 
                placeholder="Name, sector, etc..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ paddingLeft: '32px' }}
              />
              <Search size={16} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Directory</label>
            <select value={selectedDirectory} onChange={(e) => setSelectedDirectory(e.target.value)}>
              {directories.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Sector</label>
            <select value={selectedSector} onChange={(e) => setSelectedSector(e.target.value)}>
              {sectors.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="filter-group">
             <label className="filter-label">Speciality</label>
             <select value={selectedSpeciality} onChange={(e) => setSelectedSpeciality(e.target.value)}>
               {specialities.map(s => <option key={s} value={s}>{s}</option>)}
             </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">City</label>
            <select value={selectedCity} onChange={(e) => setSelectedCity(e.target.value)}>
              {cities.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="filter-group">
             <label className="filter-label">Energy Intensity</label>
             <select value={selectedEnergy} onChange={(e) => setSelectedEnergy(e.target.value)}>
               {energyOptions.map(s => <option key={s} value={s}>{s}</option>)}
             </select>
          </div>

          <div className="filter-group">
             <label className="filter-label">Minimum ICP Fit Score</label>
             <select value={selectedICP} onChange={(e) => setSelectedICP(e.target.value)}>
               {icpOptions.map(s => <option key={s} value={s}>{s}</option>)}
             </select>
          </div>

          <div style={{ marginTop: 'auto' }}>
            <button className="btn-primary" onClick={resetFilters}>Reset Filters</button>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="main-content">
          {/* Metrics Row */}
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-title">Total Industries</span>
              <span className="metric-value highlight">{filteredData.length.toLocaleString()}</span>
            </div>
            <div className="metric-card">
              <span className="metric-title">Tier 1 Prospects (Score 5 <Star size={14} fill="#F59E0B" color="#F59E0B" />)</span>
              <span className="metric-value">{tier1Count.toLocaleString()}</span>
            </div>
            <div className="metric-card">
              <span className="metric-title">Tier 2 Prospects (Score 4)</span>
              <span className="metric-value blue">{tier2Count.toLocaleString()}</span>
            </div>
          </div>

          {/* DataTable */}
          <div className="data-table-card">
            <div className="table-header-info">
              <span>Showing {filteredData.length > 0 ? (currentPage - 1) * rowsPerPage + 1 : 0} - {Math.min(currentPage * rowsPerPage, filteredData.length)} of {filteredData.length.toLocaleString()} rows</span>
            </div>
            
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Company Name</th>
                    <th>Directory</th>
                    <th>City</th>
                    <th>Email</th>
                    <th>Phone Number</th>
                    <th>Address</th>
                    <th>Business Sector</th>
                    <th>Energy Intensity</th>
                    <th>ICP Fit</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((row, i) => (
                    <tr key={i}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{row['Company Name'] || '-'}</div>
                      </td>
                      <td>
                        <span className="badge badge-purple">{row['Directory'] || '-'}</span>
                      </td>
                      <td>
                        <div style={{ fontWeight: 500, color: 'var(--text-main)' }}>{row['City'] || '-'}</div>
                      </td>
                      <td>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{row['Email'] || '-'}</div>
                      </td>
                      <td>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{row['Ph (Off)'] || '-'}</div>
                      </td>
                      <td style={{ maxWidth: '250px', whiteSpace: 'normal', lineHeight: '1.4' }}>{row['Address'] || '-'}</td>
                      <td>
                        <span className="badge badge-blue">{row['Business Sector(s)'] || '-'}</span>
                      </td>
                      <td>
                        <span className={getEnergyBadgeClass(row['Energy Intensity'])}>{row['Energy Intensity'] || '-'}</span>
                      </td>
                      <td>
                        {renderStars(row['ICP Fit Score'])}
                      </td>
                    </tr>
                  ))}
                  {paginatedData.length === 0 && (
                    <tr>
                      <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                        No results match your current filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="pagination">
              <button 
                className="pagination-btn" 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                Page {currentPage} of {totalPages || 1}
              </span>
              <button 
                className="pagination-btn" 
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages || totalPages === 0}
              >
                Next
              </button>
            </div>
          </div>
        </main>
      </div>
      
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
