import sqlite3
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app) 
DATABASE = 'stock_data.db' 


try:
    deepseek_client = OpenAI(
        base_url="https://api.deepseek.com",
        api_key=os.getenv('DEEPSEEK_API_KEY')
    )
    print("DeepSeek AI client initialized successfully.")
except Exception as e:
    print(f"Warning: Failed to initialize DeepSeek client. AI features will be disabled. Error: {e}")
    deepseek_client = None

def get_db_connection():
    """Creates a database connection and sets the row factory to access data by column name."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn


@app.route('/api/stocks')
def get_stocks():
    """
    Fetches a list of all unique stock tickers from the database.
    This is the data source for the homepage stock list.
    """
    conn = get_db_connection()
    tickers_data = conn.execute('SELECT DISTINCT stock_code FROM stock_data ORDER BY stock_code ASC').fetchall()
    conn.close()
    stocks_list = [{'ticker': row['stock_code'], 'name': f"{row['stock_code'].replace('.HK', '')} Inc."} for row in tickers_data]
    return jsonify(stocks_list)

@app.route('/api/stocks/<ticker>')
def get_stock_detail(ticker):
    """
    Fetches all detailed information for a single stock, including historical prices, news, and model predictions.
    This is the core data source for the stock detail page.
    """
    conn = get_db_connection()
    
    history_rows = conn.execute(
        "SELECT trade_date AS date, open_price AS open, high_price AS high, low_price AS low, close_price AS close, volume FROM stock_data WHERE stock_code = ? ORDER BY trade_date ASC", 
        (ticker,)
    ).fetchall()
    
    if not history_rows:
        conn.close()
        error_message = f"Cannot Find the Stock '{ticker}'. Please Double Check the Input or Reload the Database."
        return jsonify({'error': error_message}), 404


    try:
        news_rows = conn.execute(
            "SELECT published_datetime AS date, title, full_text AS summary FROM yahoo_finance_news WHERE stock_code = ? AND full_text IS NOT NULL ORDER BY published_datetime DESC LIMIT 10", 
            (ticker,)
        ).fetchall()
    except sqlite3.OperationalError:
        print(f"Warning: Table 'yahoo_finance_news' not found for ticker {ticker}. News section will be empty.")
        news_rows = []


    try:
        predictions_query = conn.execute(
            'SELECT model_name, prediction_date AS date, predicted_price FROM stock_predictions WHERE stock_code = ? ORDER BY date ASC', 
            (ticker,)
        ).fetchall()
    except sqlite3.OperationalError:
        print(f"Warning: Table 'stock_predictions' not found for ticker {ticker}. Predictions section will be empty.")
        predictions_query = []

    conn.close()


    history = [dict(row) for row in history_rows]
    news = [dict(row) for row in news_rows]
    
 
    predictions_by_model = defaultdict(list)
    for row in predictions_query:
        predictions_by_model[row['model_name']].append({'date': row['date'], 'price': row['predicted_price']})


    data = {
        'ticker': ticker,
        'name': f'{ticker.replace(".HK", "")} Inc.',
        'history': history,
        'predictions': dict(predictions_by_model),
        'news': news
    }
    return jsonify(data)

@app.route('/api/summarize', methods=['POST'])
def get_ai_summary():
    """
    Receives stock data from the frontend and calls the AI model to generate a summary.
    This is a standalone AI service endpoint.
    """
    if not deepseek_client:
        return jsonify({'error': 'AI client is not initialized. Please check the DEEPSEEK_API_KEY in your .env file.'}), 503 # 503 Service Unavailable

    data = request.get_json()
    historical_data = data.get('historicalData')
    ticker = data.get('ticker')

    if not historical_data or not ticker:
        return jsonify({'error': 'Ticker and historical data must be provided.'}), 400 # 400 Bad Request

    recent_data = historical_data[-30:]
    prompt = f"""
        You are a sharp and concise financial analyst. If you can find the stock ticker "{ticker}" in your hong kong stock market database, you can introduce it firstly. Then
        based on the following historical price data for the stock ticker "{ticker}", provide a 2-3 sentence summary in English that covers its recent performance and key trends.
        Focus on the overall direction, significant peaks, and troughs. Do not use any introductory phrases like "Hello" or "Of course." Provide the analysis directly. 

        Data (JSON format, last 30 days):
        {recent_data}
    """
    try:
        completion = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a sharp financial analyst who responds in English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        summary = completion.choices[0].message.content
        return jsonify({'summary': summary})
    except Exception as e:
        print(f"An error occurred while calling the DeepSeek API: {e}")
        return jsonify({'error': 'Failed to generate AI summary due to an external API issue.'}), 502 # 502 Bad Gateway

@app.route('/api/top-movers')
def get_top_movers():
    """
    高效地从 stock_predictions 表中获取模型预测的、未来波动最大的前10只股票。
    """
    conn = get_db_connection()
    
    # 1. 首先，找到数据库中最新的一个预测日期
    latest_date_row = conn.execute(
        "SELECT MAX(prediction_date) as max_date FROM stock_predictions"
    ).fetchone()

    if not latest_date_row or not latest_date_row['max_date']:
        conn.close()
        return jsonify([]) # 如果没有预测数据，返回空列表

    latest_date = latest_date_row['max_date']
    
    # 2. 查询这个最新日期下，预测波动百分比（绝对值）最大的前10条记录
    #    我们直接使用已经计算好的 predicted_change_pct 字段
    movers_rows = conn.execute(
        """
        SELECT 
            stock_code AS ticker, 
            predicted_change_pct AS change_percent 
        FROM 
            stock_predictions 
        WHERE 
            prediction_date = ?
        ORDER BY 
            ABS(predicted_change_pct) DESC 
        LIMIT 10
        """,
        (latest_date,)
    ).fetchall()
    
    conn.close()

    # 3. 将查询结果转换为JSON格式
    #    fetchall() 返回的是 Row 对象列表, 我们需要转换为字典列表
    top_movers = [dict(row) for row in movers_rows]
    
    return jsonify(top_movers)




if __name__ == '__main__':

    app.run(debug=True, port=5001)