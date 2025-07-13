# # # import sqlite3
# # # import random
# # # from datetime import datetime, timedelta
# # # import logging

# # # # --- Configuration ---
# # # DATABASE_FILE = "stock_data.db"
# # # # Ensure this list is consistent with your other scripts
# # # HSI_COMPONENTS = [
# # #     "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK", "0011.HK", "0012.HK", 
# # #     "0016.HK", "0017.HK", "0027.HK", "0066.HK", "0101.HK", "0175.HK", "0241.HK", 
# # #     "0285.HK", "0288.HK", "0291.HK", "0316.HK", "0322.HK", "0386.HK", "0388.HK", 
# # #     "0669.HK", "0688.HK", "0700.HK", "0762.HK", "0823.HK", "0836.HK", "0857.HK", 
# # #     "0868.HK", "0881.HK", "0883.HK", "0939.HK", "0941.HK", "0960.HK", "0968.HK", 
# # #     "0981.HK", "0992.HK", "1024.HK", "1038.HK", "1044.HK", "1088.HK", "1093.HK", 
# # #     "1099.HK", "1109.HK", "1113.HK", "1177.HK", "1209.HK", "1211.HK", "1299.HK", 
# # #     "1378.HK", "1398.HK", "1810.HK", "1876.HK", "1928.HK", "1929.HK", "1997.HK", 
# # #     "2015.HK", "2020.HK", "2057.HK", "2269.HK", "2313.HK", "2318.HK", "2319.HK", 
# # #     "2331.HK", "2359.HK", "2382.HK", "2388.HK", "2628.HK", "2688.HK", "2899.HK", 
# # #     "3690.HK", "3692.HK", "3968.HK", "3988.HK", "6618.HK", "6690.HK", "6862.HK", 
# # #     "9618.HK", "9633.HK", "9888.HK", "9901.HK", "9961.HK", "9988.HK", "9999.HK",
# # # ]
# # # MOCK_MODELS = ['AlphaModel', 'BetaTrend'] # Simulate two different prediction models

# # # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # # def create_predictions_table(conn):
# # #     """Creates the stock_predictions table if it doesn't exist."""
# # #     try:
# # #         with conn:
# # #             cursor = conn.cursor()
# # #             # Define what the future real prediction table should look like
# # #             cursor.execute("""
# # #             CREATE TABLE IF NOT EXISTS stock_predictions (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 stock_code TEXT NOT NULL,
# # #                 model_name TEXT NOT NULL,
# # #                 prediction_date TEXT NOT NULL,
# # #                 predicted_price REAL NOT NULL,
# # #                 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
# # #                 UNIQUE(stock_code, model_name, prediction_date)
# # #             );
# # #             """)
# # #             logging.info("Table 'stock_predictions' checked/created successfully.")
# # #     except sqlite3.Error as e:
# # #         logging.error(f"Failed to create predictions table: {e}")

# # # def generate_and_store_predictions():
# # #     """Generates and stores mock prediction data for all stocks."""
# # #     conn = sqlite3.connect(DATABASE_FILE)
# # #     create_predictions_table(conn)
    
# # #     all_predictions_to_insert = []

# # #     for i, stock_code in enumerate(HSI_COMPONENTS):
# # #         logging.info(f"--- Generating predictions {i+1}/{len(HSI_COMPONENTS)}: {stock_code} ---")
        
# # #         # 1. Get the latest closing price from the stock_data table as a baseline
# # #         cursor = conn.cursor()
# # #         cursor.execute(
# # #             "SELECT trade_date, close_price FROM stock_data WHERE stock_code = ? ORDER BY trade_date DESC LIMIT 1",
# # #             (stock_code,)
# # #         )
# # #         last_data = cursor.fetchone()

# # #         if not last_data:
# # #             logging.warning(f"No historical data found for {stock_code} in the database. Cannot generate predictions.")
# # #             continue
        
# # #         last_date_str, last_price = last_data
# # #         last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
# # #         logging.info(f"Found latest data for {stock_code}: Date={last_date_str}, Close Price={last_price:.2f}")

# # #         # 2. Generate future prediction data for each mock model
# # #         for model in MOCK_MODELS:
# # #             current_price = last_price
# # #             for i in range(1, 8): # Generate predictions for the next 7 periods
# # #                 # Increment the prediction date
# # #                 prediction_date = last_date + timedelta(days=i * 7)
# # #                 # Price fluctuates randomly based on the previous day's price
# # #                 price_fluctuation = random.uniform(-0.03, 0.035) # Fluctuation range
# # #                 current_price *= (1 + price_fluctuation)
                
# # #                 all_predictions_to_insert.append((
# # #                     stock_code,
# # #                     model,
# # #                     prediction_date.strftime('%Y-%m-%d'),
# # #                     round(current_price, 2)
# # #                 ))
    
# # #     if not all_predictions_to_insert:
# # #         logging.error("Failed to generate any prediction data.")
# # #         conn.close()
# # #         return

