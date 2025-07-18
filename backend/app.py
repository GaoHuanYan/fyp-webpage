# # import sqlite3
# # import os
# # from flask import Flask, jsonify, request
# # from flask_cors import CORS
# # from collections import defaultdict
# # from dotenv import load_dotenv
# # from openai import OpenAI

# # load_dotenv()

# # app = Flask(__name__)
# # CORS(app) 
# # DATABASE = 'stock_data.db' 


# # try:
# #     deepseek_client = OpenAI(
# #         base_url="https://api.deepseek.com",
# #         api_key=os.getenv('DEEPSEEK_API_KEY')
# #     )
# #     print("DeepSeek AI client initialized successfully.")
# # except Exception as e:
# #     print(f"Warning: Failed to initialize DeepSeek client. AI features will be disabled. Error: {e}")
# #     deepseek_client = None

# # def get_db_connection():
# #     """Creates a database connection and sets the row factory to access data by column name."""
# #     conn = sqlite3.connect(DATABASE)
# #     conn.row_factory = sqlite3.Row 
# #     return conn


# # @app.route('/api/stocks')
# # def get_stocks():
# #     """
# #     Fetches a list of all unique stock tickers from the database.
# #     This is the data source for the homepage stock list.
# #     """
# #     conn = get_db_connection()
# #     tickers_data = conn.execute('SELECT DISTINCT stock_code FROM stock_data ORDER BY stock_code ASC').fetchall()
# #     conn.close()
# #     stocks_list = [{'ticker': row['stock_code'], 'name': f"{row['stock_code'].replace('.HK', '')} Inc."} for row in tickers_data]
# #     return jsonify(stocks_list)

# # @app.route('/api/stocks/<ticker>')
# # def get_stock_detail(ticker):
# #     """
# #     Fetches all detailed information for a single stock, including historical prices, news, and model predictions.
# #     This is the core data source for the stock detail page.
# #     """
# #     conn = get_db_connection()
    
# #     history_rows = conn.execute(
# #         "SELECT trade_date AS date, open_price AS open, high_price AS high, low_price AS low, close_price AS close, volume FROM stock_data WHERE stock_code = ? ORDER BY trade_date ASC", 
# #         (ticker,)
# #     ).fetchall()
    
# #     if not history_rows:
# #         conn.close()
# #         error_message = f"Cannot Find the Stock '{ticker}'. Please Double Check the Input or Reload the Database."
# #         return jsonify({'error': error_message}), 404


# #     try:
# #         news_rows = conn.execute(
# #             "SELECT published_datetime AS date, title, full_text AS summary FROM yahoo_finance_news WHERE stock_code = ? AND full_text IS NOT NULL ORDER BY published_datetime DESC LIMIT 10", 
# #             (ticker,)
# #         ).fetchall()
# #     except sqlite3.OperationalError:
# #         print(f"Warning: Table 'yahoo_finance_news' not found for ticker {ticker}. News section will be empty.")
# #         news_rows = []


# #     try:
# #         predictions_query = conn.execute(
# #             'SELECT model_name, prediction_date AS date, predicted_price FROM stock_predictions WHERE stock_code = ? ORDER BY date ASC', 
# #             (ticker,)
# #         ).fetchall()
# #     except sqlite3.OperationalError:
# #         print(f"Warning: Table 'stock_predictions' not found for ticker {ticker}. Predictions section will be empty.")
# #         predictions_query = []

# #     conn.close()


# #     history = [dict(row) for row in history_rows]
# #     news = [dict(row) for row in news_rows]
    
 
# #     predictions_by_model = defaultdict(list)
# #     for row in predictions_query:
# #         predictions_by_model[row['model_name']].append({'date': row['date'], 'price': row['predicted_price']})


# #     data = {
# #         'ticker': ticker,
# #         'name': f'{ticker.replace(".HK", "")} Inc.',
# #         'history': history,
# #         'predictions': dict(predictions_by_model),
# #         'news': news
# #     }
# #     return jsonify(data)

