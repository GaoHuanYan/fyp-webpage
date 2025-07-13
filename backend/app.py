

# import sqlite3
# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from collections import defaultdict
# from dotenv import load_dotenv
# from openai import OpenAI

# # --- 初始化和配置 (无需改动) ---
# load_dotenv()
# app = Flask(__name__)
# CORS(app)
# DATABASE = 'stock_data.db' # 确保指向正确的数据库文件

# # --- 初始化 DeepSeek 客户端 (无需改动) ---
# try:
#     deepseek_client = OpenAI(
#         base_url="https://api.deepseek.com",
#         api_key=os.getenv('DEEPSEEK_API_KEY')
#     )
#     print("DeepSeek client initialized successfully.")
# except Exception as e:
#     print(f"Warning: Failed to initialize DeepSeek client: {e}")
#     deepseek_client = None

# # --- 数据库连接 (无需改动) ---
# def get_db_connection():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row 
#     return conn

# # --- API 端点 (已全部更新为正确版本) ---

# @app.route('/api/stocks')
# def get_stocks():
#     """从价格数据表 'stock_data' 获取股票代码列表"""
#     conn = get_db_connection()
#     # 假设您的价格爬虫使用 'stock_data' 表和 'stock_code' 列
#     tickers_data = conn.execute('SELECT DISTINCT stock_code FROM stock_data ORDER BY stock_code ASC').fetchall()
#     conn.close()
#     stocks_list = [{'ticker': row['stock_code'], 'name': f"{row['stock_code'].replace('.HK', '')} Inc."} for row in tickers_data]
#     return jsonify(stocks_list)

# @app.route('/api/stocks/<ticker>')
# def get_stock_detail(ticker):
#     """从所有相关的表中获取数据：历史价格、新闻、预测"""
#     conn = get_db_connection()
    
#     # 1. 获取历史数据 (假设来自 'stock_data' 表)
#     history_rows = conn.execute("SELECT trade_date AS date, open_price AS open, high_price AS high, low_price AS low, close_price AS close, volume FROM stock_data WHERE stock_code = ? ORDER BY trade_date ASC", (ticker,)).fetchall()
    
#     # 2. 获取新闻数据 (核心修改！)
#     try:
#         # <-- 修改点: 查询正确的表名 'yahoo_finance_news'
#         # <-- 修改点: 使用 AS 关键字将数据库列名翻译成前端需要的JSON键名
#         news_rows = conn.execute("""
#             SELECT 
#                 published_datetime AS date, 
#                 title, 
#                 full_text AS summary 
#             FROM yahoo_finance_news 
#             WHERE stock_code = ? AND full_text IS NOT NULL 
#             ORDER BY published_datetime DESC 
#             LIMIT 10
#         """, (ticker,)).fetchall()
#     except sqlite3.OperationalError:
#         # 这是一个非常健壮的设计：如果 news 表还不存在，程序不会崩溃，而是返回空列表
#         print("Warning: 'yahoo_finance_news' table not found. News section will be empty.")
#         news_rows = []

#     # 3. 获取预测数据 (假设来自 'stock_predictions' 表)
#     try:
#         predictions_query = conn.execute('SELECT model_name, prediction_date AS date, predicted_price FROM stock_predictions WHERE stock_code = ? ORDER BY date ASC', (ticker,)).fetchall()
#     except sqlite3.OperationalError:
#         print("Warning: 'stock_predictions' table not found. Predictions section will be empty.")
#         predictions_query = []

#     conn.close()

#     if not history_rows:
#         return jsonify({'error': f'Data for ticker {ticker} not found in the database.'}), 404

#     # --- 组装数据 (逻辑不变) ---
#     history = [dict(row) for row in history_rows]
#     news = [dict(row) for row in news_rows]
    
#     predictions_by_model = defaultdict(list)
#     for row in predictions_query:
#         predictions_by_model[row['model_name']].append({'date': row['date'], 'price': row['predicted_price']})

#     # 返回给前端的JSON结构保持完全不变
#     data = {
#         'ticker': ticker,
#         'name': f'{ticker.replace(".HK", "")} Inc.',
#         'history': history,
#         'predictions': dict(predictions_by_model),
#         'news': news
#     }
#     return jsonify(data)

# # --- AI 分析接口 (无需改动) ---
# @app.route('/api/summarize', methods=['POST'])
# def get_ai_summary():
#     # ... (此部分代码完全不变，因为它不直接操作数据库)
#     if not deepseek_client:
#         return jsonify({'error': 'AI client is not initialized. Please check the API key.'}), 500
#     data = request.get_json()
#     historical_data = data.get('historicalData')
#     ticker = data.get('ticker')
#     if not historical_data or not ticker:
#         return jsonify({'error': 'Ticker and historical data must be provided.'}), 400
#     recent_data = historical_data[-30:]
#     prompt = f"""
#         You are a sharp and concise financial analyst.
#         Based on the following historical price data for the stock ticker "{ticker}", provide a 2-3 sentence summary in English that covers its recent performance and key trends.
#         Focus on the overall direction, significant peaks, and troughs. Do not use any introductory phrases like "Hello" or "Of course." Provide the analysis directly.

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
#         return jsonify({'error': 'Failed to generate AI summary.'}), 500