# # #     # 3. Batch write to the database using INSERT OR REPLACE. If a record exists, it will be replaced.
# # #     # This allows you to run this script repeatedly to "refresh" the fake data.
# # #     logging.info(f"Preparing to insert {len(all_predictions_to_insert)} prediction records into the database...")
# # #     try:
# # #         with conn:
# # #             cursor = conn.cursor()
# # #             insert_query = """
# # #                 INSERT OR REPLACE INTO stock_predictions (
# # #                     stock_code, model_name, prediction_date, predicted_price
# # #                 ) VALUES (?, ?, ?, ?);
# # #             """
# # #             cursor.executemany(insert_query, all_predictions_to_insert)
# # #             logging.info(f"Successfully inserted or replaced {cursor.rowcount} prediction records in the database.")
# # #     except sqlite3.Error as e:
# # #         logging.error(f"Database prediction data insertion failed: {e}")
# # #     finally:
# # #         conn.close()
# # #         logging.info("Prediction database connection closed.")

# # # if __name__ == "__main__":
# # #     generate_and_store_predictions()
# # #     logging.info("Mock prediction data generation task completed!")

# # import sqlite3
# # import numpy as np
# # import torch
# # from datetime import datetime, timedelta
# # import logging
# # from model import StockMixer # 从 model.py 导入模型类

# # # --- 配置 ---
# # DATABASE_FILE = "stock_data.db"
# # MODEL_NAME = "StockMixer" # 使用真实模型的名称
# # TIME_STEPS = 16 # 模型需要的时间步长
# # # 股票列表，顺序必须与训练和 stock_data_max_values.npy 文件严格一致
# # HSI_COMPONENTS = [
# #     "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK", "0011.HK", "0012.HK", 
# #     "0016.HK", "0017.HK", "0027.HK", "0066.HK", "0101.HK", "0175.HK", "0241.HK", 
# #     "0285.HK", "0288.HK", "0291.HK", "0316.HK", "0322.HK", "0386.HK", "0388.HK", 
# #     "0669.HK", "0688.HK", "0700.HK", "0762.HK", "0823.HK", "0836.HK", "0857.HK", 
# #     "0868.HK", "0881.HK", "0883.HK", "0939.HK", "0941.HK", "0960.HK", "0968.HK", 
# #     "0981.HK", "0992.HK", "1024.HK", "1038.HK", "1044.HK", "1088.HK", "1093.HK", 
# #     "1099.HK", "1109.HK", "1113.HK", "1177.HK", "1209.HK", "1211.HK", "1299.HK", 
# #     "1378.HK", "1398.HK", "1810.HK", "1876.HK", "1928.HK", "1929.HK", "1997.HK", 
# #     "2015.HK", "2020.HK", "2057.HK", "2269.HK", "2313.HK", "2318.HK", "2319.HK", 
# #     "2331.HK", "2359.HK", "2382.HK", "2388.HK", "2628.HK", "2688.HK", "2899.HK", 
# #     "3690.HK", "3692.HK", "3968.HK", "3988.HK", "6618.HK", "6690.HK", "6862.HK", 
# #     "9618.HK", "9633.HK", "9888.HK", "9901.HK", "9961.HK", "9988.HK", "9999.HK",
# # ]

# # # 设置日志记录
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # # --- 真实模型预测函数 (来自你的脚本) ---
# # # 5个特征，依次：'High' 'Low' 'Open' 'Volume' 'Close'
# # def predict(input_data: np.ndarray) -> np.ndarray:
# #     """使用训练好的StockMixer模型进行预测"""
# #     logging.info("开始执行模型预测...")
# #     # 检查输入数据维度
# #     if input_data.shape != (len(HSI_COMPONENTS), TIME_STEPS, 5):
# #         raise ValueError(f"输入数据的形状不正确! 需要 (83, 16, 5), 但得到 {input_data.shape}")

# #     max_values = np.load('stock_data_max_values.npy')
# #     # 标准化
# #     normalized_data = np.zeros_like(input_data, dtype=np.float32)
# #     for i in range(input_data.shape[0]):
# #         for k in range(input_data.shape[2]):
# #             normalized_data[i, :, k] = input_data[i, :, k] / max_values[i, k]
    
# #     logging.info("数据标准化完成。")

# #     model = StockMixer(
# #         stocks=len(HSI_COMPONENTS),
# #         time_steps=TIME_STEPS,
# #         channels=5,
# #         market=20,
# #         scale=3
# #     )
# #     # 加载模型权重，确保模型在CPU上运行
# #     model.load_state_dict(torch.load('best_model.pth', map_location=torch.device('cpu')))
# #     model.eval()
# #     logging.info("模型加载完成并设置为评估模式。")

# #     input_tensor = torch.tensor(normalized_data, dtype=torch.float32)
# #     with torch.no_grad():
# #         output = model(input_tensor) # 模型输出形状: (83, 1)
# #         # 反标准化
# #         output = output.reshape(-1).numpy() # 转换为 (83,) 的numpy数组
# #         denormalized_output = output * max_values[:, -1] # 使用最后一列(Close)的最大值进行反标准化
    
