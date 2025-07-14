import sqlite3
import pandas as pd
import numpy as np
import logging
import os

DATABASE_FILE = "stock_data.db"
NPY_FILE = "stock_data_max_values.npy"

# This list must be identical to the one used in your prediction script and model training!
# It determines the order of the data in the .npy file.
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



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_max_values_file():
    """Reads data from the database, calculates max values, and saves to a .npy file. Uses NaN as a placeholder if data is missing."""
    if not os.path.exists(DATABASE_FILE):
        logging.error(f"Database file '{DATABASE_FILE}' does not exist. Please run `fetch_data.py` first.")
        return

    logging.info(f"Starting to read data from '{DATABASE_FILE}' to generate '{NPY_FILE}'...")
    
    feature_order = ['high_price', 'low_price', 'open_price', 'volume', 'close_price']
    all_max_values = []
    
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        
        for stock_code in HSI_COMPONENTS_FOR_MODEL:
            query = f"SELECT {', '.join(feature_order)} FROM stock_data WHERE stock_code = ?"
            df = pd.read_sql_query(query, conn, params=(stock_code,))

            # --- The main change is here ---
            if df.empty:
                # If data is empty, log a warning and add a row of NaNs as a placeholder
                logging.warning(f"Data for stock {stock_code} is missing in the database. Using NaN as a placeholder in the .npy file.")
                nan_row = [np.nan] * len(feature_order)
                all_max_values.append(nan_row)
            else:
                # If data exists, calculate max values normally
                max_values_for_stock = df.max().values
                all_max_values.append(max_values_for_stock)
        
        final_max_values_array = np.array(all_max_values, dtype=np.float32)
        
        # This shape check will now always pass because we always append a row
        expected_shape = (len(HSI_COMPONENTS_FOR_MODEL), len(feature_order))
        if final_max_values_array.shape != expected_shape:
            # This error should theoretically not happen, but it's kept as a safety check
            logging.error(f"The calculated max values array has an incorrect shape! Expected {expected_shape}, got {final_max_values_array.shape}")
            return

        np.save(NPY_FILE, final_max_values_array)
        logging.info(f"Successfully created '{NPY_FILE}' file with shape: {final_max_values_array.shape}")

    except sqlite3.Error as e:
        logging.error(f"Database operation failed: {e}")
    except Exception as e:
        logging.error(f"An unknown error occurred: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    generate_max_values_file()