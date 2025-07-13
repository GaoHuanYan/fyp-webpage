// // // StockList.js 

// // import React, { useState, useEffect } from 'react';
// // import { Link, useNavigate } from 'react-router-dom';

// // function StockList() {
// //   const [stocks, setStocks] = useState([]);
// //   const [loading, setLoading] = useState(true);
// //   const [searchTerm, setSearchTerm] = useState('');
// //   const navigate = useNavigate();

// //   useEffect(() => {
// //     fetch('/api/stocks')
// //       .then(res => res.json())
// //       .then(data => {
// //         setStocks(data);
// //         setLoading(false);
// //       })
// //       .catch(error => {
// //         console.error("Failed to fetch stock list:", error);
// //         setLoading(false);
// //       });
// //   }, []);

// //   const handleSearch = () => {
// //     if (searchTerm.trim()) {
// //       // Ensure the path is /stock/
// //       navigate(`/stock/${searchTerm.trim().toUpperCase()}`);
// //     }
// //   };

// //   const handleKeyPress = (event) => {
// //     if (event.key === 'Enter') {
// //       handleSearch();
// //     }
// //   };

// //   if (loading) {
// //     return <div>Loading stock list...</div>;
// //   }

// //   return (
// //     <div style={{ textAlign: 'center' }}>
// //       <div style={{ margin: '20px 0' }}>
// //         <h2>Search for a Stock</h2>
// //         <input
// //           type="text"
// //           placeholder="Enter stock ticker (e.g., TSLA)"
// //           value={searchTerm}
// //           onChange={(e) => setSearchTerm(e.target.value)}
// //           onKeyPress={handleKeyPress}
// //           style={{ padding: '10px', fontSize: '16px', width: '250px', borderRadius: '5px', border: '1px solid #ccc' }}
// //         />
// //         <button 
// //           onClick={handleSearch}
// //           style={{ padding: '10px 20px', fontSize: '16px', marginLeft: '10px', cursor: 'pointer', borderRadius: '5px' }}
// //         >
// //           Search
// //         </button>
// //       </div>
// //       <hr style={{width: '50%', margin: '30px auto'}} />
// //       <h2>Or select a stock below</h2>
// //       <ul style={{ listStyle: 'none', padding: 0 }}>
// //         {stocks.map(stock => (
// //           <li key={stock.ticker} style={{ margin: '15px 0' }}>
// //             {/* Ensure the path is also /stock/ here */}
// //             <Link 
// //               to={`/stock/${stock.ticker}`} 
// //               style={{ 
// //                 color: '#61dafb', 
// //                 fontSize: '18px', 
// //                 textDecoration: 'none',
// //                 padding: '10px 20px',
// //                 border: '1px solid #61dafb',
// //                 borderRadius: '5px',
// //                 display: 'inline-block',
// //                 width: '200px'
// //               }}
// //             >
// //               {stock.ticker}
// //             </Link>
// //           </li>
// //         ))}
// //       </ul>
// //     </div>
// //   );
// // }

// // export default StockList;

// // src/components/StockList.js

// import React, { useState, useEffect } from 'react';
// import { Link } from 'react-router-dom';
// import HangSengChart from './HangSengChart'; // <-- 1. 导入新的图表组件

// // 注意：我们已经移除了 useNavigate, useState for searchTerm, handleSearch, 和 handleKeyPress
// // 因为这些逻辑现在由 App.js 处理

// function StockList() {
//   const [stocks, setStocks] = useState([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     fetch('/api/stocks')
//       .then(res => res.json())
//       .then(data => {
//         setStocks(data);
//         setLoading(false);
//       })
//       .catch(error => {
//         console.error("Failed to fetch stock list:", error);
//         setLoading(false);
//       });
//   }, []);

//   if (loading) {
//     return <div>Loading stock list...</div>;
//   }

//   // 2. 移除了整个搜索框的 JSX
//   return (
//     <div className="stock-list-container">
//       {/* 3. 在列表上方添加恒生指数图表 */}
//       <HangSengChart />
      
//       <hr />
      
//       <h2>Or select a stock below</h2>
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
// src/components/StockList.js

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import HangSengChart from './HangSengChart';

// 1. 新增一个辅助函数来随机打乱数组 (Fisher-Yates Shuffle 算法)
// 这是一个非常标准且高效的随机排序方法
const shuffleArray = (array) => {
  let currentIndex = array.length, randomIndex;

  // 当还剩下元素可以打乱时...
  while (currentIndex !== 0) {
    // 随机挑选一个剩下的元素...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    // 并与当前元素交换
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
        // 2. 在获取到数据后，调用这个函数来打乱完整的股票列表
        const shuffledStocks = shuffleArray(data);
        
        // 3. 从打乱后的数组中取出前三项
        const randomThreeStocks = shuffledStocks.slice(0, 3);
        
        // 4. 将这随机的三项设置到 state 中，而不是整个列表
        setStocks(randomThreeStocks);
        
        setLoading(false);
      })
      .catch(error => {
        console.error("Failed to fetch stock list:", error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    // 为了更好的用户体验，可以稍微修改加载文本
    return <div>Loading featured stocks...</div>;
  }

  return (
    <div className="stock-list-container">
      <HangSengChart />
      
      <hr />
      
      {/* 标题也可以相应修改，更具引导性 */}
      <h2>Or select a featured stock below</h2>
      
      {/* 这部分 JSX 代码完全不需要改变，因为它会自动渲染 state 中的内容 */}
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