# # @app.route('/api/summarize', methods=['POST'])
# # def get_ai_summary():
# #     """
# #     Receives stock data from the frontend and calls the AI model to generate a summary.
# #     This is a standalone AI service endpoint.
# #     """
# #     if not deepseek_client:
# #         return jsonify({'error': 'AI client is not initialized. Please check the DEEPSEEK_API_KEY in your .env file.'}), 503 # 503 Service Unavailable

# #     data = request.get_json()
# #     historical_data = data.get('historicalData')
# #     ticker = data.get('ticker')

# #     if not historical_data or not ticker:
# #         return jsonify({'error': 'Ticker and historical data must be provided.'}), 400 # 400 Bad Request

# #     recent_data = historical_data[-30:]
# #     prompt = f"""
# #         You are a sharp and concise financial analyst. If you can find the stock ticker "{ticker}" in your hong kong stock market database, you can introduce it firstly. Then
# #         based on the following historical price data for the stock ticker "{ticker}", provide a 2-3 sentence summary in English that covers its recent performance and key trends.
# #         Focus on the overall direction, significant peaks, and troughs. Do not use any introductory phrases like "Hello" or "Of course." Provide the analysis directly. 

# #         Data (JSON format, last 30 days):
# #         {recent_data}
# #     """
# #     try:
# #         completion = deepseek_client.chat.completions.create(
# #             model="deepseek-chat",
# #             messages=[
# #                 {"role": "system", "content": "You are a sharp financial analyst who responds in English."},
# #                 {"role": "user", "content": prompt}
# #             ],
# #             temperature=0.5,
# #         )
# #         summary = completion.choices[0].message.content
# #         return jsonify({'summary': summary})
# #     except Exception as e:
# #         print(f"An error occurred while calling the DeepSeek API: {e}")
# #         return jsonify({'error': 'Failed to generate AI summary due to an external API issue.'}), 502 # 502 Bad Gateway

# # @app.route('/api/top-movers')
# # def get_top_movers():
# #     """
# #     高效地从 stock_predictions 表中获取模型预测的、未来波动最大的前10只股票。
# #     """
# #     conn = get_db_connection()
    
# #     # 1. 首先，找到数据库中最新的一个预测日期
# #     latest_date_row = conn.execute(
# #         "SELECT MAX(prediction_date) as max_date FROM stock_predictions"
# #     ).fetchone()

# #     if not latest_date_row or not latest_date_row['max_date']:
# #         conn.close()
# #         return jsonify([]) # 如果没有预测数据，返回空列表

# #     latest_date = latest_date_row['max_date']
    
# #     # 2. 查询这个最新日期下，预测波动百分比（绝对值）最大的前10条记录
# #     #    我们直接使用已经计算好的 predicted_change_pct 字段
# #     movers_rows = conn.execute(
# #         """
# #         SELECT 
# #             stock_code AS ticker, 
# #             predicted_change_pct AS change_percent 
# #         FROM 
# #             stock_predictions 
# #         WHERE 
# #             prediction_date = ?
# #         ORDER BY 
# #             ABS(predicted_change_pct) DESC 
# #         LIMIT 10
# #         """,
# #         (latest_date,)
# #     ).fetchall()
    
# #     conn.close()

# #     # 3. 将查询结果转换为JSON格式
# #     #    fetchall() 返回的是 Row 对象列表, 我们需要转换为字典列表
# #     top_movers = [dict(row) for row in movers_rows]
    
# #     return jsonify(top_movers)




# # if __name__ == '__main__':

# #     app.run(debug=True, port=5001)

# import sqlite3
# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from collections import defaultdict
# from dotenv import load_dotenv
# from openai import OpenAI

# # 加载环境变量
# load_dotenv()

# # 初始化 Flask 应用
# app = Flask(__name__)
# CORS(app) 
# DATABASE = 'stock_data.db' 

# # 初始化 AI 客户端
# try:
#     deepseek_client = OpenAI(
#         base_url="https://api.deepseek.com",
#         api_key=os.getenv('DEEPSEEK_API_KEY')
#     )
#     print("DeepSeek AI client initialized successfully.")
# except Exception as e:
#     print(f"Warning: Failed to initialize DeepSeek client. AI features will be disabled. Error: {e}")
#     deepseek_client = None

