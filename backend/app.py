# File Path: backend/app.py (Final, Cleaned & Translated Version)

import sqlite3
import os
from flask import Flask, jsonify, request # 'request' is needed to get data from POST
from flask_cors import CORS
from collections import defaultdict
from dotenv import load_dotenv # To load .env files
from openai import OpenAI # To import the OpenAI library

# --- Initialization and Configuration ---
load_dotenv() # Load environment variables from the .env file at startup

app = Flask(__name__)
CORS(app)

DATABASE = 'stock_data.db'

# --- Initialize the DeepSeek Client ---
# It will automatically read DEEPSEEK_API_KEY from the environment
try:
    deepseek_client = OpenAI(
        base_url="https://api.deepseek.com",
        api_key=os.getenv('DEEPSEEK_API_KEY')
    )
    print("DeepSeek client initialized successfully.")
except Exception as e:
    print(f"Warning: Failed to initialize DeepSeek client: {e}")
    deepseek_client = None


# --- Database Connection (Unchanged) ---
def get_db_connection():
    """Creates a reusable database connection."""
    conn = sqlite3.connect(DATABASE)
    # This allows accessing columns by name, like a dictionary.
    conn.row_factory = sqlite3.Row 
    return conn

# --- Existing API Endpoints (Unchanged) ---
@app.route('/api/stocks')
def get_stocks():
    """Get the list of all available stock tickers from the database."""
    conn = get_db_connection()
    tickers_data = conn.execute('SELECT DISTINCT ticker FROM stock_prices').fetchall()
    conn.close()
    stocks_list = [{'ticker': row['ticker'], 'name': f"{row['ticker']} Inc."} for row in tickers_data]
    return jsonify(stocks_list)

@app.route('/api/stocks/<ticker>')
def get_stock_detail(ticker):
    """Get stock details, predictions, and the latest news list."""
    conn = get_db_connection()
    history = conn.execute('SELECT date, open, high, low, close, volume FROM stock_prices WHERE ticker = ? ORDER BY date ASC', (ticker,)).fetchall()
    predictions_query = conn.execute('SELECT model_name, date, predicted_price FROM stock_predictions WHERE ticker = ? ORDER BY date ASC', (ticker,)).fetchall()
    news_query = conn.execute('SELECT date, title, summary FROM stock_news WHERE ticker = ? ORDER BY date DESC', (ticker,)).fetchall()
    conn.close()

    if not history:
        return jsonify({'error': f'Data for ticker {ticker} not found in the database.'}), 404

    predictions_by_model = defaultdict(list)
    for row in predictions_query:
        predictions_by_model[row['model_name']].append({'date': row['date'], 'price': row['predicted_price']})

    data = {
        'ticker': ticker,
        'name': f'{ticker} Inc.',
        'history': [dict(row) for row in history],
        'predictions': predictions_by_model,
        'news': [dict(row) for row in news_query]
    }
    return jsonify(data)

# --- Restored AI Analysis API Endpoint ---
@app.route('/api/summarize', methods=['POST'])
def get_ai_summary():
    """Generates an AI summary based on historical data sent from the frontend."""
    if not deepseek_client:
        return jsonify({'error': 'AI client is not initialized. Please check the API key.'}), 500

    # Get data from the request body sent by the frontend
    data = request.get_json()
    historical_data = data.get('historicalData')
    ticker = data.get('ticker')

    if not historical_data or not ticker:
        return jsonify({'error': 'Ticker and historical data must be provided.'}), 400

    # Key Optimization: Use only the last 30 days of data to build the prompt.
    # This prevents the prompt from being too large, which can cause timeouts or high costs.
    recent_data = historical_data[-30:]
    
    # Construct a high-quality prompt
    prompt = f"""
        You are a sharp and concise financial analyst.
        Based on the following historical price data for the stock ticker "{ticker}", provide a 2-3 sentence summary in English that covers its recent performance and key trends.
        Focus on the overall direction, significant peaks, and troughs. Do not use any introductory phrases like "Hello" or "Of course." Provide the analysis directly.

        Data (JSON format, last 30 days):
        {recent_data}
    """

    try:
        print(f"Contacting DeepSeek for a summary of {ticker}...")
        completion = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a sharp financial analyst who responds in English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # A lower temperature makes the response more factual
        )
        summary = completion.choices[0].message.content
        print("Successfully received summary.")
        return jsonify({'summary': summary})

    except Exception as e:
        print(f"An error occurred while calling the DeepSeek API: {e}")
        return jsonify({'error': 'Failed to generate AI summary.'}), 500


# --- Start the Server (Unchanged) ---
if __name__ == '__main__':
    # Ensure the port is 5001 to match the frontend proxy setting
    app.run(debug=True, port=5001)