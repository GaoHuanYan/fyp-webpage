
// // // import React, { useState, useEffect } from 'react';
// // // import { useParams, Link } from 'react-router-dom'; 
// // // import { Chart } from 'react-chartjs-2';
// // // import {
// // //   Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
// // //   Title, Tooltip, Legend, TimeScale
// // // } from 'chart.js';
// // // import 'chartjs-adapter-date-fns';

// // // ChartJS.register(
// // //   CategoryScale, LinearScale, PointElement, LineElement,
// // //   Title, Tooltip, Legend, TimeScale
// // // );
// // // const modelColors = [
// // //     'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
// // // ];
// // // const chartOptions = {
// // //     responsive: true,
// // //     maintainAspectRatio: false,
// // //     plugins: {
// // //         legend: { position: 'top', labels: { color: 'white' } },
// // //         title: { display: true, text: `Price Trends and Model Predictions`, color: 'white' }
// // //     },
// // //     scales: {
// // //         x: {
// // //             type: 'time',
// // //             time: { unit: 'day', tooltipFormat: 'yyyy-MM-dd' },
// // //             title: { display: true, text: 'Date', color: 'white' },
// // //             ticks: { color: 'white' },
// // //             grid: { color: 'rgba(255, 255, 255, 0.1)' }
// // //         },
// // //         y: {
// // //             title: { display: true, text: 'Price', color: 'white' },
// // //             ticks: { color: 'white' },
// // //             grid: { color: 'rgba(255, 255, 255, 0.1)' }
// // //         }
// // //     }
// // // };

// // // function StockDetails() {
// // //     const { ticker } = useParams();
// // //     // Component State
// // //     const [chartData, setChartData] = useState(null);
// // //     const [news, setNews] = useState([]);
// // //     const [error, setError] = useState(null);
// // //     const [loading, setLoading] = useState(true);
// // //     const [isNewsExpanded, setIsNewsExpanded] = useState(false);

// // //     // State for the AI analysis feature
// // //     const [historicalData, setHistoricalData] = useState(null);
// // //     const [aiSummary, setAiSummary] = useState('');
// // //     const [isAiLoading, setIsAiLoading] = useState(true);

// // //     const toggleNews = () => setIsNewsExpanded(!isNewsExpanded);

// // //     // useEffect Hook: Fetches main stock data (history, predictions, news)
// // //     useEffect(() => {
// // //         // <-- Core Change: Use async/await for consistent style and improved error handling
// // //         async function fetchStockData() {
// // //             setLoading(true);
// // //             setError(null);
// // //             try {
// // //                 const response = await fetch(`/api/stocks/${ticker}`);
// // //                 // Always try to parse JSON, regardless of success
// // //                 const result = await response.json(); 

// // //                 // If the HTTP response status is not OK (e.g., 404, 500), 
// // //                 // throw the error message provided by the backend.
// // //                 if (!response.ok) {
// // //                     throw new Error(result.error || `Server error: ${response.status}`);
// // //                 }

// // //                 // --- Logic for successfully fetched data ---
// // //                 const historyDataset = {
// // //                     label: 'Close Price',
// // //                     data: result.history.map(item => ({ x: item.date, y: item.close })),
// // //                     borderColor: 'rgb(75, 192, 192)',
// // //                     backgroundColor: 'rgba(75, 192, 192, 0.5)',
// // //                     tension: 0.1
// // //                 };
// // //                 const predictionDatasets = Object.keys(result.predictions).map((modelName, index) => ({
// // //                     label: `${modelName} Prediction`,
// // //                     data: result.predictions[modelName].map(p => ({ x: p.date, y: p.price })),
// // //                     borderColor: modelColors[index % modelColors.length],
// // //                     backgroundColor: modelColors[index % modelColors.length],
// // //                     showLine: false, pointRadius: 6, pointHoverRadius: 8,
// // //                 }));
// // //                 setChartData({ datasets: [historyDataset, ...predictionDatasets] });
// // //                 setNews(result.news || []);
// // //                 // Save historical data to trigger the AI analysis fetch
// // //                 setHistoricalData(result.history); 