# def get_db_connection():
#     """创建一个数据库连接，并设置 row_factory 以便按列名访问数据。"""
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row 
#     return conn


# @app.route('/api/stocks')
# def get_stocks():
#     """获取数据库中所有唯一的股票代码列表。"""
#     conn = get_db_connection()
#     tickers_data = conn.execute('SELECT DISTINCT stock_code FROM stock_data ORDER BY stock_code ASC').fetchall()
#     conn.close()
#     stocks_list = [{'ticker': row['stock_code'], 'name': f"{row['stock_code'].replace('.HK', '')} Inc."} for row in tickers_data]
#     return jsonify(stocks_list)

# @app.route('/api/stocks/<ticker>')
# def get_stock_detail(ticker):
#     """获取单个股票的所有详细信息，包括历史价格、新闻和模型预测。"""
#     conn = get_db_connection()
    
#     # 获取历史价格数据
#     history_rows = conn.execute(
#         "SELECT trade_date AS date, open_price AS open, high_price AS high, low_price AS low, close_price AS close, volume FROM stock_data WHERE stock_code = ? ORDER BY trade_date ASC", 
#         (ticker,)
#     ).fetchall()
    
#     # 如果找不到股票，返回404错误
#     if not history_rows:
#         conn.close()
#         error_message = f"Cannot Find the Stock '{ticker}'. Please Double Check the Input or Reload the Database."
#         return jsonify({'error': error_message}), 404

#     # 获取新闻数据
#     try:
#         news_rows = conn.execute(
#             "SELECT published_datetime AS date, title, full_text AS summary FROM yahoo_finance_news WHERE stock_code = ? AND full_text IS NOT NULL ORDER BY published_datetime DESC LIMIT 10", 
#             (ticker,)
#         ).fetchall()
#     except sqlite3.OperationalError:
#         print(f"Warning: Table 'yahoo_finance_news' not found for ticker {ticker}. News section will be empty.")
#         news_rows = []

#     # ==================================================================
#     # ===                      这是核心修改区域                      ===
#     # ==================================================================
#     try:
#         # 这个查询使用窗口函数为每个模型的预测按日期降序排名，然后只选择排名前5的记录
#         predictions_query = conn.execute(
#             """
#             SELECT model_name, date, predicted_price
#             FROM (
#                 SELECT 
#                     model_name, 
#                     prediction_date AS date, 
#                     predicted_price,
#                     ROW_NUMBER() OVER(PARTITION BY model_name ORDER BY prediction_date DESC) as rn
#                 FROM stock_predictions
#                 WHERE stock_code = ?
#             )
#             WHERE rn <= 5
#             ORDER BY date ASC;
#             """,
#             (ticker,)
#         ).fetchall()
#     except sqlite3.OperationalError:
#         print(f"Warning: Table 'stock_predictions' not found for ticker {ticker}. Predictions section will be empty.")
#         predictions_query = []
#     # ==================================================================
#     # ===                        修改结束                          ===
#     # ==================================================================

#     conn.close()

#     # 格式化数据
#     history = [dict(row) for row in history_rows]
#     news = [dict(row) for row in news_rows]
    
#     # 按模型分组预测结果
#     predictions_by_model = defaultdict(list)
#     for row in predictions_query:
#         predictions_by_model[row['model_name']].append({'date': row['date'], 'price': row['predicted_price']})

#     # 准备最终的JSON响应
#     data = {
#         'ticker': ticker,
#         'name': f'{ticker.replace(".HK", "")} Inc.',
#         'history': history,
#         'predictions': dict(predictions_by_model),
#         'news': news
#     }
#     return jsonify(data)

# @app.route('/api/summarize', methods=['POST'])
# def get_ai_summary():
#     """接收前端的股票数据，并调用AI模型生成摘要。"""
#     if not deepseek_client:
#         return jsonify({'error': 'AI client is not initialized. Please check the DEEPSEEK_API_KEY in your .env file.'}), 503

#     data = request.get_json()
#     historical_data = data.get('historicalData')
#     ticker = data.get('ticker')

#     if not historical_data or not ticker:
#         return jsonify({'error': 'Ticker and historical data must be provided.'}), 400

