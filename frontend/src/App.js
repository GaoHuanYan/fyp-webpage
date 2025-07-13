// // App.js 

// import React from 'react';
// import { Routes, Route } from 'react-router-dom';
// import StockList from './components/StockList';
// import StockDetails from './components/StockDetails';
// import './App.css';

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <h1>Hong Kong Stock Market Prediction Lookup Helper</h1>
//         <Routes>
//           <Route path="/" element={<StockList />} />
//           {/* Ensure the path here is /stock/ not /stocks/ */}
//           <Route path="/stock/:ticker" element={<StockDetails />} />
//         </Routes>
//       </header>
//     </div>
//   );
// }

// export default App;


// src/App.js

import React, { useState } from 'react'; // <-- 1. 导入 useState
import { Routes, Route, useNavigate } from 'react-router-dom'; // <-- 2. 导入 useNavigate
import StockList from './components/StockList';
import StockDetails from './components/StockDetails';
import './App.css';

function App() {
  // 3. 将搜索框的状态和逻辑移到这里
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const handleSearch = () => {
    if (searchTerm.trim()) {
      navigate(`/stock/${searchTerm.trim().toUpperCase()}`);
      setSearchTerm(''); // 可选：搜索后清空输入框
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
        {/* 4. 创建一个新的顶栏容器，用于放置标题和搜索框 */}
        <div className="header-top-bar">
          <h1 className="main-title">Hong Kong Stock Market Prediction Lookup Helper</h1>
          
          {/* 5. 将搜索框的 JSX 放在这里 */}
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

        {/* 路由控制的页面内容将显示在顶栏下方 */}
        <Routes>
          <Route path="/" element={<StockList />} />
          <Route path="/stock/:ticker" element={<StockDetails />} />
        </Routes>
      </header>
    </div>
  );
}

export default App;