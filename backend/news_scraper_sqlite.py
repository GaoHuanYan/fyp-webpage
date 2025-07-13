

import yfinance as yf
import sqlite3
from datetime import datetime, timezone
import time
import logging
import random

# --- 配置 (保持不变) ---
DATABASE_FILE = "stock_data.db"
DELAY_RANGE = (3, 7)
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 数据库函数 (保持不变) ---
def create_news_table(conn):
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS yahoo_finance_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                uuid TEXT UNIQUE NOT NULL,
                title TEXT,
                published_datetime TEXT,
                full_text TEXT,
                link TEXT
            );
            """)
            logging.info("Table 'yahoo_finance_news' checked/created successfully.")
    except sqlite3.Error as e:
        logging.error(f"创建新闻表格失败: {e}")

def insert_news_data(conn, news_data_list):
    if not news_data_list:
        return 0
    try:
        cursor = conn.cursor()
        insert_query = """
            INSERT OR IGNORE INTO yahoo_finance_news (
                stock_code, uuid, title, published_datetime, full_text, link
            ) VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.executemany(insert_query, news_data_list)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        logging.error(f"数据库新闻插入操作失败: {e}")
        conn.rollback()
        return 0

# --- 主函数 (已根据新数据结构修复) ---
def fetch_and_store_news_fixed():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        logging.info("数据库连接已打开。")
        create_news_table(conn)
        
        total_new_entries = 0
        for i, stock_code in enumerate(HSI_COMPONENTS):
            logging.info(f"--- 获取新闻 {i+1}/{len(HSI_COMPONENTS)}: {stock_code} ---")
            
            current_stock_news_to_insert = []
            try:
                ticker = yf.Ticker(stock_code)
                news_list = ticker.news

                if not news_list:
                    logging.warning(f"未找到股票 {stock_code} 的新闻。")
                    time.sleep(1)
                    continue

                logging.info(f"成功获取 {stock_code} 的 {len(news_list)} 条新闻，正在处理...")

                for news_item in news_list:
                    # --- 核心改动：根据新的数据结构提取信息 ---
                    
                    # 1. 检查必要的数据是否存在
                    if 'id' not in news_item or 'content' not in news_item or 'pubDate' not in news_item['content']:
                        logging.warning("跳过一条格式不完整的新闻。")
                        continue
                    
                    content = news_item['content']
                    
                    # 2. 获取数据
                    uuid = news_item['id']
                    title = content.get('title')
                    summary = content.get('summary')
                    
                    # 3. 解析新的日期格式 (从 '2025-06-13T21:04:32Z' 转换为 'YYYY-MM-DD HH:MM:SS')
                    try:
                        # fromisoformat 可以直接处理 'Z' (Zulu time / UTC)
                        dt_object_utc = datetime.fromisoformat(content['pubDate'])
                        # 转换为本地时区或保持UTC，然后格式化
                        formatted_datetime = dt_object_utc.strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        logging.warning(f"无法解析日期 '{content.get('pubDate')}'，跳过此新闻。")
                        continue

                    # 4. 安全地获取链接
                    link = None
                    if 'canonicalUrl' in content and isinstance(content['canonicalUrl'], dict):
                        link = content['canonicalUrl'].get('url')

                    current_stock_news_to_insert.append((
                        stock_code,
                        uuid,
                        title,
                        formatted_datetime,
                        summary,
                        link
                    ))
                
                # --- 存储部分 (保持不变) ---
                if current_stock_news_to_insert:
                    inserted_count = insert_news_data(conn, current_stock_news_to_insert)
                    logging.info(f"成功向数据库插入了 {inserted_count} 条关于 {stock_code} 的新记录。")
                    total_new_entries += inserted_count

            except Exception as e:
                logging.error(f"处理股票 {stock_code} 时发生未知错误: {e}")
            
            delay = random.uniform(*DELAY_RANGE)
            logging.info(f"暂停 {delay:.2f} 秒...")
            time.sleep(delay)

        logging.info(f"所有股票处理完毕。总共向数据库添加了 {total_new_entries} 条全新的新闻记录。")

    finally:
        if conn:
            conn.close()
            logging.info("数据库连接已关闭。")

# --- 主程序入口 ---
if __name__ == "__main__":
    fetch_and_store_news_fixed()
    logging.info("新闻抓取任务全部完成！")