# 文件名: generate_npy.py (修改版)

import sqlite3
import pandas as pd
import numpy as np
import logging
import os

DATABASE_FILE = "stock_data.db"
NPY_FILE = "stock_data_max_values.npy"

# 这个列表必须和你的预测脚本、模型训练时完全一致！
# 它决定了 .npy 文件中数据的顺序。
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
    """从数据库读取数据，计算最大值并保存为 .npy 文件。如果数据缺失，则使用 NaN 作为占位符。"""
    if not os.path.exists(DATABASE_FILE):
        logging.error(f"数据库文件 '{DATABASE_FILE}' 不存在。请先运行 `fetch_data.py`。")
        return

    logging.info(f"开始从 '{DATABASE_FILE}' 读取数据以生成 '{NPY_FILE}'...")
    
    feature_order = ['high_price', 'low_price', 'open_price', 'volume', 'close_price']
    all_max_values = []
    
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        
        for stock_code in HSI_COMPONENTS_FOR_MODEL:
            query = f"SELECT {', '.join(feature_order)} FROM stock_data WHERE stock_code = ?"
            df = pd.read_sql_query(query, conn, params=(stock_code,))

            # --- 主要修改点在这里 ---
            if df.empty:
                # 如果数据为空，记录警告并添加一行 NaN 作为占位符
                logging.warning(f"数据库中缺少股票 {stock_code} 的数据。将在 .npy 文件中使用 NaN 占位。")
                nan_row = [np.nan] * len(feature_order)
                all_max_values.append(nan_row)
            else:
                # 如果数据存在，正常计算最大值
                max_values_for_stock = df.max().values
                all_max_values.append(max_values_for_stock)
        
        final_max_values_array = np.array(all_max_values, dtype=np.float32)
        
        # 这个形状检查现在总是会通过，因为我们总是会添加一行
        expected_shape = (len(HSI_COMPONENTS_FOR_MODEL), len(feature_order))
        if final_max_values_array.shape != expected_shape:
            # 这个错误理论上不应该发生，但作为安全检查保留
            logging.error(f"计算出的最大值数组形状不正确！期望 {expected_shape}, 得到 {final_max_values_array.shape}")
            return

        np.save(NPY_FILE, final_max_values_array)
        logging.info(f"成功创建 '{NPY_FILE}' 文件，形状为: {final_max_values_array.shape}")

    except sqlite3.Error as e:
        logging.error(f"数据库操作失败: {e}")
    except Exception as e:
        logging.error(f"发生未知错误: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("数据库连接已关闭。")

if __name__ == "__main__":
    generate_max_values_file()