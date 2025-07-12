// File Path: frontend/src/components/StockDetails.js (Final, Cleaned & Translated Version)

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// --- This section remains unchanged ---
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
        title: { display: true, text: `Price Trends and Predictions`, color: 'white' }
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

    // useEffect hook to fetch the main stock data (history, predictions, news)
    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`/api/stocks/${ticker}`)
            .then(response => {
                if (!response.ok) return Promise.reject(`Server error: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.error) return Promise.reject(data.error);

                const historyDataset = {
                    label: 'Close Price',
                    data: data.history.map(item => ({ x: item.date, y: item.close })),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    tension: 0.1
                };
                const predictionDatasets = Object.keys(data.predictions).map((modelName, index) => ({
                    label: `${modelName} Prediction`,
                    data: data.predictions[modelName].map(p => ({ x: p.date, y: p.price })),
                    borderColor: modelColors[index % modelColors.length],
                    backgroundColor: modelColors[index % modelColors.length],
                    showLine: false, pointRadius: 6, pointHoverRadius: 8,
                }));
                setChartData({ datasets: [historyDataset, ...predictionDatasets] });
                setNews(data.news || []);

                // Crucial Step: Save historical data to trigger the AI analysis fetch
                setHistoricalData(data.history);
            })
            .catch(err => {
                console.error(`Failed to fetch stock details for ${ticker}:`, err);
                setError(typeof err === 'string' ? err : 'An unknown error occurred.');
            })
            .finally(() => setLoading(false));
    }, [ticker]);

    // useEffect hook to fetch the AI summary after historical data is available
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
                setAiSummary('Could not load AI analysis summary.'); // Translated error message
            } finally {
                setIsAiLoading(false);
            }
        }
        fetchAiSummary();
    }, [historicalData, ticker]);

    if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading data for {ticker}...</div>;
    if (error) return <div style={{ color: '#ff4d4d', textAlign: 'center', marginTop: '50px' }}>Error: {error}</div>;

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
                            {/* Using the correct SVG icon instead of an emoji */}
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                <path d="M3 17L9 11L13 15L21 7V13H23V4H14V6H19.59L13 12.59L9 8.59L3 14.59V17Z"/>
                            </svg>
                            AI Analysis
                        </h3>
                        {isAiLoading ? (
                            <p>Generating analysis...</p> // Translated loading message
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