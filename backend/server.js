const express = require('express');
const cors = require('cors');
require('dotenv').config();
const OpenAI = require('openai');

const app = express();
const PORT = 3001; // AI backend runs on port 3001

// --- Middleware ---
app.use(cors());
app.use(express.json());

// Initialize DeepSeek Client
const deepseek = new OpenAI({
    baseURL: 'https://api.deepseek.com',
    apiKey: process.env.DEEPSEEK_API_KEY,
});

// --- API Endpoints ---
app.post('/api/summarize', async (req, res) => {
    try {
        const { historicalData, ticker } = req.body;
        if (!historicalData || historicalData.length === 0 || !ticker) {
            return res.status(400).json({ error: 'Ticker and historical data are required.' });
        }

        // We only send the last 30 days of data to the AI to save tokens and focus on recent performance
        const recentData = historicalData.slice(-30);

        const prompt = `
            You are a sharp and concise financial analyst.
            Based on the following historical price data for the stock ticker "${ticker}", provide a 2-3 sentence summary in English that covers its recent performance and key trends.
            Focus on the overall direction, significant peaks, and troughs. Do not use any introductory phrases like "Hello" or "Of course." Provide the analysis directly.

            Data (JSON format, last 30 days):
            ${JSON.stringify(recentData)}
        `;

        console.log(`[AI-Server] Received request for ${ticker}. Contacting DeepSeek API...`);

        const completion = await deepseek.chat.completions.create({
            model: "deepseek-chat",
            messages: [
                { role: "system", content: "You are a sharp financial analyst who responds in English." },
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

// --- Start Server ---
app.listen(PORT, () => {
    console.log(`✅ AI Backend server is running on http://localhost:${PORT}`);
});