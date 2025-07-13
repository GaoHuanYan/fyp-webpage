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


END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=365 * 1)
DELAY_RANGE = (5, 10)  


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_tables(conn):
    """Creates tables using SQLite syntax."""
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
        logging.error(f"Failed to create tables: {e}")

def fetch_all_data():
    """
    Core function: Fetches all stock data one by one and saves it to SQLite in a single batch.
    """
    all_rows_to_insert = []
    failed_stocks = []


    for i, stock_code in enumerate(HSI_COMPONENTS):
        logging.info(f"--- Processing {i+1}/{len(HSI_COMPONENTS)}: {stock_code} ---")
        try:
            ticker = yf.Ticker(stock_code)
            stock_data = ticker.history(start=START_DATE, end=END_DATE)

            if stock_data.empty:
                logging.warning(f"No historical data found for stock {stock_code}.")
                continue

            for trade_date, row in stock_data.iterrows():
                all_rows_to_insert.append((
                    stock_code,
                    trade_date.strftime('%Y-%m-%d'), 
                    None if pd.isna(row['Open']) else float(row['Open']),
                    None if pd.isna(row['High']) else float(row['High']),
                    None if pd.isna(row['Low']) else float(row['Low']),
                    None if pd.isna(row['Close']) else float(row['Close']),
                    None if pd.isna(row['Volume']) else int(row['Volume']),
                    None if pd.isna(row['Dividends']) else float(row['Dividends']),
                    None if pd.isna(row['Stock Splits']) else float(row['Stock Splits'])
                ))
            logging.info(f"Successfully fetched {len(stock_data)} records for {stock_code}.")

        except Exception as e:
            logging.error(f"Failed to fetch historical data for stock {stock_code}: {e}")
            failed_stocks.append(stock_code)
        
        delay = random.uniform(*DELAY_RANGE)
        logging.info(f"Pausing for {delay:.2f} seconds...")
        time.sleep(delay)

    if not all_rows_to_insert:
        logging.error("Failed to fetch any stock data. Database will not be written to.")
        return

    logging.info(f"Preparing to insert {len(all_rows_to_insert)} records into the database in a single batch...")
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        create_tables(conn) 
        cursor = conn.cursor()

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
        
        cursor.executemany(insert_query, all_rows_to_insert)
        conn.commit()
        logging.info(f"Successfully batch inserted/updated {cursor.rowcount} records in the database.")

    except sqlite3.Error as e:
        logging.error(f"Database batch insert operation failed: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")
    
    if failed_stocks:
        logging.warning(f"The following stocks failed to download: {failed_stocks}")

if __name__ == "__main__":
    if os.path.exists(DATABASE_FILE):
        logging.warning(f"Old database file '{DATABASE_FILE}' found, deleting...")
        os.remove(DATABASE_FILE)
        
    fetch_all_data()
    logging.info("Data fetching task completed!")