// // //             } catch (err) {
// // //                 console.error(`Failed to fetch stock details for ${ticker}:`, err);
// // //                 // Set the captured, more specific message to the error state
// // //                 setError(err.message); 
// // //             } finally {
// // //                 setLoading(false);
// // //             }
// // //         }
        
// // //         fetchStockData();
// // //     }, [ticker]);

// // //     // useEffect Hook: Fetches the AI summary (this logic is solid and needs no major changes)
// // //     useEffect(() => {
// // //         if (!historicalData || historicalData.length === 0) return;

// // //         async function fetchAiSummary() {
// // //             setIsAiLoading(true);
// // //             try {
// // //                 const response = await fetch('/api/summarize', {
// // //                     method: 'POST',
// // //                     headers: { 'Content-Type': 'application/json' },
// // //                     body: JSON.stringify({ historicalData, ticker })
// // //                 });
// // //                 const result = await response.json();
// // //                 if (!response.ok) {
// // //                     throw new Error(result.error || 'Failed to get AI summary.');
// // //                 }
// // //                 setAiSummary(result.summary);
// // //             } catch (err) {
// // //                 console.error("AI summary fetch error:", err);
// // //                 setAiSummary('Could not load AI analysis summary.');
// // //             } finally {
// // //                 setIsAiLoading(false);
// // //             }
// // //         }
// // //         fetchAiSummary();
// // //     }, [historicalData, ticker]);

// // //     // --- Render Logic ---
// // //     if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading data for {ticker}...</div>;

// // //     // <-- Core Change: Use the new, more user-friendly error display component
// // //     if (error) {
// // //         return (
// // //             <div className="error-container">
// // //                 <div className="error-icon">⚠️</div>
// // //                 <h2>Could not load stock data</h2>
// // //                 <p className="error-message">{error}</p>
// // //                 <Link to="/" className="home-button">
// // //                     Back to Home
// // //                 </Link>
// // //             </div>
// // //         );
// // //     }

// // //     // Render logic for when data is successfully fetched
// // //     return (
// // //         <div className="stock-details-page-container">
// // //             <h2 className="stock-details-subtitle">
// // //                 {ticker} Historical Prices and Model Predictions
// // //             </h2>
            
// // //             <div className="details-container">
// // //                 <div className="chart-container">
// // //                     {chartData ? (
// // //                         <div style={{ position: 'relative', height: '500px' }}>
// // //                              <Chart type='line' data={chartData} options={chartOptions} />
// // //                         </div>
// // //                     ) : ( <div>Preparing chart...</div> )}
// // //                 </div>
                
// // //                 <div className="side-panel">
// // //                     {/* AI Analysis Card */}
// // //                     <div className="ai-summary-container">
// // //                         <h3 className="ai-summary-header">
// // //                             <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px', verticalAlign: 'bottom' }}>
// // //                                 <path d="M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7ZM12 14C8.13401 14 5 17.134 5 21H19C19 17.134 15.866 14 12 14Z" />
// // //                             </svg>
// // //                             AI Analysis
// // //                         </h3>
// // //                         {isAiLoading ? (
// // //                             <p>Generating analysis...</p>
// // //                         ) : (
// // //                             <p className="ai-summary-text">{aiSummary}</p>
// // //                         )}
// // //                     </div>

// // //                     {/* Related News Card */}
// // //                     <div className="news-container">
// // //                         <h3 onClick={toggleNews} className="news-header">
// // //                             Related News <span>{isNewsExpanded ? '▲' : '▼'}</span>
// // //                         </h3>
// // //                         {isNewsExpanded && (
// // //                             <div className="news-list">
// // //                                 {news.length > 0 ? (
// // //                                     news.map((item, index) => (
// // //                                         <div key={index} className="news-item">
// // //                                             <div className="news-content">
// // //                                                 <h4>{item.title}</h4>
// // //                                                 <p>{item.summary}</p>
// // //                                             </div>
// // //                                             <span className="news-date">{new Date(item.date).toLocaleDateString()}</span>
// // //                                         </div>
// // //                                     ))
// // //                                 ) : ( <p>No related news available.</p> )}
// // //                             </div>
// // //                         )}
// // //                     </div>
// // //                 </div>
// // //             </div>
// // //         </div>
// // //     );
// // // }

