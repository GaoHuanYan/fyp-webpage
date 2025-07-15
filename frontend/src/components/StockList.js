import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import HangSengChart from './HangSengChart'; 
import './../App.css'; 

/**
 * Helper function: Formats the percentage change.
 * @param {number} change - The change value.
 * @returns {JSX.Element} - Returns a JSX element with color and sign.
 */
const formatChange = (change) => {
  // Handle the edge case where data is null or undefined.
  if (change === null || change === undefined) {
    return <span style={{ color: 'gray' }}>N/A</span>;
  }
  
  // Determine if the change is positive or negative.
  const isPositive = parseFloat(change) >= 0;
  // Define professional colors for gain (green) and loss (red).
  const color = isPositive ? '#26a69a' : '#ef5350';
  // Add a '+' sign for positive numbers.
  const sign = isPositive ? '+' : '';
  // Format as a percentage string with two decimal places.
  const formattedChange = `${sign}${parseFloat(change).toFixed(2)}%`;

  return <span style={{ color, fontWeight: 'bold' }}>{formattedChange}</span>;
};

function StockList() {
  // Define component state
  const [topMovers, setTopMovers] = useState([]); // Stores the Top 10 stock data
  const [loading, setLoading] = useState(true);   // Loading state
  const [error, setError] = useState(null);       // Error state

  // Use useEffect to fetch data from the backend API when the component mounts.
  useEffect(() => {
    fetch('/api/top-movers')
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to fetch top movers data from the server.');
        }
        return res.json();
      })
      .then(data => {
        setTopMovers(data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Fetch error:", error);
        setError(error.message);
        setLoading(false);
      });
  }, []); // The empty dependency array ensures this effect runs only once.

  // Render different content based on the component's state (loading, error, success).
  const renderContent = () => {
    if (loading) {
      return <div className="loading-message">Loading AI Predicted Top 10 Movers...</div>;
    }
    if (error) {
      return <div className="error-message" style={{ color: '#ef5350' }}>Error: {error}</div>;
    }
    if (topMovers.length === 0) {
      return <div className="info-message">No prediction data available for today. Please run the prediction script.</div>;
    }
    
    // After successfully fetching the data, render the list.
    // The layout of this ul list is controlled by the 'top-movers-list' class in App.css (CSS Grid).
    return (
      <ul className="top-movers-list">
        {topMovers.map((stock, index) => (
          <li key={stock.ticker}>
            <Link to={`/stock/${stock.ticker}`}>
              <span className="ticker-name">
                
                {/* === This is the modified core logic === */}
                {/* Only display the crown if it's the first item and the change is positive. */}
                {index === 0 && stock.change_percent >= 0 && <span className="crown-icon">👑</span>}
                
                {stock.ticker}
              </span>
              <span className="ticker-change">
                {/* Use the helper function to format the displayed percentage change. */}
                {formatChange(stock.change_percent)}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    );
  };

  // The final return content of the component.
  return (
    <div className="stock-list-container">
      <HangSengChart />
      <hr className="divider"/> 
      
      <h2 className="list-title">AI Predicted Top 10 Movers for Next Trading Day</h2>
      
      {/* Call the content rendering function. */}
      {renderContent()}
    </div>
  );
}

export default StockList;