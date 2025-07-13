
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom'; 
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';

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

function StockDetails() {
    const { ticker } = useParams();
    // Component State
    const [chartData, setChartData] = useState(null);
    const [news, setNews] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isNewsExpanded, setIsNewsExpanded] = useState(false);

    // State for the AI analysis feature
    const [historicalData, setHistoricalData] = useState(null);
    const [aiSummary, setAiSummary] = useState('');
    const [isAiLoading, setIsAiLoading] = useState(true);

    const toggleNews = () => setIsNewsExpanded(!isNewsExpanded);

    // useEffect Hook: Fetches main stock data (history, predictions, news)
    useEffect(() => {
        // <-- Core Change: Use async/await for consistent style and improved error handling
        async function fetchStockData() {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`/api/stocks/${ticker}`);
                // Always try to parse JSON, regardless of success
                const result = await response.json(); 

                // If the HTTP response status is not OK (e.g., 404, 500), 
                // throw the error message provided by the backend.
                if (!response.ok) {
                    throw new Error(result.error || `Server error: ${response.status}`);
                }

                // --- Logic for successfully fetched data ---
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
                // Save historical data to trigger the AI analysis fetch
                setHistoricalData(result.history); 

            } catch (err) {
                console.error(`Failed to fetch stock details for ${ticker}:`, err);
                // Set the captured, more specific message to the error state
                setError(err.message); 
            } finally {
                setLoading(false);
            }
        }
        
        fetchStockData();
    }, [ticker]);

    // useEffect Hook: Fetches the AI summary (this logic is solid and needs no major changes)
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

    // --- Render Logic ---
    if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading data for {ticker}...</div>;

    // <-- Core Change: Use the new, more user-friendly error display component
    if (error) {
        return (
            <div className="error-container">
                <div className="error-icon">⚠️</div>
                <h2>Could not load stock data</h2>
                <p className="error-message">{error}</p>
                <Link to="/" className="home-button">
                    Back to Home
                </Link>
            </div>
        );
    }

    // Render logic for when data is successfully fetched
    return (
        <div className="stock-details-page-container">
            <h2 className="stock-details-subtitle">
                {ticker} Historical Prices and Model Predictions
            </h2>
            
            <div className="details-container">
                <div className="chart-container">
                    {chartData ? (
                        <div style={{ position: 'relative', height: '500px' }}>
                             <Chart type='line' data={chartData} options={chartOptions} />
                        </div>
                    ) : ( <div>Preparing chart...</div> )}
                </div>
                
                <div className="side-panel">
                    {/* AI Analysis Card */}
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
                            <p className="ai-summary-text">{aiSummary}</p>
                        )}
                    </div>

                    {/* Related News Card */}
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
        </div>
    );
}

export default StockDetails;