// // // export default StockDetails;


// // import React, { useState, useEffect } from 'react';
// // import { useParams, Link } from 'react-router-dom';
// // import { Chart } from 'react-chartjs-2';
// // import {
// //   Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
// //   Title, Tooltip, Legend, TimeScale
// // } from 'chart.js';
// // import 'chartjs-adapter-date-fns';

// // ChartJS.register(
// //   CategoryScale, LinearScale, PointElement, LineElement,
// //   Title, Tooltip, Legend, TimeScale
// // );
// // const modelColors = [
// //     'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
// // ];
// // const chartOptions = {
// //     responsive: true,
// //     maintainAspectRatio: false,
// //     plugins: {
// //         legend: { position: 'top', labels: { color: 'white' } },
// //         title: { display: true, text: `Price Trends and Model Predictions`, color: 'white' }
// //     },
// //     scales: {
// //         x: {
// //             type: 'time',
// //             time: { unit: 'day', tooltipFormat: 'yyyy-MM-dd' },
// //             title: { display: true, text: 'Date', color: 'white' },
// //             ticks: { color: 'white' },
// //             grid: { color: 'rgba(255, 255, 255, 0.1)' }
// //         },
// //         y: {
// //             title: { display: true, text: 'Price', color: 'white' },
// //             ticks: { color: 'white' },
// //             grid: { color: 'rgba(255, 255, 255, 0.1)' }
// //         }
// //     }
// // };

// // function StockDetails() {
// //     const { ticker } = useParams();
// //     // Component State
// //     const [chartData, setChartData] = useState(null);
// //     const [news, setNews] = useState([]);
// //     const [error, setError] = useState(null);
// //     const [loading, setLoading] = useState(true);
// //     const [isNewsExpanded, setIsNewsExpanded] = useState(true); // <-- 设置为默认展开

// //     // State for the AI analysis feature
// //     const [historicalData, setHistoricalData] = useState(null);
// //     const [aiSummary, setAiSummary] = useState('');
// //     const [isAiLoading, setIsAiLoading] = useState(true);

// //     const toggleNews = () => setIsNewsExpanded(!isNewsExpanded);

// //     // useEffect Hook: Fetches main stock data (history, predictions, news)
// //     useEffect(() => {
// //         async function fetchStockData() {
// //             setLoading(true);
// //             setError(null);
// //             try {
// //                 const response = await fetch(`/api/stocks/${ticker}`);
// //                 const result = await response.json(); 
// //                 if (!response.ok) {
// //                     throw new Error(result.error || `Server error: ${response.status}`);
// //                 }
// //                 const historyDataset = {
// //                     label: 'Close Price',
// //                     data: result.history.map(item => ({ x: item.date, y: item.close })),
// //                     borderColor: 'rgb(75, 192, 192)',
// //                     backgroundColor: 'rgba(75, 192, 192, 0.5)',
// //                     tension: 0.1
// //                 };
// //                 const predictionDatasets = Object.keys(result.predictions).map((modelName, index) => ({
// //                     label: `${modelName} Prediction`,
// //                     data: result.predictions[modelName].map(p => ({ x: p.date, y: p.price })),
// //                     borderColor: modelColors[index % modelColors.length],
// //                     backgroundColor: modelColors[index % modelColors.length],
// //                     showLine: false, pointRadius: 6, pointHoverRadius: 8,
// //                 }));
// //                 setChartData({ datasets: [historyDataset, ...predictionDatasets] });
// //                 setNews(result.news || []);
// //                 setHistoricalData(result.history); 
// //             } catch (err) {
// //                 console.error(`Failed to fetch stock details for ${ticker}:`, err);
// //                 setError(err.message); 
// //             } finally {
// //                 setLoading(false);
// //             }
// //         }
// //         fetchStockData();
// //     }, [ticker]);