# #     logging.info("模型预测和反标准化完成。")
# #     return denormalized_output

# # # --- 数据库操作函数 ---
# # def create_predictions_table(conn):
# #     """创建用于存储预测结果的表 (如果不存在)"""
# #     try:
# #         with conn:
# #             cursor = conn.cursor()
# #             cursor.execute("""
# #             CREATE TABLE IF NOT EXISTS stock_predictions (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 stock_code TEXT NOT NULL,
# #                 model_name TEXT NOT NULL,
# #                 prediction_date TEXT NOT NULL,
# #                 predicted_price REAL NOT NULL,
# #                 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
# #                 UNIQUE(stock_code, model_name, prediction_date)
# #             );
# #             """)
# #             logging.info("数据表 'stock_predictions' 检查/创建成功。")
# #     except sqlite3.Error as e:
# #         logging.error(f"创建预测表失败: {e}")
# #         raise

# # def generate_and_store_real_predictions():
# #     """获取最新数据，使用真实模型进行预测，并将结果存入数据库。"""
# #     conn = None
# #     try:
# #         conn = sqlite3.connect(DATABASE_FILE)
# #         create_predictions_table(conn)
        
# #         input_data_list = []
# #         latest_date_str = None
        
# #         logging.info("开始从数据库为所有股票获取最新数据...")
# #         # 1. 从数据库为每只股票获取输入数据
# #         for stock_code in HSI_COMPONENTS:
# #             cursor = conn.cursor()
# #             # 查询模型所需的5个特征，并按日期升序排列
# #             # 注意：SELECT的字段顺序必须是 'High', 'Low', 'Open', 'Volume', 'Close'
# #             cursor.execute(
# #                 """
# #                 SELECT high_price, low_price, open_price, volume, close_price, trade_date 
# #                 FROM stock_data 
# #                 WHERE stock_code = ? 
# #                 ORDER BY trade_date DESC 
# #                 LIMIT ?
# #                 """,
# #                 (stock_code, TIME_STEPS)
# #             )
# #             rows = cursor.fetchall()

# #             if len(rows) != TIME_STEPS:
# #                 logging.error(f"股票 {stock_code} 数据不足 {len(rows)}/{TIME_STEPS} 条，无法进行预测。请检查数据源。")
# #                 return # 中断执行

# #             # 数据是按日期降序获取的，需要反转为升序（时间从小到大）
# #             rows.reverse()
            
# #             # 记录最新的日期，用于确定预测日期
# #             if latest_date_str is None:
# #                 latest_date_str = rows[-1][5] # 最后一列是 trade_date

# #             # 提取前5个特征，忽略日期
# #             stock_features = [row[:5] for row in rows]
# #             input_data_list.append(stock_features)

# #         logging.info("所有股票的数据均已成功获取。")

# #         # 2. 准备模型输入并进行预测
# #         input_data_np = np.array(input_data_list, dtype=np.float32)
# #         predicted_prices = predict(input_data_np)

# #         # 3. 准备要插入数据库的数据
# #         prediction_date = datetime.strptime(latest_date_str, '%Y-%m-%d') + timedelta(days=1)
# #         prediction_date_str = prediction_date.strftime('%Y-%m-%d')
# #         logging.info(f"所有预测都是针对日期: {prediction_date_str}")
        
# #         all_predictions_to_insert = []
# #         for i, stock_code in enumerate(HSI_COMPONENTS):
# #             all_predictions_to_insert.append((
# #                 stock_code,
# #                 MODEL_NAME,
# #                 prediction_date_str,
# #                 round(float(predicted_prices[i]), 2) # 确保价格是浮点数并四舍五入
# #             ))

# #         # 4. 批量写入数据库
# #         if not all_predictions_to_insert:
# #             logging.error("未能生成任何预测数据。")
# #             return

# #         logging.info(f"准备将 {len(all_predictions_to_insert)} 条预测记录写入数据库...")
# #         cursor = conn.cursor()
# #         insert_query = """
# #             INSERT OR REPLACE INTO stock_predictions (
# #                 stock_code, model_name, prediction_date, predicted_price
# #             ) VALUES (?, ?, ?, ?);
# #         """
# #         cursor.executemany(insert_query, all_predictions_to_insert)
# #         conn.commit() # 提交事务
# #         logging.info(f"成功向数据库中插入或替换了 {cursor.rowcount} 条预测记录。")

# #     except sqlite3.Error as e:
# #         logging.error(f"数据库操作失败: {e}")
# #     except FileNotFoundError as e:
# #         logging.error(f"文件未找到，请确保模型和数据文件存在: {e}")
# #     except Exception as e:
# #         logging.error(f"发生未知错误: {e}")
# #     finally:
# #         if conn:
# #             conn.close()
# #             logging.info("数据库连接已关闭。")

# # if __name__ == "__main__":
# #     generate_and_store_real_predictions()
# #     logging.info("真实预测数据生成与存储任务完成！")


