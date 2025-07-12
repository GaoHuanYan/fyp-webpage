// 文件路径: backend/server.js

const express = require('express');
const cors = require('cors');
require('dotenv').config();
const OpenAI = require('openai');

const app = express();
const PORT = 3001; // AI后端运行在 3001 端口

// --- 中间件 ---
app.use(cors());
app.use(express.json());

// 初始化 DeepSeek 客户端
const deepseek = new OpenAI({
    baseURL: 'https://api.deepseek.com',
    apiKey: process.env.DEEPSEEK_API_KEY,
});

// --- API 端点 ---
app.post('/api/summarize', async (req, res) => {
    try {
        const { historicalData, ticker } = req.body;
        if (!historicalData || historicalData.length === 0 || !ticker) {
            return res.status(400).json({ error: 'Ticker and historical data are required.' });
        }

        // 我们只发送最近30天的数据给AI，以节省token并聚焦于近期表现
        const recentData = historicalData.slice(-30);

        const prompt = `
            你是一位精明且简洁的金融分析师。
            请根据以下关于股票代码 "${ticker}" 的历史价格数据，用中文提供一个2-3句话的摘要，总结其近期表现和关键趋势。
            请重点关注总体方向、重要的波峰和波谷。不要说任何“你好”或“当然”之类的开场白，直接给出分析。

            数据 (JSON格式, 最近30天):
            ${JSON.stringify(recentData)}
        `;

        console.log(`[AI-Server] Received request for ${ticker}. Contacting DeepSeek API...`);

        const completion = await deepseek.chat.completions.create({
            model: "deepseek-chat",
            messages: [
                { role: "system", content: "你是一位精明的金融分析师，使用中文进行回复。" },
                { role: "user", content: prompt }
            ],
            temperature: 0.5,
        });

        const summary = completion.choices[0].message.content;
        console.log(`[AI-Server] Successfully received summary for ${ticker}.`);
        
        res.json({ summary });

    } catch (error) {
        console.error('[AI-Server] Error contacting DeepSeek API:', error);
        res.status(500).json({ error: 'Failed to generate AI summary.' });
    }
});

// --- 启动服务器 ---
app.listen(PORT, () => {
    console.log(`✅ AI Backend server is running on http://localhost:${PORT}`);
});