// //     // useEffect Hook: Fetches the AI summary
// //     useEffect(() => {
// //         if (!historicalData || historicalData.length === 0) return;
// //         async function fetchAiSummary() {
// //             setIsAiLoading(true);
// //             try {
// //                 const response = await fetch('/api/summarize', {
// //                     method: 'POST',
// //                     headers: { 'Content-Type': 'application/json' },
// //                     body: JSON.stringify({ historicalData, ticker })
// //                 });
// //                 const result = await response.json();
// //                 if (!response.ok) {
// //                     throw new Error(result.error || 'Failed to get AI summary.');
// //                 }
// //                 setAiSummary(result.summary);
// //             } catch (err) {
// //                 console.error("AI summary fetch error:", err);
// //                 setAiSummary('Could not load AI analysis summary.');
// //             } finally {
// //                 setIsAiLoading(false);
// //             }
// //         }
// //         fetchAiSummary();
// //     }, [historicalData, ticker]);

// //     if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading data for {ticker}...</div>;
// //     if (error) {
// //         return (
// //             <div className="error-container">
// //                 <div className="error-icon">⚠️</div>
// //                 <h2>Could not load stock data</h2>
// //                 <p className="error-message">{error}</p>
// //                 <Link to="/" className="home-button">Back to Home</Link>
// //             </div>
// //         );
// //     }

// //     return (
// //         <div className="stock-details-page-container">
// //             <h2 className="stock-details-subtitle">
// //                 {ticker} Historical Prices and Model Predictions
// //             </h2>
            
// //             {/* === 容器1: 图表和AI摘要 (双列布局) === */}
// //             <div className="details-container">
// //                 <div className="chart-container">
// //                     {chartData ? (
// //                         <div style={{ position: 'relative', height: '500px' }}>
// //                              <Chart type='line' data={chartData} options={chartOptions} />
// //                         </div>
// //                     ) : ( <div>Preparing chart...</div> )}
// //                 </div>
                
// //                 <div className="side-panel">
// //                     {/* AI Analysis Card - 现在是侧边栏唯一的内容 */}
// //                     <div className="ai-summary-container">
// //                         <h3 className="ai-summary-header">
// //                             <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px', verticalAlign: 'bottom' }}>
// //                                 <path d="M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7ZM12 14C8.13401 14 5 17.134 5 21H19C19 17.134 15.866 14 12 14Z" />
// //                             </svg>
// //                             AI Analysis
// //                         </h3>
// //                         {isAiLoading ? (
// //                             <p>Generating analysis...</p>
// //                         ) : (
// //                             <p className="ai-summary-text">{aiSummary}</p>
// //                         )}
// //                     </div>
// //                     {/* 新闻部分已从这里移除 */}
// //                 </div>
// //             </div>

// //             {/* === 容器2: 相关新闻 (单列，在下方) === */}
// //             <div className="news-section-container"> {/* <-- 新增的包裹容器 */}
// //                 <div className="news-container">
// //                     <h3 onClick={toggleNews} className="news-header">
// //                         Related News <span>{isNewsExpanded ? '▲' : '▼'}</span>
// //                     </h3>
// //                     {isNewsExpanded && (
// //                         <div className="news-list">
// //                             {news.length > 0 ? (
// //                                 news.map((item, index) => (
// //                                     <div key={index} className="news-item">
// //                                         <div className="news-content">
// //                                             <h4>{item.title}</h4>
// //                                             <p>{item.summary}</p>
// //                                         </div>
// //                                         <span className="news-date">{new Date(item.date).toLocaleDateString()}</span>
// //                                     </div>
// //                                 ))
// //                             ) : ( <p>No related news available.</p> )}
// //                         </div>
// //                     )}
// //                 </div>
// //             </div>
// //         </div>
// //     );
// // }