# # import sqlite3
# # import numpy as np
# # import torch
# # from datetime import datetime, timedelta
# # import logging
# # from model import StockMixer # Import the model class from model.py

# # # --- Configuration ---
# # DATABASE_FILE = "stock_data.db"
# # MODEL_NAME = "StockMixer" # The name of the real model
# # TIME_STEPS = 16 # The number of time steps required by the model
# # # The list of stocks. The order must be strictly consistent with the training and the stock_data_max_values.npy file.
# # HSI_COMPONENTS = [
# #     "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK", "0011.HK", "0012.HK", 
# #     "0016.HK", "0017.HK", "0027.HK", "0066.HK", "0101.HK", "0175.HK", "0241.HK", 
# #     "0285.HK", "0288.HK", "0291.HK", "0316.HK", "0322.HK", "0386.HK", "0388.HK", 
# #     "0669.HK", "0688.HK", "0700.HK", "0762.HK", "0823.HK", "0836.HK", "0857.HK", 
# #     "0868.HK", "0881.HK", "0883.HK", "0939.HK", "0941.HK", "0960.HK", "0968.HK", 
# #     "0981.HK", "0992.HK", "1024.HK", "1038.HK", "1044.HK", "1088.HK", "1093.HK", 
# #     "1099.HK", "1109.HK", "1113.HK", "1177.HK", "1209.HK", "1211.HK", "1299.HK", 
# #     "1378.HK", "1398.HK", "1810.HK", "1876.HK", "1928.HK", "1929.HK", "1997.HK", 
# #     "2015.HK", "2020.HK", "2057.HK", "2269.HK", "2313.HK", "2318.HK", "2319.HK", 
# #     "2331.HK", "2359.HK", "2382.HK", "2388.HK", "2628.HK", "2688.HK", "2899.HK", 
# #     "3690.HK", "3692.HK", "3968.HK", "3988.HK", "6618.HK", "6690.HK", "6862.HK", 
# #     "9618.HK", "9633.HK", "9888.HK", "9901.HK", "9961.HK", "9988.HK", "9999.HK",
# # ]

# # # Set up logging
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # # --- Real Model Prediction Function (from your script) ---
# # # 5 features, in order: 'High', 'Low', 'Open', 'Volume', 'Close'
# # def predict(input_data: np.ndarray) -> np.ndarray:
# #     """Makes predictions using the trained StockMixer model."""
# #     logging.info("Starting model prediction...")
# #     # Check input data dimensions
# #     if input_data.shape != (len(HSI_COMPONENTS), TIME_STEPS, 5):
# #         raise ValueError(f"Incorrect shape for input data! Expected ({len(HSI_COMPONENTS)}, {TIME_STEPS}, 5), but got {input_data.shape}")

# #     max_values = np.load('stock_data_max_values.npy')
# #     # Normalization
# #     normalized_data = np.zeros_like(input_data, dtype=np.float32)
# #     for i in range(input_data.shape[0]):
# #         for k in range(input_data.shape[2]):
# #             normalized_data[i, :, k] = input_data[i, :, k] / max_values[i, k]
    
# #     logging.info("Data normalization complete.")

# #     model = StockMixer(
# #         stocks=len(HSI_COMPONENTS),
# #         time_steps=TIME_STEPS,
# #         channels=5,
# #         market=20,
# #         scale=3
# #     )
# #     # Load model weights, ensuring it runs on the CPU
# #     model.load_state_dict(torch.load('best_model.pth', map_location=torch.device('cpu')))
# #     model.eval()
# #     logging.info("Model loaded and set to evaluation mode.")

# #     input_tensor = torch.tensor(normalized_data, dtype=torch.float32)
# #     with torch.no_grad():
# #         output = model(input_tensor) # Model output shape: (83, 1)
# #         # Denormalization
# #         output = output.reshape(-1).numpy() # Convert to a numpy array of shape (83,)
# #         denormalized_output = output * max_values[:, -1] # Denormalize using the max value of the last column (Close)
    
# #     logging.info("Model prediction and denormalization complete.")
# #     return denormalized_output

# # # --- Database Operation Functions ---
# # def create_predictions_table(conn):
# #     """Creates the table to store prediction results (if it doesn't exist)."""
# #     try:
# #         with conn:
# #             cursor = conn.cursor()
# #             cursor.execute("""
# #             CREATE TABLE IF NOT EXISTS stock_predictions (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 stock_code TEXT NOT NULL,
# #                 model_name TEXT NOT NULL,
# #                 prediction_date TEXT NOT NULL,
# #                 predicted_price REAL NOT NULL,
# #                 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
# #                 UNIQUE(stock_code, model_name, prediction_date)
# #             );
# #             """)
# #             logging.info("Table 'stock_predictions' checked/created successfully.")
# #     except sqlite3.Error as e:
# #         logging.error(f"Failed to create predictions table: {e}")
# #         raise

