import React, { useState } from 'react'; // Import useState
import { Routes, Route, useNavigate } from 'react-router-dom'; // Import useNavigate
import StockList from './components/StockList';
import StockDetails from './components/StockDetails';
import './App.css';

function App() {
  // Move the state and logic for the search bar here
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const handleSearch = () => {
    if (searchTerm.trim()) {
      navigate(`/stock/${searchTerm.trim().toUpperCase()}`);
      setSearchTerm(''); // Optional: Clear the input box after searching
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        {/* 4. Create a new top bar container for the title and search bar */}
        <div className="header-top-bar">
          <h1 className="main-title">Hong Kong Stock Market Prediction Lookup Helper</h1>
          
          {/* 5. Place the search bar's JSX here */}
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

        {/* The page content controlled by the routes will be displayed below the top bar */}
        <Routes>
          <Route path="/" element={<StockList />} />
          <Route path="/stock/:ticker" element={<StockDetails />} />
        </Routes>
      </header>
    </div>
  );
}

export default App;