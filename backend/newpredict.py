import sqlite3
import numpy as np
import torch
from datetime import datetime, timedelta
import logging
from model import StockMixer
import os

# --- Configuration ---
DATABASE_FILE = "stock_data.db"
NPY_FILE = "stock_data_max_values.npy"
MODEL_PATH = "best_model.pth"
MODEL_NAME = "StockMixer"
TIME_STEPS = 16


HSI_COMPONENTS_FOR_MODEL = [
    "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK", "0011.HK", "0012.HK", 
    "0016.HK", "0066.HK", "0101.HK", "0267.HK", "0291.HK", "0386.HK", "0388.HK", 
    "0688.HK", "0762.HK", "0857.HK", "0883.HK", "0939.HK", "0941.HK", "1038.HK", 
    "1398.HK", "2318.HK", "2388.HK", "2628.HK", "0836.HK", "1044.HK", "1211.HK", 
    "2319.HK", "2899.HK", "0322.HK", "1109.HK", "3968.HK", "0992.HK", "1299.HK", 
    "1928.HK", "0027.HK", "0175.HK", "0316.HK", "0823.HK", "0868.HK", "0960.HK", 
    "1099.HK", "1177.HK", "1929.HK", "2313.HK", "2688.HK", "0669.HK", "0881.HK", 
    "0981.HK", "2331.HK", "0285.HK", "1093.HK", "1997.HK", "2020.HK", "1088.HK", 
    "3988.HK", "0700.HK", "0288.HK", "0968.HK", "1378.HK", "2382.HK", "0241.HK", 
    "1113.HK", "1810.HK", "3690.HK", "6862.HK", "2359.HK", "3692.HK", "1876.HK", 
    "9988.HK", "9999.HK", "9618.HK", "9633.HK", "9901.HK", "1209.HK", "6618.HK", 
    "2269.HK", "6690.HK", "1024.HK", "9888.HK", "9961.HK", "2015.HK",
]