# # def generate_and_store_real_predictions():
# #     """Fetches the latest data, makes predictions using the real model, and stores the results in the database."""
# #     conn = None
# #     try:
# #         conn = sqlite3.connect(DATABASE_FILE)
# #         create_predictions_table(conn)
        
# #         input_data_list = []
# #         latest_date_str = None
        
# #         logging.info("Starting to fetch the latest data for all stocks from the database...")
# #         # 1. Fetch input data for each stock from the database
# #         for stock_code in HSI_COMPONENTS:
# #             cursor = conn.cursor()
# #             # NOTE: The SELECT field order must be 'High', 'Low', 'Open', 'Volume', 'Close'
# #             cursor.execute(
# #                 """
# #                 SELECT high_price, low_price, open_price, volume, close_price, trade_date 
# #                 FROM stock_data 
# #                 WHERE stock_code = ? 
# #                 ORDER BY trade_date DESC 
# #                 LIMIT ?
# #                 """,
# #                 (stock_code, TIME_STEPS)
# #             )
# #             rows = cursor.fetchall()

# #             if len(rows) != TIME_STEPS:
# #                 logging.error(f"Insufficient data for stock {stock_code}: {len(rows)}/{TIME_STEPS} records found. Cannot make a prediction. Please check the data source.")
# #                 return # Abort execution

# #             # The data is fetched in descending date order, so it needs to be reversed to ascending (oldest to newest)
# #             rows.reverse()
            
# #             # Record the latest date to determine the prediction date
# #             if latest_date_str is None:
# #                 latest_date_str = rows[-1][5] # The last column is trade_date

# #             # Extract the first 5 features, ignoring the date
# #             stock_features = [row[:5] for row in rows]
# #             input_data_list.append(stock_features)

# #         logging.info("Data for all stocks has been successfully fetched.")

# #         # 2. Prepare model input and make predictions
# #         input_data_np = np.array(input_data_list, dtype=np.float32)
# #         predicted_prices = predict(input_data_np)

# #         # 3. Prepare the data to be inserted into the database
# #         prediction_date = datetime.strptime(latest_date_str, '%Y-%m-%d') + timedelta(days=1)
# #         prediction_date_str = prediction_date.strftime('%Y-%m-%d')
# #         logging.info(f"All predictions are for the date: {prediction_date_str}")
        
# #         all_predictions_to_insert = []
# #         for i, stock_code in enumerate(HSI_COMPONENTS):
# #             all_predictions_to_insert.append((
# #                 stock_code,
# #                 MODEL_NAME,
# #                 prediction_date_str,
# #                 round(float(predicted_prices[i]), 2) # Ensure the price is a float and round it
# #             ))

# #         # 4. Batch write to the database
# #         if not all_predictions_to_insert:
# #             logging.error("Failed to generate any prediction data.")
# #             return

# #         logging.info(f"Preparing to insert {len(all_predictions_to_insert)} prediction records into the database...")
# #         cursor = conn.cursor()
# #         insert_query = """
# #             INSERT OR REPLACE INTO stock_predictions (
# #                 stock_code, model_name, prediction_date, predicted_price
# #             ) VALUES (?, ?, ?, ?);
# #         """
# #         cursor.executemany(insert_query, all_predictions_to_insert)
# #         conn.commit() # Commit the transaction
# #         logging.info(f"Successfully inserted or replaced {cursor.rowcount} prediction records in the database.")

# #     except sqlite3.Error as e:
# #         logging.error(f"Database operation failed: {e}")
# #     except FileNotFoundError as e:
# #         logging.error(f"File not found. Please ensure model and data files exist: {e}")
# #     except Exception as e:
# #         logging.error(f"An unexpected error occurred: {e}")
# #     finally:
# #         if conn:
# #             conn.close()
# #             logging.info("Database connection closed.")

# # if __name__ == "__main__":
# #     generate_and_store_real_predictions()
# #     logging.info("Real prediction data generation and storage task completed!")
# import sqlite3
# import numpy as np
# import torch
# from datetime import datetime, timedelta
# import logging
# from model import StockMixer # Import the model class from model.py
# import os # Import os to check for file existence

