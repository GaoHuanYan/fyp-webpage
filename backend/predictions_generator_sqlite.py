# 文件名: predictions_generator_sqlite.py
# 描述: 读取最新的历史股价，生成模拟的未来预测数据，并存入数据库。

import sqlite3
import random
from datetime import datetime, timedelta
import logging

# --- 配置 ---
DATABASE_FILE = "stock_data.db"
# 确保这个列表与你其他脚本中的一致
HSI_COMPONENTS = [
    "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK", "0011.HK", "0012.HK", 
    "0016.HK", "0017.HK", "0027.HK", "0066.HK", "0101.HK", "0175.HK", "0241.HK", 
    "0285.HK", "0288.HK", "0291.HK", "0316.HK", "0322.HK", "0386.HK", "0388.HK", 
    "0669.HK", "0688.HK", "0700.HK", "0762.HK", "0823.HK", "0836.HK", "0857.HK", 
    "0868.HK", "0881.HK", "0883.HK", "0939.HK", "0941.HK", "0960.HK", "0968.HK", 
    "0981.HK", "0992.HK", "1024.HK", "1038.HK", "1044.HK", "1088.HK", "1093.HK", 
    "1099.HK", "1109.HK", "1113.HK", "1177.HK", "1209.HK", "1211.HK", "1299.HK", 
    "1378.HK", "1398.HK", "1810.HK", "1876.HK", "1928.HK", "1929.HK", "1997.HK", 
    "2015.HK", "2020.HK", "2057.HK", "2269.HK", "2313.HK", "2318.HK", "2319.HK", 
    "2331.HK", "2359.HK", "2382.HK", "2388.HK", "2628.HK", "2688.HK", "2899.HK", 
    "3690.HK", "3692.HK", "3968.HK", "3988.HK", "6618.HK", "6690.HK", "6862.HK", 
    "9618.HK", "9633.HK", "9888.HK", "9901.HK", "9961.HK", "9988.HK", "9999.HK",
]
MOCK_MODELS = ['AlphaModel', 'BetaTrend'] # 模拟两个不同的预测模型

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_predictions_table(conn):
    """创建 stock_predictions 表 (如果不存在)。"""
    try:
        with conn:
            cursor = conn.cursor()
            # 定义未来真实预测表该有的样子
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                model_name TEXT NOT NULL,
                prediction_date TEXT NOT NULL,
                predicted_price REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, model_name, prediction_date)
            );
            """)
            logging.info("Table 'stock_predictions' checked/created successfully.")
    except sqlite3.Error as e:
        logging.error(f"创建预测表格失败: {e}")

def generate_and_store_predictions():
    """为所有股票生成并存储模拟预测数据。"""
    conn = sqlite3.connect(DATABASE_FILE)
    create_predictions_table(conn)
    
    all_predictions_to_insert = []

    for i, stock_code in enumerate(HSI_COMPONENTS):
        logging.info(f"--- 生成预测 {i+1}/{len(HSI_COMPONENTS)}: {stock_code} ---")
        
        # 1. 从 stock_data 表获取最新的收盘价作为基准
        cursor = conn.cursor()
        cursor.execute(
            "SELECT trade_date, close_price FROM stock_data WHERE stock_code = ? ORDER BY trade_date DESC LIMIT 1",
            (stock_code,)
        )
        last_data = cursor.fetchone()

        if not last_data:
            logging.warning(f"在数据库中未找到 {stock_code} 的历史数据，无法生成预测。")
            continue
        
        last_date_str, last_price = last_data
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        logging.info(f"找到 {stock_code} 的最新数据: 日期={last_date_str}, 收盘价={last_price:.2f}")

        # 2. 为每个模拟模型生成未来的预测数据
        for model in MOCK_MODELS:
            current_price = last_price
            for i in range(1, 8): # 生成未来7个周期的预测
                # 预测日期递增
                prediction_date = last_date + timedelta(days=i * 7)
                # 价格在上一天价格基础上随机波动
                price_fluctuation = random.uniform(-0.03, 0.035) # 波动范围
                current_price *= (1 + price_fluctuation)
                
                all_predictions_to_insert.append((
                    stock_code,
                    model,
                    prediction_date.strftime('%Y-%m-%d'),
                    round(current_price, 2)
                ))
    
    if not all_predictions_to_insert:
        logging.error("未能生成任何预测数据。")
        conn.close()
        return

    # 3. 使用 INSERT OR REPLACE 批量写入数据库。如果记录已存在，则会替换它。
    # 这让你可以反复运行此脚本来“刷新”假数据。
    logging.info(f"准备将 {len(all_predictions_to_insert)} 条预测记录存入数据库...")
    try:
        with conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT OR REPLACE INTO stock_predictions (
                    stock_code, model_name, prediction_date, predicted_price
                ) VALUES (?, ?, ?, ?);
            """
            cursor.executemany(insert_query, all_predictions_to_insert)
            logging.info(f"成功向数据库插入或替换了 {cursor.rowcount} 条预测记录。")
    except sqlite3.Error as e:
        logging.error(f"数据库预测数据插入操作失败: {e}")
    finally:
        conn.close()
        logging.info("预测数据库连接已关闭。")

if __name__ == "__main__":
    generate_and_store_predictions()
    logging.info("模拟预测数据生成任务全部完成！")