#     recent_data = historical_data[-30:]
#     prompt = f"""
#         You are a sharp and concise financial analyst. If you can find the stock ticker "{ticker}" in your hong kong stock market database, you can introduce it firstly. Do not use any introductory phrases like "Hello" or "Of course." Provide the analysis directly. 
# As a senior Hong Kong stock analyst, please write a structured analysis report based on the complete market data of ${ticker} over the past 30 trading days. The report should include the following elements:
# 1、 Core Trend Analysis (3-4 sentences)
# 1. Overall trend judgment:
# -Clarify the upward/downward/oscillatory trend
# -Cumulative increase or decrease (percentage+absolute price change)
# -Volatility characteristics (such as "daily fluctuation ± 2.3%")
# 2. Key turning point:
# -List 2-3 important peaks/valleys (date+price)
# -Mark the situation of breaking through/falling below the key level
# -Significant volume trading days and their impact
# 2、 Deep interpretation of technical aspects (2-3 sentences)
# 1. Indicator status:
# -Arrangement of moving average system (such as "5-day line crossing 20 day line")
# -Key indicator values (RSI, MACD, etc.)
   
# 2. Quantity price relationship:
# -Characteristics of Trading Volume Changes
# -Abnormal volume price signal (such as "shrinking volume and rising")
# 3、 Industry comparison and valuation (2 sentences)
# 1. Relative performance:
# -Compare industry indices
# -Industry ranking
   
# 2. Valuation changes:
# -Main Valuation Indicator Dynamics
# -Compared to the industry average
# 4、 Risk Warning (2-3 sentences)
# 1. Technical risks:
# -Key support/resistance level
# -Overbuy/oversold signal
   
# 2. Event risk:
# -Important upcoming dates
# -Potential catalyst/risk source

# 5、 Comprehensive analysis conclusion (1-2 sentences)
# Provide actionable suggestions or trend predictions
# [Data Requirements]
# -All prices are accurate to 2 decimal places
# -Percentage change to one decimal place
# -Date in YYYY-MM-DD format
# -Technical indicator parameters should indicate the period (such as RSI (14))
# [Prohibited Content]
# -Vague expressions (such as "possible" or "perhaps")
# -Conclusion without data support
# -Repetitive description
#         Data (JSON format, last 30 days):
#         {recent_data}
#     """
#     try:
#         completion = deepseek_client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[
#                 {"role": "system", "content": "You are a sharp financial analyst who responds in English."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.5,
#         )
#         summary = completion.choices[0].message.content
#         return jsonify({'summary': summary})
#     except Exception as e:
#         print(f"An error occurred while calling the DeepSeek API: {e}")
#         return jsonify({'error': 'Failed to generate AI summary due to an external API issue.'}), 502

# @app.route('/api/top-movers')
# def get_top_movers():
#     """高效地从 stock_predictions 表中获取模型预测的、未来波动最大的前10只股票。"""
#     conn = get_db_connection()
    
#     latest_date_row = conn.execute(
#         "SELECT MAX(prediction_date) as max_date FROM stock_predictions"
#     ).fetchone()

#     if not latest_date_row or not latest_date_row['max_date']:
#         conn.close()
#         return jsonify([])

#     latest_date = latest_date_row['max_date']
    
#     movers_rows = conn.execute(
#         """
#         SELECT 
#             stock_code AS ticker, 
#             predicted_change_pct AS change_percent 
#         FROM 
#             stock_predictions 
#         WHERE 
#             prediction_date = ?
#         ORDER BY 
#             ABS(predicted_change_pct) DESC 
#         LIMIT 10
#         """,
#         (latest_date,)
#     ).fetchall()
    
#     conn.close()

#     top_movers = [dict(row) for row in movers_rows]
    
#     return jsonify(top_movers)

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)



# filename: app.py
import sqlite3
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app) 
DATABASE = 'stock_data.db' 

# Initialize AI client
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
    """Fetches a list of all unique stock tickers from the database."""
    conn = get_db_connection()
    tickers_data = conn.execute('SELECT DISTINCT stock_code FROM stock_data ORDER BY stock_code ASC').fetchall()
    conn.close()
    stocks_list = [{'ticker': row['stock_code'], 'name': f"{row['stock_code'].replace('.HK', '')} Inc."} for row in tickers_data]
    return jsonify(stocks_list)

