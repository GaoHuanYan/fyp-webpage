import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import HangSengChart from './HangSengChart';

// 1. Add a helper function to shuffle an array (Fisher-Yates Shuffle algorithm)
// This is a very standard and efficient method for random sorting
const shuffleArray = (array) => {
  let currentIndex = array.length, randomIndex;

  // While there remain elements to shuffle...
  while (currentIndex !== 0) {
    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    // And swap it with the current element.
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex], array[currentIndex]];
  }

  return array;
};

function StockList() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/stocks')
      .then(res => res.json())
      .then(data => {
        // 2. After fetching the data, call this function to shuffle the full stock list
        const shuffledStocks = shuffleArray(data);
        
        // 3. Take the first three items from the shuffled array
        const randomThreeStocks = shuffledStocks.slice(0, 3);
        
        // 4. Set these three random items into the state, not the entire list
        setStocks(randomThreeStocks);
        
        setLoading(false);
      })
      .catch(error => {
        console.error("Failed to fetch stock list:", error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    // For a better user experience, we can slightly modify the loading text
    return <div>Loading featured stocks...</div>;
  }

  return (
    <div className="stock-list-container">
      <HangSengChart />
      
      <hr />
      
      {/* The title can also be modified to be more guiding */}
      <h2>Or select a featured stock below</h2>
      
      {/* This part of the JSX code doesn't need to be changed at all, as it automatically renders the content of the state */}
      <ul>
        {stocks.map(stock => (
          <li key={stock.ticker}>
            <Link to={`/stock/${stock.ticker}`}>
              {stock.ticker}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default StockList;