// // export default StockDetails;



// // filename: StockDetails.js
// import React, { useState, useEffect } from 'react';
// import { useParams, Link } from 'react-router-dom';
// import { Chart } from 'react-chartjs-2';
// import {
//   Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
//   Title, Tooltip, Legend, TimeScale
// } from 'chart.js';
// import 'chartjs-adapter-date-fns';

// // --- Chart.js Registration and Options (No Changes) ---
// ChartJS.register(
//   CategoryScale, LinearScale, PointElement, LineElement,
//   Title, Tooltip, Legend, TimeScale
// );
// const modelColors = [
//     'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
// ];
// const chartOptions = {
//     responsive: true,
//     maintainAspectRatio: false,
//     plugins: {
//         legend: { position: 'top', labels: { color: 'white' } },
//         title: { display: true, text: `Price Trends and Model Predictions`, color: 'white' }
//     },
//     scales: {
//         x: {
//             type: 'time',
//             time: { unit: 'day', tooltipFormat: 'yyyy-MM-dd' },
//             title: { display: true, text: 'Date', color: 'white' },
//             ticks: { color: 'white' },
//             grid: { color: 'rgba(255, 255, 255, 0.1)' }
//         },
//         y: {
//             title: { display: true, text: 'Price', color: 'white' },
//             ticks: { color: 'white' },
//             grid: { color: 'rgba(255, 255, 255, 0.1)' }
//         }
//     }
// };

// // ==================================================================
// // ===     CORE CHANGE: NEW COMPONENT TO RENDER AI REPORT         ===
// // ==================================================================
// /**
//  * A component that parses a Markdown-like string from the AI and renders it as styled HTML.
//  * It handles headers (####), bold text (**), and list items (-).
//  */
// const AIAnalysisReport = ({ summary }) => {
//     const renderLine = (line, index) => {
//         // Handle Headers (e.g., #### 1. Core Trend Analysis)
//         if (line.startsWith('####')) {
//             // Remove '####' and trim whitespace
//             const headerText = line.replace(/^#+\s*/, '');
//             return <h4 key={index} className="ai-report-header" dangerouslySetInnerHTML={{ __html: renderBold(headerText) }} />;
//         }
//         // Handle List Items (e.g., - **Overall Trend**:)
//         if (line.startsWith('- ')) {
//             const listItemText = line.substring(2);
//             return <li key={index} dangerouslySetInnerHTML={{ __html: renderBold(listItemText) }} />;
//         }
//         // Handle empty lines by adding some vertical space
//         if (line.trim() === '') {
//             return <div key={index} style={{ height: '10px' }} />;
//         }
//         // Handle any other text as a paragraph
//         return <p key={index} dangerouslySetInnerHTML={{ __html: renderBold(line) }} />;
//     };

//     // Helper function to replace **text** with <strong>text</strong>
//     const renderBold = (text) => {
//         return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
//     };

//     const lines = summary.split('\n');
//     const reportElements = lines.map(renderLine);

//     return <div className="ai-report-content">{reportElements}</div>;
// };


// function StockDetails() {
//     const { ticker } = useParams();
//     // --- State Management (No Changes) ---
//     const [chartData, setChartData] = useState(null);
//     const [news, setNews] = useState([]);
//     const [error, setError] = useState(null);
//     const [loading, setLoading] = useState(true);
//     const [isNewsExpanded, setIsNewsExpanded] = useState(true);
//     const [historicalData, setHistoricalData] = useState(null);
//     const [aiSummary, setAiSummary] = useState('');
//     const [isAiLoading, setIsAiLoading] = useState(true);

//     const toggleNews = () => setIsNewsExpanded(!isNewsExpanded);