# HSI_COMPONENTS_TO_PREDICT: This list contains only the stocks you want to save to the database.
# We have excluded "^HSI" from the list above.
HSI_COMPONENTS_TO_PREDICT = [stock for stock in HSI_COMPONENTS_FOR_MODEL if stock != "^HSI"]


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def predict(input_data: np.ndarray) -> np.ndarray:
    """Uses the trained model to make predictions. This function is now tightly coupled with the model configuration."""
    logging.info("Starting model prediction...")
    # Check if the input data matches the model configuration
    if input_data.shape != (len(HSI_COMPONENTS_FOR_MODEL), TIME_STEPS, 5):
        raise ValueError(f"Incorrect input data shape! Model requires ({len(HSI_COMPONENTS_FOR_MODEL)}, {TIME_STEPS}, 5), but got {input_data.shape}")

    max_values = np.load(NPY_FILE)
    if max_values.shape[0] != len(HSI_COMPONENTS_FOR_MODEL):
        raise ValueError(f"The number of stocks in the .npy file ({max_values.shape[0]}) does not match the model configuration ({len(HSI_COMPONENTS_FOR_MODEL)}).")

    normalized_data = np.zeros_like(input_data, dtype=np.float32)
    for i in range(input_data.shape[0]):
        max_vals_stock = max_values[i]
        if np.isnan(max_vals_stock).any(): continue
        safe_max_values = np.where(max_vals_stock == 0, 1, max_vals_stock)
        for k in range(input_data.shape[2]):
            normalized_data[i, :, k] = input_data[i, :, k] / safe_max_values[k]
    
    logging.info("Data normalization complete.")

    model = StockMixer(
        stocks=len(HSI_COMPONENTS_FOR_MODEL), # Initialize the model using the full count of stocks, including the index
        time_steps=TIME_STEPS, channels=5, market=20, scale=3
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
    logging.info("Model loaded and set to evaluation mode.")

    input_tensor = torch.tensor(normalized_data, dtype=torch.float32)
    with torch.no_grad():
        output = model(input_tensor).reshape(-1).numpy()

    denormalized_output = np.zeros_like(output)
    for i in range(len(output)):
        max_vals_stock = max_values[i]
        if np.isnan(max_vals_stock).any():
            denormalized_output[i] = np.nan
            continue
        denormalized_output[i] = output[i] * max_vals_stock[-1]

    logging.info("Model prediction and denormalization complete.")
    return denormalized_output

def create_predictions_table(conn):
    """Creates or updates the predictions table, this function does not need changes."""
    # ... (Code is identical to the previous version)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, stock_code TEXT NOT NULL, model_name TEXT NOT NULL,
                prediction_date TEXT NOT NULL, predicted_price REAL NOT NULL, predicted_change_pct REAL, 
                created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(stock_code, model_name, prediction_date)
            );
            """)
            cursor.execute("PRAGMA table_info(stock_predictions);")
            columns = [info[1] for info in cursor.fetchall()]
            if 'predicted_change_pct' not in columns:
                cursor.execute("ALTER TABLE stock_predictions ADD COLUMN predicted_change_pct REAL;")
            logging.info("Table 'stock_predictions' checked/updated successfully.")
    except sqlite3.Error as e:
        logging.error(f"Failed to create/update predictions table: {e}")
        raise

def generate_and_store_real_predictions():
    """Fetches data, predicts, calculates percentage change, and stores only the component stock results in the database."""
    for file_path in [DATABASE_FILE, NPY_FILE, MODEL_PATH]:
        if not os.path.exists(file_path):
            logging.error(f"CRITICAL: Required file not found: '{file_path}'. Aborting.")
            return

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        create_predictions_table(conn)
        
        input_data_list = []
        latest_date_str = None
        last_close_prices = {} 
        logging.info(f"Fetching latest data for all {len(HSI_COMPONENTS_FOR_MODEL)} tickers required by the model...")
        for stock_code in HSI_COMPONENTS_FOR_MODEL:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT high_price, low_price, open_price, volume, close_price, trade_date FROM stock_data WHERE stock_code = ? ORDER BY trade_date DESC LIMIT ?",
                (stock_code, TIME_STEPS)
            )
            rows = cursor.fetchall()

            if len(rows) < TIME_STEPS:
                logging.warning(f"Insufficient data for {stock_code}: Found {len(rows)}/{TIME_STEPS}. This stock will be skipped in prediction.")
                input_data_list.append(np.zeros((TIME_STEPS, 5)))
                last_close_prices[stock_code] = None
            else:
                rows.reverse()
                if latest_date_str is None:
                    latest_date_str = rows[-1][5]
                stock_features = [row[:5] for row in rows]
                input_data_list.append(stock_features)
                last_close_prices[stock_code] = rows[-1][4]

        if latest_date_str is None:
            logging.error("CRITICAL: No stocks had sufficient data. Cannot make any predictions. Aborting.")
            return

        input_data_np = np.array(input_data_list, dtype=np.float32)
        # The model will return predicted prices for all stocks (including ^HSI)
        predicted_prices = predict(input_data_np)

        prediction_date = datetime.strptime(latest_date_str, '%Y-%m-%d') + timedelta(days=1)
        prediction_date_str = prediction_date.strftime('%Y-%m-%d')
        logging.info(f"Predictions are for date: {prediction_date_str}")
        
        all_predictions_to_insert = []
        
        logging.info("Filtering predictions to store only component stocks (excluding index)...")
        for i, stock_code in enumerate(HSI_COMPONENTS_FOR_MODEL):
            # If the current stock is one we don't want to save (like the index), skip it
            if stock_code not in HSI_COMPONENTS_TO_PREDICT:
                logging.info(f"Skipping DB insertion for '{stock_code}' as it is not in the target prediction list.")
                continue

            predicted_price = predicted_prices[i]
            last_close = last_close_prices.get(stock_code)
            
            if np.isnan(predicted_price) or last_close is None or last_close == 0:
                logging.warning(f"Skipping DB insertion for {stock_code} due to invalid price or missing last close.")
                continue
            
            change_pct = ((predicted_price - last_close) / last_close) * 100
            
            all_predictions_to_insert.append((
                stock_code, MODEL_NAME, prediction_date_str,
                round(float(predicted_price), 2),
                round(float(change_pct), 2)
            ))

        if not all_predictions_to_insert:
            logging.error("CRITICAL: Failed to generate any valid prediction data to store.")
            return

        logging.info(f"Preparing to insert {len(all_predictions_to_insert)} valid prediction records...")
        cursor = conn.cursor()
        insert_query = "INSERT OR REPLACE INTO stock_predictions (stock_code, model_name, prediction_date, predicted_price, predicted_change_pct) VALUES (?, ?, ?, ?, ?);"
        cursor.executemany(insert_query, all_predictions_to_insert)
        conn.commit()
        logging.info(f"Successfully inserted/replaced {cursor.rowcount} prediction records.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    generate_and_store_real_predictions()
    logging.info("Prediction and storage task completed!")