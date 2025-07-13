import yfinance as yf
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import time
import logging
import os
import random

DATABASE_FILE = "stock_data.db"

HSI_COMPONENTS = [
    "^HSI",
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

# 3. 时间和延迟配置
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=365 * 1)
DELAY_RANGE = (5, 10)  

# 4. 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_tables(conn):
    """使用 SQLite 语法创建表格"""
    try:
        with conn: 
            cursor = conn.cursor()
   
            create_stock_table_query = """
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume INTEGER,
                dividends REAL DEFAULT 0,
                stock_splits REAL DEFAULT 0,
                UNIQUE (stock_code, trade_date)
            );
            """
            cursor.execute(create_stock_table_query)
            logging.info("Table 'stock_data' checked/created successfully.")
    except sqlite3.Error as e:
        logging.error(f"创建表格失败: {e}")

def fetch_all_data():
    """
    核心函数：逐个获取所有股票数据，并一次性存入 SQLite。
    """
    all_rows_to_insert = []
    failed_stocks = []

    # --- 第一步: 循环获取所有数据 ---
    for i, stock_code in enumerate(HSI_COMPONENTS):
        logging.info(f"--- 处理 {i+1}/{len(HSI_COMPONENTS)}: {stock_code} ---")
        try:
            ticker = yf.Ticker(stock_code)
            stock_data = ticker.history(start=START_DATE, end=END_DATE)

            if stock_data.empty:
                logging.warning(f"未找到股票 {stock_code} 的历史数据。")
                continue

            # 准备要插入的数据行
            for trade_date, row in stock_data.iterrows():
                all_rows_to_insert.append((
                    stock_code,
                    trade_date.strftime('%Y-%m-%d'), # 日期存为文本
                    None if pd.isna(row['Open']) else float(row['Open']),
                    None if pd.isna(row['High']) else float(row['High']),
                    None if pd.isna(row['Low']) else float(row['Low']),
                    None if pd.isna(row['Close']) else float(row['Close']),
                    None if pd.isna(row['Volume']) else int(row['Volume']),
                    None if pd.isna(row['Dividends']) else float(row['Dividends']),
                    None if pd.isna(row['Stock Splits']) else float(row['Stock Splits'])
                ))
            logging.info(f"成功获取 {stock_code} 的 {len(stock_data)} 条数据。")

        except Exception as e:
            logging.error(f"获取股票 {stock_code} 历史数据失败: {e}")
            failed_stocks.append(stock_code)
        
        # 随机延迟，避免被服务器限制
        delay = random.uniform(*DELAY_RANGE)
        logging.info(f"暂停 {delay:.2f} 秒...")
        time.sleep(delay)

    # --- 第二步: 批量插入所有获取到的数据 ---
    if not all_rows_to_insert:
        logging.error("未能成功获取任何股票数据，数据库未写入。")
        return

    logging.info(f"准备将 {len(all_rows_to_insert)} 条数据记录一次性存入数据库...")
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        create_tables(conn) # 确保表存在
        cursor = conn.cursor()

        # 使用 SQLite 的 ON CONFLICT 语法 (等同于 PostgreSQL 的 ON CONFLICT ... DO UPDATE)
        insert_query = """
            INSERT INTO stock_data (
                stock_code, trade_date, open_price, high_price, low_price,
                close_price, volume, dividends, stock_splits
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (stock_code, trade_date) DO UPDATE SET
                open_price = excluded.open_price,
                high_price = excluded.high_price,
                low_price = excluded.low_price,
                close_price = excluded.close_price,
                volume = excluded.volume,
                dividends = excluded.dividends,
                stock_splits = excluded.stock_splits;
        """
        
        # executemany() 是最高效的批量插入方法
        cursor.executemany(insert_query, all_rows_to_insert)
        conn.commit()
        logging.info(f"成功向数据库批量插入/更新了 {cursor.rowcount} 条记录。")

    except sqlite3.Error as e:
        logging.error(f"数据库批量插入操作失败: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("数据库连接已关闭。")
    
    if failed_stocks:
        logging.warning(f"以下股票未能成功下载: {failed_stocks}")

if __name__ == "__main__":
    # 在运行前，删除旧的数据库文件以确保数据是全新的
    if os.path.exists(DATABASE_FILE):
        logging.warning(f"发现旧的数据库文件 '{DATABASE_FILE}'，正在删除...")
        os.remove(DATABASE_FILE)
        
    fetch_all_data()
    logging.info("数据抓取任务全部完成！")