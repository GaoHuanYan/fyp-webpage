import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import StockList from './components/StockList';
import StockDetails from './components/StockDetails';
import './App.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const handleSearch = () => {
    if (searchTerm.trim()) {
      navigate(`/stock/${searchTerm.trim().toUpperCase()}`);
      setSearchTerm('');
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  // The main structure remains the same, we just add a footer at the end.
  return (
    // The className "App" is important for our CSS styling
    <div className="App">
      {/* The header contains the main content and routes */}
      <header className="App-header">
        <div className="header-top-bar">
          <h1 className="main-title">Hong Kong Stock Market Prediction Lookup Helper</h1>
          
          <div className="search-container-top-right">
            <input
              type="text"
              placeholder="Enter stock ticker..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button onClick={handleSearch}>
              Search
            </button>
          </div>
        </div>

        <Routes>
          <Route path="/" element={<StockList />} />
          <Route path="/stock/:ticker" element={<StockDetails />} />
        </Routes>
      </header>

      {/* === STEP 1: Add the footer element here, outside the main header === */}
      <footer className="app-footer">
        <p>
          Disclaimer: All predictions, analysis, and data are for informational purposes only and should not be considered as financial advice. Please invest with caution and conduct your own research.
        </p>
      </footer>
    </div>
  );
}

export default App;