@app.route('/api/stocks/<ticker>')
def get_stock_detail(ticker):
    """Fetches all detailed information for a single stock."""
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
    Receives stock data and calls the AI model to generate a structured, Markdown-formatted summary.
    """
    if not deepseek_client:
        return jsonify({'error': 'AI client is not initialized. Check DEEPSEEK_API_KEY.'}), 503

    data = request.get_json()
    historical_data = data.get('historicalData')
    ticker = data.get('ticker')

    if not historical_data or not ticker:
        return jsonify({'error': 'Ticker and historical data must be provided.'}), 400

    recent_data = historical_data[-30:]
    
    # ==================================================================
    # ===                CORE CHANGE: THE NEW PROMPT                 ===
    # ==================================================================
    # This new prompt instructs the AI to generate a structured report using Markdown.
    prompt = f"""
        As a senior Hong Kong stock market analyst, generate a structured analysis report for stock **{ticker}** based on its last 30 days of trading data.
        Format the entire response using Markdown. Use `####` for section titles and `**` for bolding key terms and figures. Do not use any introductory phrases.

        #### **1. Core Trend Analysis**
        - **Overall Trend**: [Describe the primary trend (e.g., upward, downward, volatile sideways). State the starting price and date, and the ending price and date. Calculate and include the percentage and absolute HKD change. Example: "Strong upward trend, rising from **21.48 (2025-06-02)** to **24.10 (2025-07-14)** (+12.2%, +2.62 HKD)."]
        - **Key Turning Points**: [Identify 2-3 significant dates. Examples: "Rebounded at **21.34 (2025-06-19)** after testing support.", "Broke out to **23.25 (2025-07-02)** on high volume."]

        #### **2. Technical Deep Dive**
        - **Indicator Status**: [Mention the status of key indicators. Example: "5-day MA (**23.80**) is above the 20-day MA (**22.90**), confirming a bullish alignment. RSI(14) is at **68**, approaching overbought levels."]
        - **Volume-Price Analysis**: [Analyze the relationship between price and volume. Example: "The breakout on **2025-07-02** was supported by volume **260%** above the 30-day average, confirming strong buying interest."]

        #### **3. Risk Warning**
        - **Technical Risks**: [Identify immediate support and resistance levels and any warning signals. Example: "Immediate support is at the 20-day MA around **23.50 HKD**. An RSI above **70** could trigger a short-term pullback."]
        - **Event Risks**: [Mention any upcoming events that could impact the price. Example: "Earnings report expected on **2025-07-25** could introduce volatility."]

        #### **4. Conclusion & Action**
        - **Actionable Insight**: [Provide a concise conclusion. Example: "Hold with a trailing stop at **23.50 HKD**. The next upside target is **25.00 HKD** if current momentum and volume are sustained."]

        **Data (JSON format, last 30 days):**
        {recent_data}
    """
    
    try:
        completion = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a professional Hong Kong stock market analyst who provides structured reports in Markdown format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6, # Slightly increased for better text generation
            max_tokens=1024,
        )
        summary = completion.choices[0].message.content
        return jsonify({'summary': summary})
    except Exception as e:
        print(f"An error occurred while calling the DeepSeek API: {e}")
        return jsonify({'error': 'Failed to generate AI summary due to an external API issue.'}), 502

# The rest of the file remains the same...
@app.route('/api/top-movers')
def get_top_movers():
    """Fetches top 10 predicted movers from the database."""
    conn = get_db_connection()
    
    latest_date_row = conn.execute(
        "SELECT MAX(prediction_date) as max_date FROM stock_predictions"
    ).fetchone()

    if not latest_date_row or not latest_date_row['max_date']:
        conn.close()
        return jsonify([])

    latest_date = latest_date_row['max_date']
    
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

    top_movers = [dict(row) for row in movers_rows]
    
    return jsonify(top_movers)


if __name__ == '__main__':
    app.run(debug=True, port=5001)