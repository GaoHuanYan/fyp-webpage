// StockList.js 

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function StockList() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/api/stocks')
      .then(res => res.json())
      .then(data => {
        setStocks(data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Failed to fetch stock list:", error);
        setLoading(false);
      });
  }, []);

  const handleSearch = () => {
    if (searchTerm.trim()) {
      // Ensure the path is /stock/
      navigate(`/stock/${searchTerm.trim().toUpperCase()}`);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  if (loading) {
    return <div>Loading stock list...</div>;
  }

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ margin: '20px 0' }}>
        <h2>Search for a Stock</h2>
        <input
          type="text"
          placeholder="Enter stock ticker (e.g., TSLA)"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={handleKeyPress}
          style={{ padding: '10px', fontSize: '16px', width: '250px', borderRadius: '5px', border: '1px solid #ccc' }}
        />
        <button 
          onClick={handleSearch}
          style={{ padding: '10px 20px', fontSize: '16px', marginLeft: '10px', cursor: 'pointer', borderRadius: '5px' }}
        >
          Search
        </button>
      </div>
      <hr style={{width: '50%', margin: '30px auto'}} />
      <h2>Or select a stock below</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {stocks.map(stock => (
          <li key={stock.ticker} style={{ margin: '15px 0' }}>
            {/* Ensure the path is also /stock/ here */}
            <Link 
              to={`/stock/${stock.ticker}`} 
              style={{ 
                color: '#61dafb', 
                fontSize: '24px', 
                textDecoration: 'none',
                padding: '10px 20px',
                border: '1px solid #61dafb',
                borderRadius: '5px',
                display: 'inline-block',
                width: '200px'
              }}
            >
              {stock.ticker}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default StockList;