# # --- Configuration ---
# DATABASE_FILE = "stock_data.db"
# NPY_FILE = "stock_data_max_values.npy"
# MODEL_PATH = "best_model.pth"
# MODEL_NAME = "StockMixer"
# TIME_STEPS = 16
# # The list of stocks. The order must be strictly consistent with the training and the .npy file.
# HSI_COMPONENTS = [
#     "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK", "0011.HK", "0012.HK", 
#     "0016.HK", "0017.HK", "0027.HK", "0066.HK", "0101.HK", "0175.HK", "0241.HK", 
#     "0285.HK", "0288.HK", "0291.HK", "0316.HK", "0322.HK", "0386.HK", "0388.HK", 
#     "0669.HK", "0688.HK", "0700.HK", "0762.HK", "0823.HK", "0836.HK", "0857.HK", 
#     "0868.HK", "0881.HK", "0883.HK", "0939.HK", "0941.HK", "0960.HK", "0968.HK", 
#     "0981.HK", "0992.HK", "1024.HK", "1038.HK", "1044.HK", "1088.HK", "1093.HK", 
#     "1099.HK", "1109.HK", "1113.HK", "1177.HK", "1209.HK", "1211.HK", "1299.HK", 
#     "1378.HK", "1398.HK", "1810.HK", "1876.HK", "1928.HK", "1929.HK", "1997.HK", 
#     "2015.HK", "2020.HK", "2057.HK", "2269.HK", "2313.HK", "2318.HK", "2319.HK", 
#     "2331.HK", "2359.HK", "2382.HK", "2388.HK", "2628.HK", "2688.HK", "2899.HK", 
#     "3690.HK", "3692.HK", "3968.HK", "3988.HK", "6618.HK", "6690.HK", "6862.HK", 
#     "9618.HK", "9633.HK", "9888.HK", "9901.HK", "9961.HK", "9988.HK", "9999.HK",
# ]

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Modified Model Prediction Function ---
# def predict(input_data: np.ndarray) -> np.ndarray:
#     """
#     Makes predictions using the trained StockMixer model.
#     Handles missing data by skipping prediction for specific stocks.
#     """
#     logging.info("Starting model prediction...")
#     if input_data.shape != (len(HSI_COMPONENTS), TIME_STEPS, 5):
#         raise ValueError(f"Incorrect shape for input data! Expected ({len(HSI_COMPONENTS)}, {TIME_STEPS}, 5), but got {input_data.shape}")

#     max_values = np.load(NPY_FILE)
    
#     # --- MODIFICATION 1: Handle NaN during Normalization ---
#     normalized_data = np.zeros_like(input_data, dtype=np.float32)
#     for i in range(input_data.shape[0]):
#         max_values_for_stock = max_values[i]
        
#         # Check if the max values for this stock are valid
#         if np.isnan(max_values_for_stock).any():
#             logging.warning(f"Max values for {HSI_COMPONENTS[i]} (index {i}) contain NaN. Skipping normalization for this stock.")
#             # Its normalized_data will remain all zeros, a neutral input
#             continue

#         # Replace zeros in max_values with 1 to avoid division by zero errors
#         safe_max_values = np.where(max_values_for_stock == 0, 1, max_values_for_stock)
        
#         # Normalize each feature
#         for k in range(input_data.shape[2]):
#             normalized_data[i, :, k] = input_data[i, :, k] / safe_max_values[k]
    
#     logging.info("Data normalization complete. Stocks with missing max values were skipped.")

#     model = StockMixer(
#         stocks=len(HSI_COMPONENTS), time_steps=TIME_STEPS,
#         channels=5, market=20, scale=3
#     )
#     model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
#     model.eval()
#     logging.info("Model loaded and set to evaluation mode.")

#     input_tensor = torch.tensor(normalized_data, dtype=torch.float32)
#     with torch.no_grad():
#         output = model(input_tensor)
#         output = output.reshape(-1).numpy()

#     # --- MODIFICATION 2: Handle NaN during Denormalization ---
#     denormalized_output = np.zeros_like(output)
#     for i in range(len(output)):
#         max_values_for_stock = max_values[i]
        
#         # If max values were invalid, mark the final prediction as NaN
#         if np.isnan(max_values_for_stock).any():
#             denormalized_output[i] = np.nan
#             continue
        
#         # Denormalize using the max value of the last column ('Close' price)
#         denormalized_output[i] = output[i] * max_values_for_stock[-1]

#     logging.info("Model prediction and denormalization complete.")
#     return denormalized_output

# # --- Database Operation Functions ---
# def create_predictions_table(conn):
#     """Creates the table to store prediction results (if it doesn't exist)."""
#     try:
#         with conn:
#             cursor = conn.cursor()
#             cursor.execute("""
#             CREATE TABLE IF NOT EXISTS stock_predictions (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT, stock_code TEXT NOT NULL, model_name TEXT NOT NULL,
#                 prediction_date TEXT NOT NULL, predicted_price REAL NOT NULL,
#                 created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(stock_code, model_name, prediction_date)
#             );
#             """)
#             logging.info("Table 'stock_predictions' checked/created successfully.")
#     except sqlite3.Error as e:
#         logging.error(f"Failed to create predictions table: {e}")
#         raise

# def generate_and_store_real_predictions():
#     """Fetches the latest data, makes predictions, and stores valid results in the database."""
#     # Pre-flight checks for necessary files
#     for file_path in [DATABASE_FILE, NPY_FILE, MODEL_PATH]:
#         if not os.path.exists(file_path):
#             logging.error(f"Required file not found: '{file_path}'. Please generate it first.")
#             return

#     conn = None
#     try:
#         conn = sqlite3.connect(DATABASE_FILE)
#         create_predictions_table(conn)
        
#         input_data_list = []
#         latest_date_str = None
#         valid_stock_indices = [] # Keep track of stocks with enough data
        
