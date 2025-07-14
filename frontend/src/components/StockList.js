// // 引入React核心库和路由组件
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// 引入子组件和样式文件
import HangSengChart from './HangSengChart'; // 恒生指数图表组件
import './../App.css'; // 引入我们修改过的CSS，它包含了Grid布局样式

/**
 * 帮助函数：格式化涨跌幅百分比
 * @param {number} change - 涨跌幅数值
 * @returns {JSX.Element} - 返回带颜色和正负号的JSX元素
 */
const formatChange = (change) => {
  // 处理数据不存在的边缘情况
  if (change === null || change === undefined) {
    return <span style={{ color: 'gray' }}>N/A</span>;
  }
  
  // 判断涨跌
  const isPositive = parseFloat(change) >= 0;
  // 定义专业的涨（绿）跌（红）颜色
  const color = isPositive ? '#26a69a' : '#ef5350';
  // 为正数添加 '+' 号
  const sign = isPositive ? '+' : '';
  // 格式化为带两位小数的百分比字符串
  const formattedChange = `${sign}${parseFloat(change).toFixed(2)}%`;

  return <span style={{ color, fontWeight: 'bold' }}>{formattedChange}</span>;
};

function StockList() {
  // 定义组件状态
  const [topMovers, setTopMovers] = useState([]); // 存储Top 10股票数据
  const [loading, setLoading] = useState(true);   // 加载状态
  const [error, setError] = useState(null);       // 错误状态

  // 使用useEffect在组件加载时从后端API获取数据
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
  }, []); // 空依赖数组确保此effect仅运行一次

  // 根据组件状态（加载、错误、成功）渲染不同的内容
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
    
    // 成功获取数据后，渲染列表
    // 这个ul列表的布局由 App.css 中的 'top-movers-list' 类控制 (CSS Grid)
    return (
      <ul className="top-movers-list">
        {topMovers.map((stock, index) => (
          <li key={stock.ticker}>
            <Link to={`/stock/${stock.ticker}`}>
              <span className="ticker-name">
                
                {/* === 核心修改点 === */}
                {/* 如果是第一个元素 (index === 0)，则显示王冠图标 */}
                {index === 0 && <span className="crown-icon">👑</span>}
                
                {stock.ticker}
              </span>
              <span className="ticker-change">
                {/* 使用帮助函数来格式化显示的涨跌幅 */}
                {formatChange(stock.change_percent)}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    );
  };

  // 组件的最终返回内容
  return (
    <div className="stock-list-container">
      <HangSengChart />
      <hr className="divider"/> {/* 建议给hr添加一个类名，方便在CSS中单独设置样式 */}
      
      <h2 className="list-title">AI Predicted Top 10 Movers for Next Trading Day</h2>
      
      {/* 调用内容渲染函数 */}
      {renderContent()}
    </div>
  );
}

export default StockList;