import sqlite3
import random
from datetime import datetime, timedelta
import logging

# --- Configuration ---
DATABASE_FILE = "stock_data.db"
# Ensure this list is consistent with your other scripts
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
MOCK_MODELS = ['AlphaModel', 'BetaTrend'] # Simulate two different prediction models

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_predictions_table(conn):
    """Creates the stock_predictions table if it doesn't exist."""
    try:
        with conn:
            cursor = conn.cursor()
            # Define what the future real prediction table should look like
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
        logging.error(f"Failed to create predictions table: {e}")

def generate_and_store_predictions():
    """Generates and stores mock prediction data for all stocks."""
    conn = sqlite3.connect(DATABASE_FILE)
    create_predictions_table(conn)
    
    all_predictions_to_insert = []

    for i, stock_code in enumerate(HSI_COMPONENTS):
        logging.info(f"--- Generating predictions {i+1}/{len(HSI_COMPONENTS)}: {stock_code} ---")
        
        # 1. Get the latest closing price from the stock_data table as a baseline
        cursor = conn.cursor()
        cursor.execute(
            "SELECT trade_date, close_price FROM stock_data WHERE stock_code = ? ORDER BY trade_date DESC LIMIT 1",
            (stock_code,)
        )
        last_data = cursor.fetchone()

        if not last_data:
            logging.warning(f"No historical data found for {stock_code} in the database. Cannot generate predictions.")
            continue
        
        last_date_str, last_price = last_data
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        logging.info(f"Found latest data for {stock_code}: Date={last_date_str}, Close Price={last_price:.2f}")

        # 2. Generate future prediction data for each mock model
        for model in MOCK_MODELS:
            current_price = last_price
            for i in range(1, 8): # Generate predictions for the next 7 periods
                # Increment the prediction date
                prediction_date = last_date + timedelta(days=i * 7)
                # Price fluctuates randomly based on the previous day's price
                price_fluctuation = random.uniform(-0.03, 0.035) # Fluctuation range
                current_price *= (1 + price_fluctuation)
                
                all_predictions_to_insert.append((
                    stock_code,
                    model,
                    prediction_date.strftime('%Y-%m-%d'),
                    round(current_price, 2)
                ))
    
    if not all_predictions_to_insert:
        logging.error("Failed to generate any prediction data.")
        conn.close()
        return

    # 3. Batch write to the database using INSERT OR REPLACE. If a record exists, it will be replaced.
    # This allows you to run this script repeatedly to "refresh" the fake data.
    logging.info(f"Preparing to insert {len(all_predictions_to_insert)} prediction records into the database...")
    try:
        with conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT OR REPLACE INTO stock_predictions (
                    stock_code, model_name, prediction_date, predicted_price
                ) VALUES (?, ?, ?, ?);
            """
            cursor.executemany(insert_query, all_predictions_to_insert)
            logging.info(f"Successfully inserted or replaced {cursor.rowcount} prediction records in the database.")
    except sqlite3.Error as e:
        logging.error(f"Database prediction data insertion failed: {e}")
    finally:
        conn.close()
        logging.info("Prediction database connection closed.")

if __name__ == "__main__":
    generate_and_store_predictions()
    logging.info("Mock prediction data generation task completed!")