#         logging.info("Starting to fetch the latest data for all stocks from the database...")
#         for i, stock_code in enumerate(HSI_COMPONENTS):
#             cursor = conn.cursor()
#             cursor.execute(
#                 "SELECT high_price, low_price, open_price, volume, close_price, trade_date FROM stock_data WHERE stock_code = ? ORDER BY trade_date DESC LIMIT ?",
#                 (stock_code, TIME_STEPS)
#             )
#             rows = cursor.fetchall()

#             if len(rows) != TIME_STEPS:
#                 logging.warning(f"Insufficient data for stock {stock_code}: {len(rows)}/{TIME_STEPS} records found. This stock will be skipped.")
#                 input_data_list.append(np.zeros((TIME_STEPS, 5))) # Add zero padding
#             else:
#                 rows.reverse()
#                 if latest_date_str is None:
#                     latest_date_str = rows[-1][5]
#                 stock_features = [row[:5] for row in rows]
#                 input_data_list.append(stock_features)
#                 valid_stock_indices.append(i) # Mark this index as valid

#         if not valid_stock_indices:
#             logging.error("No stocks had sufficient data for prediction. Aborting.")
#             return
            
#         logging.info(f"Data fetched for {len(valid_stock_indices)}/{len(HSI_COMPONENTS)} stocks with sufficient records.")

#         input_data_np = np.array(input_data_list, dtype=np.float32)
#         predicted_prices = predict(input_data_np)

#         prediction_date = datetime.strptime(latest_date_str, '%Y-%m-%d') + timedelta(days=1)
#         prediction_date_str = prediction_date.strftime('%Y-%m-%d')
#         logging.info(f"All predictions are for the date: {prediction_date_str}")
        
#         # --- MODIFICATION 3: Handle NaN during Database Insertion ---
#         all_predictions_to_insert = []
#         for i, stock_code in enumerate(HSI_COMPONENTS):
#             price = predicted_prices[i]
            
#             # Check if the prediction is a valid number
#             if np.isnan(price):
#                 logging.warning(f"Skipping DB insertion for {stock_code} due to invalid (NaN) prediction.")
#                 continue
            
#             all_predictions_to_insert.append((
#                 stock_code, MODEL_NAME, prediction_date_str,
#                 round(float(price), 2)
#             ))

#         if not all_predictions_to_insert:
#             logging.error("Failed to generate any valid prediction data to store.")
#             return

#         logging.info(f"Preparing to insert {len(all_predictions_to_insert)} valid prediction records...")
#         cursor = conn.cursor()
#         insert_query = "INSERT OR REPLACE INTO stock_predictions (stock_code, model_name, prediction_date, predicted_price) VALUES (?, ?, ?, ?);"
#         cursor.executemany(insert_query, all_predictions_to_insert)
#         conn.commit()
#         logging.info(f"Successfully inserted or replaced {cursor.rowcount} prediction records.")

#     except sqlite3.Error as e:
#         logging.error(f"Database operation failed: {e}")
#     except FileNotFoundError as e:
#         logging.error(f"File not found error: {e}")
#     except Exception as e:
#         logging.error(f"An unexpected error occurred: {e}", exc_info=True)
#     finally:
#         if conn:
#             conn.close()
#             logging.info("Database connection closed.")

# if __name__ == "__main__":
#     generate_and_store_real_predictions()
#     logging.info("Prediction and storage task completed!")

# 文件名: predict.py (修改版)

import sqlite3
import numpy as np
import torch
from datetime import datetime, timedelta
import logging
from model import StockMixer
import os

# --- 配置 (无变化) ---
DATABASE_FILE = "stock_data.db"
NPY_FILE = "stock_data_max_values.npy"
MODEL_PATH = "best_model.pth"
MODEL_NAME = "StockMixer"
TIME_STEPS = 16
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

# predict 函数保持和你之前版本的一致，它只负责价格预测
def predict(input_data: np.ndarray) -> np.ndarray:
    logging.info("Starting model prediction...")
    if input_data.shape != (len(HSI_COMPONENTS), TIME_STEPS, 5):
        raise ValueError(f"Incorrect shape for input data! Expected ({len(HSI_COMPONENTS)}, {TIME_STEPS}, 5), but got {input_data.shape}")
    max_values = np.load(NPY_FILE)
    normalized_data = np.zeros_like(input_data, dtype=np.float32)
    for i in range(input_data.shape[0]):
        max_values_for_stock = max_values[i]
        if np.isnan(max_values_for_stock).any():
            logging.warning(f"Max values for {HSI_COMPONENTS[i]} contain NaN. Skipping normalization.")
            continue
        safe_max_values = np.where(max_values_for_stock == 0, 1, max_values_for_stock)
        for k in range(input_data.shape[2]):
            normalized_data[i, :, k] = input_data[i, :, k] / safe_max_values[k]
    logging.info("Data normalization complete.")
    model = StockMixer(stocks=len(HSI_COMPONENTS), time_steps=TIME_STEPS, channels=5, market=20, scale=3)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
    logging.info("Model loaded.")
    input_tensor = torch.tensor(normalized_data, dtype=np.float32)
    with torch.no_grad():
        output = model(input_tensor).reshape(-1).numpy()
    denormalized_output = np.zeros_like(output)
    for i in range(len(output)):
        max_values_for_stock = max_values[i]
        if np.isnan(max_values_for_stock).any():
            denormalized_output[i] = np.nan
            continue
        denormalized_output[i] = output[i] * max_values_for_stock[-1]
    logging.info("Model prediction and denormalization complete.")
    return denormalized_output

