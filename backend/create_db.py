import sqlite3
import random
from datetime import date, timedelta
import os

DATABASE = 'stock_data.db'

def create_database():
    """Creates the database and all necessary table structures."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create the stock_prices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            UNIQUE(ticker, date)
        )
    ''')
    
    # Create the stock_predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            model_name TEXT NOT NULL,
            date TEXT NOT NULL,
            predicted_price REAL NOT NULL
        )
    ''')
    
    # Create the stock_news table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database table structure created/verified.")

def populate_database():
    """Populates the database with mock data."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if the database already contains data. If so, skip the process.
    cursor.execute('SELECT COUNT(*) FROM stock_prices')
    if cursor.fetchone()[0] > 0:
        print("Database already contains data, skipping population process. To regenerate, please delete the stock_data.db file first.")
        conn.close()
        return

    print("Populating the database with new mock data...")

    # --- List of tickers, including TSLA ---
    tickers = ['AAPL', 'GOOGL', 'TSLA']
    today = date.today()

    for ticker in tickers:
        print(f"  -> Generating data for {ticker}...")

        # 1. Populate historical price data
        if ticker == 'AAPL': base_price = random.uniform(150, 180)
        elif ticker == 'GOOGL': base_price = random.uniform(130, 150)
        else: base_price = random.uniform(200, 300) # TSLA

        for i in range(100):
            current_date = today - timedelta(days=i)
            price_change = random.uniform(-5, 5)
            open_price = round(base_price + price_change, 2)
            close_price = round(open_price + random.uniform(-3, 3), 2)
            high_price = round(max(open_price, close_price) + random.uniform(0, 2), 2)
            low_price = round(min(open_price, close_price) - random.uniform(0, 2), 2)
            volume = random.randint(10_000_000, 90_000_000)
            cursor.execute(
                'INSERT INTO stock_prices (ticker, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (ticker, current_date.strftime('%Y-%m-%d'), open_price, high_price, low_price, close_price, volume)
            )
            base_price = close_price
        
        # 2. Populate model prediction data
        models = ['AlphaModel', 'BetaTrend']
        for model in models:
            for i in range(3):
                pred_date = today + timedelta(days=i*15 + 7) # Predict future dates
                predicted_price = round(base_price * (1 + random.uniform(-0.1, 0.1)), 2)
                cursor.execute(
                    'INSERT INTO stock_predictions (ticker, model_name, date, predicted_price) VALUES (?, ?, ?, ?)',
                    (ticker, model, pred_date.strftime('%Y-%m-%d'), predicted_price)
                )

        # 3. Populate related news data
        news_items = [
            (f"{ticker} stock price hits new high", "The company released a better-than-expected financial report, driving the stock price up."), 
            (f"Analyst adjusts {ticker} rating", "A top analyst upgraded the rating from 'Hold' to 'Buy'."),
        ]
        for i, (title, summary) in enumerate(news_items):
            news_date = today - timedelta(days=i*10 + 5)
            cursor.execute(
                'INSERT INTO stock_news (ticker, date, title, summary) VALUES (?, ?, ?, ?)',
                (ticker, news_date.strftime('%Y-%m-%d'), title, summary)
            )

    conn.commit()
    conn.close()
    print("Database population complete!")

if __name__ == '__main__':
    # If the database file already exists, delete it to ensure we generate fresh data
    if os.path.exists(DATABASE):
        print(f"Old database file '{DATABASE}' detected, deleting to regenerate...")
        os.remove(DATABASE)
    
    create_database()
    populate_database()