//     // --- Data Fetching useEffect Hooks (No Changes) ---
//     useEffect(() => {
//         async function fetchStockData() {
//             setLoading(true);
//             setError(null);
//             try {
//                 const response = await fetch(`/api/stocks/${ticker}`);
//                 const result = await response.json(); 
//                 if (!response.ok) {
//                     throw new Error(result.error || `Server error: ${response.status}`);
//                 }
//                 const historyDataset = {
//                     label: 'Close Price',
//                     data: result.history.map(item => ({ x: item.date, y: item.close })),
//                     borderColor: 'rgb(75, 192, 192)',
//                     backgroundColor: 'rgba(75, 192, 192, 0.5)',
//                     tension: 0.1
//                 };
//                 const predictionDatasets = Object.keys(result.predictions).map((modelName, index) => ({
//                     label: `${modelName} Prediction`,
//                     data: result.predictions[modelName].map(p => ({ x: p.date, y: p.price })),
//                     borderColor: modelColors[index % modelColors.length],
//                     backgroundColor: modelColors[index % modelColors.length],
//                     showLine: false, pointRadius: 6, pointHoverRadius: 8,
//                 }));
//                 setChartData({ datasets: [historyDataset, ...predictionDatasets] });
//                 setNews(result.news || []);
//                 setHistoricalData(result.history); 
//             } catch (err) {
//                 console.error(`Failed to fetch stock details for ${ticker}:`, err);
//                 setError(err.message); 
//             } finally {
//                 setLoading(false);
//             }
//         }
//         fetchStockData();
//     }, [ticker]);

//     useEffect(() => {
//         if (!historicalData || historicalData.length === 0) return;
//         async function fetchAiSummary() {
//             setIsAiLoading(true);
//             try {
//                 const response = await fetch('/api/summarize', {
//                     method: 'POST',
//                     headers: { 'Content-Type': 'application/json' },
//                     body: JSON.stringify({ historicalData, ticker })
//                 });
//                 const result = await response.json();
//                 if (!response.ok) {
//                     throw new Error(result.error || 'Failed to get AI summary.');
//                 }
//                 setAiSummary(result.summary);
//             } catch (err) {
//                 console.error("AI summary fetch error:", err);
//                 setAiSummary('Could not load AI analysis summary.');
//             } finally {
//                 setIsAiLoading(false);
//             }
//         }
//         fetchAiSummary();
//     }, [historicalData, ticker]);

//     // --- Render Logic (Minor Changes) ---
//     if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading data for {ticker}...</div>;
//     if (error) {
//         return (
//             <div className="error-container">
//                 <div className="error-icon">⚠️</div>
//                 <h2>Could not load stock data</h2>
//                 <p className="error-message">{error}</p>
//                 <Link to="/" className="home-button">Back to Home</Link>
//             </div>
//         );
//     }

//     return (
//         <div className="stock-details-page-container">
//             <h2 className="stock-details-subtitle">
//                 {ticker} Historical Prices and Model Predictions
//             </h2>
            
//             <div className="details-container">
//                 <div className="chart-container">
//                     {chartData ? (
//                         <div style={{ position: 'relative', height: '500px' }}>
//                              <Chart type='line' data={chartData} options={chartOptions} />
//                         </div>
//                     ) : ( <div>Preparing chart...</div> )}
//                 </div>
                
//                 <div className="side-panel">
//                     <div className="ai-summary-container">
//                         <h3 className="ai-summary-header">
//                             <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px', verticalAlign: 'bottom' }}>
//                                 <path d="M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7ZM12 14C8.13401 14 5 17.134 5 21H19C19 17.134 15.866 14 12 14Z" />
//                             </svg>
//                             AI Analysis
//                         </h3>
//                         {isAiLoading ? (
//                             <p>Generating analysis...</p>
//                         ) : (
//                             // ==================================================================
//                             // ===   CORE CHANGE: USE THE NEW REPORT RENDERER COMPONENT       ===
//                             // ==================================================================
//                             <AIAnalysisReport summary={aiSummary} />
//                         )}
//                     </div>
//                 </div>
//             </div>