# --- 修改后的数据库操作函数 ---
def create_predictions_table(conn):
    """创建或更新预测表，增加涨跌幅字段"""
    try:
        with conn:
            cursor = conn.cursor()
            # --- 修改1: 增加 predicted_change_pct 字段 ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                model_name TEXT NOT NULL,
                prediction_date TEXT NOT NULL,
                predicted_price REAL NOT NULL,
                predicted_change_pct REAL, 
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, model_name, prediction_date)
            );
            """)
            # 兼容旧表，如果字段不存在则添加
            cursor.execute("PRAGMA table_info(stock_predictions);")
            columns = [info[1] for info in cursor.fetchall()]
            if 'predicted_change_pct' not in columns:
                cursor.execute("ALTER TABLE stock_predictions ADD COLUMN predicted_change_pct REAL;")
                logging.info("Added 'predicted_change_pct' column to existing table.")
            logging.info("Table 'stock_predictions' checked/created successfully.")
    except sqlite3.Error as e:
        logging.error(f"Failed to create/update predictions table: {e}")
        raise

def generate_and_store_real_predictions():
    """获取数据，预测，计算涨跌幅，并存入数据库"""
    for file_path in [DATABASE_FILE, NPY_FILE, MODEL_PATH]:
        if not os.path.exists(file_path):
            logging.error(f"CRITICAL: Required file not found: '{file_path}'. Please ensure it exists and the script has permission to read it. Aborting.")
            return

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        create_predictions_table(conn)
        
        input_data_list = []
        latest_date_str = None
        # --- 修改2: 使用字典来存储每只股票的昨日收盘价 ---
        last_close_prices = {} 

        logging.info("Fetching latest data and last close prices for all stocks...")
        for stock_code in HSI_COMPONENTS:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT high_price, low_price, open_price, volume, close_price, trade_date FROM stock_data WHERE stock_code = ? ORDER BY trade_date DESC LIMIT ?",
                (stock_code, TIME_STEPS)
            )
            rows = cursor.fetchall()

            if len(rows) < TIME_STEPS:
                logging.warning(f"Insufficient data for {stock_code}: Found {len(rows)} records, but need {TIME_STEPS}. This stock will be skipped.")
                input_data_list.append(np.zeros((TIME_STEPS, 5))) # 填充0以保持数组形状
                last_close_prices[stock_code] = None # 标记为无效
            else:
                rows.reverse()
                if latest_date_str is None:
                    latest_date_str = rows[-1][5]
                stock_features = [row[:5] for row in rows]
                input_data_list.append(stock_features)
                last_close_prices[stock_code] = rows[-1][4] # 记录昨日收盘价

        if latest_date_str is None:
            logging.error(f"CRITICAL: No stocks had sufficient data ({TIME_STEPS} records). Cannot make any predictions. Please run the data fetching script to get more historical data. Aborting.")
            return

        input_data_np = np.array(input_data_list, dtype=np.float32)
        predicted_prices = predict(input_data_np)

        prediction_date = datetime.strptime(latest_date_str, '%Y-%m-%d') + timedelta(days=1)
        prediction_date_str = prediction_date.strftime('%Y-%m-%d')
        logging.info(f"Predictions are for date: {prediction_date_str}")
        
        all_predictions_to_insert = []
        for i, stock_code in enumerate(HSI_COMPONENTS):
            predicted_price = predicted_prices[i]
            last_close = last_close_prices[stock_code]
            
            # --- 修改3: 计算涨跌幅并准备插入 ---
            if np.isnan(predicted_price) or last_close is None or last_close == 0:
                logging.warning(f"Skipping DB insertion for {stock_code} due to invalid prediction price or missing last close price.")
                continue
            
            change_pct = ((predicted_price - last_close) / last_close) * 100
            
            all_predictions_to_insert.append((
                stock_code, MODEL_NAME, prediction_date_str,
                round(float(predicted_price), 2),
                round(float(change_pct), 2) # 将涨跌幅也存入
            ))

        if not all_predictions_to_insert:
            logging.error("CRITICAL: Failed to generate any valid prediction data to store. This might be due to issues with 'stock_data_max_values.npy' or all stocks having insufficient data. Aborting.")
            return

        logging.info(f"Preparing to insert {len(all_predictions_to_insert)} valid prediction records...")
        cursor = conn.cursor()
        # --- 修改4: 更新INSERT语句以包含新字段 ---
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