import yfinance as yf
import sqlite3
from datetime import datetime, timezone
import time
import logging
import random

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

# --- Database Functions (Unaltered) ---
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
        logging.error(f"Failed to create news table: {e}")

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
        logging.error(f"Database news insertion failed: {e}")
        conn.rollback()
        return 0

# --- Main Function (Fixed for new data structure) ---
def fetch_and_store_news_fixed():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        logging.info("Database connection opened.")
        create_news_table(conn)
        
        total_new_entries = 0
        for i, stock_code in enumerate(HSI_COMPONENTS):
            logging.info(f"--- Fetching news {i+1}/{len(HSI_COMPONENTS)}: {stock_code} ---")
            
            current_stock_news_to_insert = []
            try:
                ticker = yf.Ticker(stock_code)
                news_list = ticker.news

                if not news_list:
                    logging.warning(f"No news found for stock {stock_code}.")
                    time.sleep(1)
                    continue

                logging.info(f"Successfully fetched {len(news_list)} news items for {stock_code}, now processing...")

                for news_item in news_list:
                    # --- Core Change: Extracting info based on the new data structure ---
                    
                    # 1. Check if essential data exists
                    if 'id' not in news_item or 'content' not in news_item or 'pubDate' not in news_item['content']:
                        logging.warning("Skipping one news item with incomplete format.")
                        continue
                    
                    content = news_item['content']
                    
                    # 2. Get the data
                    uuid = news_item['id']
                    title = content.get('title')
                    summary = content.get('summary')
                    
                    # 3. Parse the new date format (from '2025-06-13T21:04:32Z' to 'YYYY-MM-DD HH:MM:SS')
                    try:
                        # fromisoformat can directly handle 'Z' (Zulu time / UTC)
                        dt_object_utc = datetime.fromisoformat(content['pubDate'])
                        # Convert to local timezone or keep as UTC, then format
                        formatted_datetime = dt_object_utc.strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        logging.warning(f"Could not parse date '{content.get('pubDate')}', skipping this news item.")
                        continue

                    # 4. Safely get the link
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
                
                # --- Storage Part (Unaltered) ---
                if current_stock_news_to_insert:
                    inserted_count = insert_news_data(conn, current_stock_news_to_insert)
                    logging.info(f"Successfully inserted {inserted_count} new records for {stock_code} into the database.")
                    total_new_entries += inserted_count

            except Exception as e:
                logging.error(f"An unknown error occurred while processing stock {stock_code}: {e}")
            
            delay = random.uniform(*DELAY_RANGE)
            logging.info(f"Pausing for {delay:.2f} seconds...")
            time.sleep(delay)

        logging.info(f"All stocks processed. A total of {total_new_entries} new news records were added to the database.")

    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

# --- Main Program Entry Point ---
if __name__ == "__main__":
    fetch_and_store_news_fixed()
    logging.info("News fetching task completed!")