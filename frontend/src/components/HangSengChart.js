// // src/components/HangSengChart.js

// import React, { useState, useEffect } from 'react';
// import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

// const formatDate = (tickItem) => {
//     // 例如，将 '2024-05-20' 格式化为 '05-20'
//     return tickItem.slice(5);
// };

// function HangSengChart() {
//     const [chartData, setChartData] = useState([]);
//     const [loading, setLoading] = useState(true);
//     const [error, setError] = useState(null);

//     useEffect(() => {
//         fetch('/api/stocks/^HSI')
//             .then(res => {
//                 if (!res.ok) {
//                     throw new Error('Network response was not ok');
//                 }
//                 return res.json();
//             })
//             .then(data => {
//                 const formattedData = data.history.map(item => ({
//                     date: item.date,
//                     price: item.close,
//                 }));
//                 setChartData(formattedData);
//                 setLoading(false);
//             })
//             .catch(err => {
//                 console.error("Failed to fetch Hang Seng Index data:", err);
//                 setError("Could not load index data.");
//                 setLoading(false);
//             });
//     }, []); 
//     if (loading) {
//         return <div className="hsi-chart-container placeholder">Loading Index Chart...</div>;
//     }

//     if (error) {
//         return <div className="hsi-chart-container placeholder">{error}</div>;
//     }

//     return (
//         <div className="hsi-chart-container">
//             <h3>Hang Seng Index Trend</h3>
//             <ResponsiveContainer width="100%" height={250}>
//                 <LineChart data={chartData}>
//                     <CartesianGrid strokeDasharray="3 3" stroke="#444" />
//                     <XAxis 
//                         dataKey="date" 
//                         tickFormatter={formatDate} 
//                         stroke="#ccc"
//                         fontSize={12}
//                     />
//                     <YAxis 
//                         domain={['dataMin - 2', 'dataMax + 2']} 
//                         stroke="#ccc"
//                         fontSize={12}
//                     />
//                     <Tooltip 
//                         contentStyle={{ backgroundColor: '#282c34', border: '1px solid #555' }}
//                         labelStyle={{ color: '#fff' }}
//                     />
//                     <Line 
//                         type="monotone" 
//                         dataKey="price" 
//                         stroke="#61dafb" 
//                         strokeWidth={2} 
//                         dot={false} 
//                     />
//                 </LineChart>
//             </ResponsiveContainer>
//         </div>
//     );
// }

// export default HangSengChart;


// src/components/HangSengChart.js (FIXED VERSION)

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Brush } from 'recharts';

const formatDate = (tickItem) => {
    return tickItem.slice(5);
};

function HangSengChart() {
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [brushIndexes, setBrushIndexes] = useState({ startIndex: 0, endIndex: 0 });

    useEffect(() => {
        fetch('/api/stocks/^HSI')
            .then(res => {
                if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then(data => {
                const formattedData = data.history
                    .map(item => ({
                        date: item.date,
                        price: parseFloat(item.close), 
                    }))
                    .filter(item => !isNaN(item.price));

                setChartData(formattedData);

                const defaultLookback = 60;
                const dataLength = formattedData.length;
                const startIndex = Math.max(0, dataLength - defaultLookback);
                setBrushIndexes({ startIndex: startIndex, endIndex: dataLength - 1 });

                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch Hang Seng Index data:", err);
                setError("Could not load index data.");
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <div className="hsi-chart-container placeholder">Loading Index Chart...</div>;
    }

    if (error) {
        return <div className="hsi-chart-container placeholder">{error}</div>;
    }

    return (
        <div className="hsi-chart-container">
            <h3>Hang Seng Index Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart 
                    data={chartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                    <XAxis 
                        dataKey="date" 
                        tickFormatter={formatDate} 
                        stroke="#ccc"
                        fontSize={12}
                    />
                    <YAxis 
                        domain={['dataMin - 1', 'dataMax + 1']} 
                        stroke="#ccc"
                        fontSize={12}
                        tickFormatter={(value) => value.toFixed(2)} 
                        allowDecimals={true}
                    />
                    <Tooltip 
                        contentStyle={{ backgroundColor: '#282c34', border: '1px solid #555' }}
                        labelStyle={{ color: '#fff' }}
                        formatter={(value) => typeof value === 'number' ? value.toFixed(2) : value}
                    />
                    <Line 
                        type="monotone" 
                        dataKey="price" 
                        stroke="#61dafb" 
                        strokeWidth={2} 
                        dot={false} 
                    />
                    
                    {chartData.length > 0 && (
                        <Brush
                            dataKey="date"
                            height={30}
                            stroke="#61dafb"
                            fill="#3a3f44"
                            startIndex={brushIndexes.startIndex}
                            endIndex={brushIndexes.endIndex}
                            tickFormatter={formatDate}
                        >
                            {/* --- 核心修复点在这里！--- */}
                            {/* 为内部的迷你图表也提供 data 属性 */}
                            <LineChart data={chartData}>
                                <Line type="monotone" dataKey="price" stroke="#61dafb" dot={false} />
                            </LineChart>
                        </Brush>
                    )}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

export default HangSengChart;


