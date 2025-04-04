import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# === CONFIGURATION ===
ticker = "INFY.NS"  # INFY listed on NSE India
period = "2y"       # Last 2 years of data
csv_filename = "infy_stock_data.csv"

# === DOWNLOAD DATA ===
data = yf.download(ticker, period=period)

# === FORMAT COLUMNS ===
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
data.reset_index(inplace=True)  # Make Date a column instead of index
data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')  # Format date as string

# === SAVE TO CSV ===
data.to_csv(csv_filename, index=False)
print(f"✅ CSV saved as '{csv_filename}' with {len(data)} rows.")