# # --- 启动服务器 (无需改动) ---
# if __name__ == '__main__':
#     app.run(debug=True, port=5001)
import sqlite3
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI

# --- 初始化与配置 ---
# 加载 .env 文件中的环境变量 (例如 DEEPSEEK_API_KEY)
load_dotenv()

app = Flask(__name__)
# 允许所有来源的跨域请求，这对于前后端分离部署至关重要
CORS(app) 
# 定义数据库文件名
DATABASE = 'stock_data.db' 

# --- 初始化 DeepSeek AI 客户端 ---
# 这是一个健壮的设计：即使API密钥无效或网络不通，程序也不会崩溃
try:
    deepseek_client = OpenAI(
        base_url="https://api.deepseek.com",
        api_key=os.getenv('DEEPSEEK_API_KEY')
    )
    print("DeepSeek AI client initialized successfully.")
except Exception as e:
    print(f"Warning: Failed to initialize DeepSeek client. AI features will be disabled. Error: {e}")
    deepseek_client = None

# --- 数据库辅助函数 ---
def get_db_connection():
    """创建一个数据库连接，并设置行工厂以方便地按列名访问数据"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

# --- API 端点 ---

@app.route('/api/stocks')
def get_stocks():
    """
    获取数据库中所有不重复的股票代码列表。
    这是主页股票列表的数据源。
    """
    conn = get_db_connection()
    # 从 'stock_data' 表中查询所有唯一的股票代码
    tickers_data = conn.execute('SELECT DISTINCT stock_code FROM stock_data ORDER BY stock_code ASC').fetchall()
    conn.close()
    # 将查询结果格式化为前端需要的 {ticker, name} 结构
    stocks_list = [{'ticker': row['stock_code'], 'name': f"{row['stock_code'].replace('.HK', '')} Inc."} for row in tickers_data]
    return jsonify(stocks_list)

@app.route('/api/stocks/<ticker>')
def get_stock_detail(ticker):
    """
    获取单个股票的所有详细信息，包括历史价格、新闻和模型预测。
    这是股票详情页的核心数据源。
    """
    conn = get_db_connection()
    
    # 1. 获取历史价格数据
    history_rows = conn.execute(
        "SELECT trade_date AS date, open_price AS open, high_price AS high, low_price AS low, close_price AS close, volume FROM stock_data WHERE stock_code = ? ORDER BY trade_date ASC", 
        (ticker,)
    ).fetchall()
    
    # 如果连最基本的历史数据都没有，说明股票代码无效，直接返回一个友好的错误信息
    if not history_rows:
        conn.close()
        error_message = f"Cannot Find the stock '{ticker}'. Please Double Check the Input or Reload the Database."
        return jsonify({'error': error_message}), 404

    # 2. 获取新闻数据 (使用 try-except 保证即使新闻表不存在也不会崩溃)
    try:
        news_rows = conn.execute(
            "SELECT published_datetime AS date, title, full_text AS summary FROM yahoo_finance_news WHERE stock_code = ? AND full_text IS NOT NULL ORDER BY published_datetime DESC LIMIT 10", 
            (ticker,)
        ).fetchall()
    except sqlite3.OperationalError:
        print(f"Warning: Table 'yahoo_finance_news' not found for ticker {ticker}. News section will be empty.")
        news_rows = []

    # 3. 获取预测数据 (同样使用 try-except)
    try:
        predictions_query = conn.execute(
            'SELECT model_name, prediction_date AS date, predicted_price FROM stock_predictions WHERE stock_code = ? ORDER BY date ASC', 
            (ticker,)
        ).fetchall()
    except sqlite3.OperationalError:
        print(f"Warning: Table 'stock_predictions' not found for ticker {ticker}. Predictions section will be empty.")
        predictions_query = []

    conn.close()

    # --- 组装数据以匹配前端期望的格式 ---
    history = [dict(row) for row in history_rows]
    news = [dict(row) for row in news_rows]
    
    # 使用 defaultdict 轻松地按模型名称对预测进行分组
    predictions_by_model = defaultdict(list)
    for row in predictions_query:
        predictions_by_model[row['model_name']].append({'date': row['date'], 'price': row['predicted_price']})

    # 最终返回给前端的 JSON 对象
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
    接收前端发送的股票数据，调用 AI 模型生成摘要。
    这是一个独立的 AI 服务接口。
    """
    if not deepseek_client:
        return jsonify({'error': 'AI client is not initialized. Please check the DEEPSEEK_API_KEY in your .env file.'}), 503 # 503 Service Unavailable

    data = request.get_json()
    historical_data = data.get('historicalData')
    ticker = data.get('ticker')

    if not historical_data or not ticker:
        return jsonify({'error': 'Ticker and historical data must be provided.'}), 400 # 400 Bad Request

    # 只使用最近30天的数据以节省 token 并聚焦于近期表现
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

# --- 启动服务器 ---
if __name__ == '__main__':
    # 使用 debug=True 进行本地开发，它会自动重载代码改动
    # port=5001 是为了避免与前端或其他常用服务的端口冲突
    app.run(debug=True, port=5001)