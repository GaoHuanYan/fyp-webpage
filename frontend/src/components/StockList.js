// import React, { useState, useEffect } from 'react';
// import { Link } from 'react-router-dom';
// import HangSengChart from './HangSengChart';

// // 1. Add a helper function to shuffle an array (Fisher-Yates Shuffle algorithm)
// // This is a very standard and efficient method for random sorting
// const shuffleArray = (array) => {
//   let currentIndex = array.length, randomIndex;

//   // While there remain elements to shuffle...
//   while (currentIndex !== 0) {
//     // Pick a remaining element...
//     randomIndex = Math.floor(Math.random() * currentIndex);
//     currentIndex--;

//     // And swap it with the current element.
//     [array[currentIndex], array[randomIndex]] = [
//       array[randomIndex], array[currentIndex]];
//   }

//   return array;
// };

// function StockList() {
//   const [stocks, setStocks] = useState([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     fetch('/api/stocks')
//       .then(res => res.json())
//       .then(data => {
//         // 2. After fetching the data, call this function to shuffle the full stock list
//         const shuffledStocks = shuffleArray(data);
        
//         // 3. Take the first three items from the shuffled array
//         const randomThreeStocks = shuffledStocks.slice(0, 3);
        
//         // 4. Set these three random items into the state, not the entire list
//         setStocks(randomThreeStocks);
        
//         setLoading(false);
//       })
//       .catch(error => {
//         console.error("Failed to fetch stock list:", error);
//         setLoading(false);
//       });
//   }, []);

//   if (loading) {
//     // For a better user experience, we can slightly modify the loading text
//     return <div>Loading featured stocks...</div>;
//   }

//   return (
//     <div className="stock-list-container">
//       <HangSengChart />
      
//       <hr />
      
//       {/* The title can also be modified to be more guiding */}
//       <h2>Or select a featured stock below</h2>
      
//       {/* This part of the JSX code doesn't need to be changed at all, as it automatically renders the content of the state */}
//       <ul>
//         {stocks.map(stock => (
//           <li key={stock.ticker}>
//             <Link to={`/stock/${stock.ticker}`}>
//               {stock.ticker}
//             </Link>
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// }

// export default StockList;


// 文件名: src/components/StockList.js (最终版本)

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import HangSengChart from './HangSengChart'; // 恒生指数图表组件保持不变

// 1. 新增一个帮助函数，用于格式化数字、添加颜色和正负号
const formatChange = (change) => {
  if (change === null || change === undefined) {
    return <span style={{ color: 'gray' }}>N/A</span>;
  }
  const isPositive = change >= 0;
  const color = isPositive ? '#26a69a' : '#ef5350'; // 专业的绿色和红色
  const sign = isPositive ? '+' : '';
  const formattedChange = `${sign}${change.toFixed(2)}%`;

  return <span style={{ color, fontWeight: 'bold' }}>{formattedChange}</span>;
};

function StockList() {
  // 2. 状态变量改名为 topMovers，更清晰
  const [topMovers, setTopMovers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 3. API调用地址从 '/api/stocks' 改为 '/api/top-movers'
    fetch('/api/top-movers')
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to fetch top movers data from the server.');
        }
        return res.json();
      })
      .then(data => {
        // 4. 直接将获取到的10条数据存入状态，不再需要随机筛选
        setTopMovers(data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Fetch error:", error);
        setError(error.message);
        setLoading(false);
      });
  }, []); // 空依赖数组确保只在组件加载时运行一次

  // 用于渲染列表内容的函数，包含加载、错误和成功状态
  const renderContent = () => {
    if (loading) {
      return <div>Loading AI Predicted Top 10 Movers...</div>;
    }
    if (error) {
      return <div style={{ color: '#ef5350' }}>Error: {error}</div>;
    }
    if (topMovers.length === 0) {
      return <div>No prediction data available for today. Please run the prediction script.</div>;
    }
    return (
      // 5. 渲染一个新的、更专业的列表
      <ul className="top-movers-list">
        {topMovers.map(stock => (
          <li key={stock.ticker}>
            <Link to={`/stock/${stock.ticker}`}>
              <span className="ticker-name">{stock.ticker}</span>
              <span className="ticker-change">{formatChange(stock.change_percent)}</span>
            </Link>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="stock-list-container">
      <HangSengChart />
      <hr />
      {/* 6. 修改标题，突出AI预测的特点 */}
      <h2>AI Predicted Top 10 Movers for Next Trading Day</h2>
      {renderContent()}
    </div>
  );
}

export default StockList;