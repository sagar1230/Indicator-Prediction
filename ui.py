import matplotlib.pyplot as plt
import datetime as dt

from main import predict


symbol = input("Enter Ticker: ")
date = input("Enter Date | MM-DD-YYYY: ")
date_vec = list(map(int, date.split('-')))
indicator_type = input("Enter Indicator Type | SMA or MACD: ")

if indicator_type == 'SMA':
    short_label = '30-day SMA'
    long_label = '100-day SMA'
elif indicator_type == 'MACD':
    short_label = '12-day EMA'
    long_label = '26-day EMA'
else:
    raise Exception("Invalid Indicator Type")

epoch_seconds = dt.datetime(date_vec[2], date_vec[0], date_vec[1]).timestamp()

df, r2, _, _ = predict(symbol, epoch_seconds, indicator_type)

plt.figure(figsize=(10, 7.5))

df['Adj Close'].plot(color='c', alpha=0.5)
df['Prediction'].plot(color='orange', alpha=0.75)
plt.plot(df[['Short Indicator']], 'b', label=short_label, alpha=0.5)
plt.plot(df[['Long Indicator']], 'r', label=long_label, alpha=0.5)
plt.scatter(df.index, df['Buy Signal'], label="Buy Signal", marker="^", color='g')
plt.scatter(df.index, df['Sell Signal'], label="Sell Signal", marker="v", color='r')

plt.title('R\N{SUPERSCRIPT TWO} = ' + str(r2))
plt.suptitle(symbol)
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.grid()
plt.show()
