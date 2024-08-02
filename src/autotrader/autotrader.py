import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Download historical data for a stock (e.g., AAPL)
stock_data = yf.download('NVDA', start='2024-01-30', end='2024-07-31')

# Calculate the MACD and Signal Line
stock_data['EMA12'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
stock_data['EMA26'] = stock_data['Close'].ewm(span=26, adjust=False).mean()
stock_data['MACD'] = stock_data['EMA12'] - stock_data['EMA26']
stock_data['Signal_Line'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()

# Buy and Sell signals
stock_data['Buy_Signal'] = (stock_data['MACD'] > stock_data['Signal_Line']) & (stock_data['MACD'].shift(1) <= stock_data['Signal_Line'].shift(1))
stock_data['Sell_Signal'] = (stock_data['MACD'] < stock_data['Signal_Line']) & (stock_data['MACD'].shift(1) >= stock_data['Signal_Line'].shift(1))

# Plotting the data
plt.figure(figsize=(14,7))
plt.plot(stock_data['Close'], label='Close Price')
plt.plot(stock_data['MACD'], label='MACD', color='r')
plt.plot(stock_data['Signal_Line'], label='Signal Line', color='g')
plt.scatter(stock_data.index, stock_data['Buy_Signal'] * stock_data['Close'], label='Buy Signal', marker='^', color='green')
plt.scatter(stock_data.index, stock_data['Sell_Signal'] * stock_data['Close'], label='Sell Signal', marker='v', color='red')
plt.legend()
plt.show()

# Print Buy/Sell dates
print("Buy Signals:\n", stock_data[stock_data['Buy_Signal']].index)
print("Sell Signals:\n", stock_data[stock_data['Sell_Signal']].index)