//             <div className="news-section-container">
//                 <div className="news-container">
//                     <h3 onClick={toggleNews} className="news-header">
//                         Related News <span>{isNewsExpanded ? '▲' : '▼'}</span>
//                     </h3>
//                     {isNewsExpanded && (
//                         <div className="news-list">
//                             {news.length > 0 ? (
//                                 news.map((item, index) => (
//                                     <div key={index} className="news-item">
//                                         <div className="news-content">
//                                             <h4>{item.title}</h4>
//                                             <p>{item.summary}</p>
//                                         </div>
//                                         <span className="news-date">{new Date(item.date).toLocaleDateString()}</span>
//                                     </div>
//                                 ))
//                             ) : ( <p>No related news available.</p> )}
//                         </div>
//                     )}
//                 </div>
//             </div>
//         </div>
//     );
// }

// export default StockDetails;


// filename: StockDetails.js

import React, { useState, useEffect, useRef } from 'react'; // <-- 1. 引入 useRef
import { useParams, Link } from 'react-router-dom';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// --- Chart.js Registration and Options (无变化) ---
ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, TimeScale
);
const modelColors = [
    'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
];
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { position: 'top', labels: { color: 'white' } },
        title: { display: true, text: `Price Trends and Model Predictions`, color: 'white' }
    },
    scales: {
        x: {
            type: 'time',
            time: { unit: 'day', tooltipFormat: 'yyyy-MM-dd' },
            title: { display: true, text: 'Date', color: 'white' },
            ticks: { color: 'white' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        y: {
            title: { display: true, text: 'Price', color: 'white' },
            ticks: { color: 'white' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' }
        }
    }
};

const AIAnalysisReport = ({ summary }) => {
    const renderLine = (line, index) => {
        if (line.startsWith('####')) {
            const headerText = line.replace(/^#+\s*/, '');
            return <h4 key={index} className="ai-report-header" dangerouslySetInnerHTML={{ __html: renderBold(headerText) }} />;
        }
        if (line.startsWith('- ')) {
            const listItemText = line.substring(2);
            return <li key={index} dangerouslySetInnerHTML={{ __html: renderBold(listItemText) }} />;
        }
        if (line.trim() === '') {
            return <div key={index} style={{ height: '10px' }} />;
        }
        return <p key={index} dangerouslySetInnerHTML={{ __html: renderBold(line) }} />;
    };

    const renderBold = (text) => {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    };

    const lines = summary.split('\n');
    const reportElements = lines.map(renderLine);

    return <div className="ai-report-content">{reportElements}</div>;
};


function StockDetails() {
    const { ticker } = useParams();
    const [chartData, setChartData] = useState(null);
    const [news, setNews] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isNewsExpanded, setIsNewsExpanded] = useState(true);
    const [historicalData, setHistoricalData] = useState(null);
    const [aiSummary, setAiSummary] = useState('');
    const [isAiLoading, setIsAiLoading] = useState(true);

    // ==================================================================
    // ===                 核心修改区域 (开始)                      ===
    // ==================================================================

    // 2. 创建一个 ref 来引用图表容器 DOM 元素
    const chartContainerRef = useRef(null);
    // 3. 创建一个 state 来存储计算出的面板高度
    const [panelHeight, setPanelHeight] = useState(0);

    // 4. 使用 useEffect 在图表渲染完成后获取其高度
    useEffect(() => {
      // 当数据加载完成，且图表容器的 ref 已经绑定到 DOM 上时
      if (!loading && chartContainerRef.current) {
        // 获取图表容器的实际渲染高度
        const height = chartContainerRef.current.offsetHeight;
        // 更新 state，这个 state 将被用于设置 AI 面板的高度
        setPanelHeight(height);
      }
    }, [loading]); // 这个 effect 会在 loading 状态改变时运行

    // ==================================================================
    // ===                 核心修改区域 (结束)                      ===
    // ==================================================================

    const toggleNews = () => setIsNewsExpanded(!isNewsExpanded);

    // --- 数据获取的 useEffect (无变化) ---
    useEffect(() => {
        async function fetchStockData() {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`/api/stocks/${ticker}`);
                const result = await response.json(); 
                if (!response.ok) {
                    throw new Error(result.error || `Server error: ${response.status}`);
                }
                const historyDataset = {
                    label: 'Close Price',
                    data: result.history.map(item => ({ x: item.date, y: item.close })),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    tension: 0.1
                };
                const predictionDatasets = Object.keys(result.predictions).map((modelName, index) => ({
                    label: `${modelName} Prediction`,
                    data: result.predictions[modelName].map(p => ({ x: p.date, y: p.price })),
                    borderColor: modelColors[index % modelColors.length],
                    backgroundColor: modelColors[index % modelColors.length],
                    showLine: false, pointRadius: 6, pointHoverRadius: 8,
                }));
                setChartData({ datasets: [historyDataset, ...predictionDatasets] });
                setNews(result.news || []);
                setHistoricalData(result.history); 
            } catch (err) {
                console.error(`Failed to fetch stock details for ${ticker}:`, err);
                setError(err.message); 
            } finally {
                setLoading(false);
            }
        }
        fetchStockData();
    }, [ticker]);

    useEffect(() => {
        if (!historicalData || historicalData.length === 0) return;
        async function fetchAiSummary() {
            setIsAiLoading(true);
            try {
                const response = await fetch('/api/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ historicalData, ticker })
                });
                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.error || 'Failed to get AI summary.');
                }
                setAiSummary(result.summary);
            } catch (err) {
                console.error("AI summary fetch error:", err);
                setAiSummary('Could not load AI analysis summary.');
            } finally {
                setIsAiLoading(false);
            }
        }
        fetchAiSummary();
    }, [historicalData, ticker]);

    // --- Render Logic (有修改) ---
    if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading data for {ticker}...</div>;
    if (error) {
        return (
            <div className="error-container">
                <div className="error-icon">⚠️</div>
                <h2>Could not load stock data</h2>
                <p className="error-message">{error}</p>
                <Link to="/" className="home-button">Back to Home</Link>
            </div>
        );
    }

    return (
        <div className="stock-details-page-container">
            <h2 className="stock-details-subtitle">
                {ticker} Historical Prices and Model Predictions
            </h2>
            
            <div className="details-container">
                {/* 5. 将 ref 绑定到图表容器上 */}
                <div className="chart-container" ref={chartContainerRef}>
                    {chartData ? (
                        <div style={{ position: 'relative', height: '500px' }}>
                             <Chart type='line' data={chartData} options={chartOptions} />
                        </div>
                    ) : ( <div>Preparing chart...</div> )}
                </div>
                
                {/* 6. 将计算出的高度应用到 side-panel 上 */}
                <div className="side-panel" style={{ height: panelHeight > 0 ? `${panelHeight}px` : 'auto' }}>
                    <div className="ai-summary-container">
                        <h3 className="ai-summary-header">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px', verticalAlign: 'bottom' }}>
                                <path d="M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7ZM12 14C8.13401 14 5 17.134 5 21H19C19 17.134 15.866 14 12 14Z" />
                            </svg>
                            AI Analysis
                        </h3>
                        {isAiLoading ? (
                            <p>Generating analysis...</p>
                        ) : (
                            <AIAnalysisReport summary={aiSummary} />
                        )}
                    </div>
                </div>
            </div>

            <div className="news-section-container">
                <div className="news-container">
                    <h3 onClick={toggleNews} className="news-header">
                        Related News <span>{isNewsExpanded ? '▲' : '▼'}</span>
                    </h3>
                    {isNewsExpanded && (
                        <div className="news-list">
                            {news.length > 0 ? (
                                news.map((item, index) => (
                                    <div key={index} className="news-item">
                                        <div className="news-content">
                                            <h4>{item.title}</h4>
                                            <p>{item.summary}</p>
                                        </div>
                                        <span className="news-date">{new Date(item.date).toLocaleDateString()}</span>
                                    </div>
                                ))
                            ) : ( <p>No related news available.</p> )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default StockDetails;