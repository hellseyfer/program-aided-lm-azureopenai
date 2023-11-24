# filename: stock_plot.py

import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

# Get date of first trading day of this year
this_year = datetime.now().year
start_date = datetime(this_year, 1, 1)

# Download stock data
nvda = yf.download('NVDA', start=start_date)
tsla = yf.download('TSLA', start=start_date)

# Plot the closing prices
plt.figure(figsize=(14, 7))
plt.plot(nvda.Close, label='NVDA')
plt.plot(tsla.Close, label='TESLA')
plt.xlabel('Date')
plt.ylabel('Stock Price ($)')
plt.legend()
plt.title('NVDA and TESLA Stock Price YTD')
plt.grid(True)

# Save plot as a .png image
plt.savefig('stock_prices.png')

print("done")