import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime as dt

from main import predict


def backtest(symbol, start_vec, indicator_type, num_days):
    current_epoch_seconds = dt.datetime(start_vec[2], start_vec[0], start_vec[1]).timestamp()
    date_range = pd.date_range(dt.datetime.fromtimestamp(current_epoch_seconds), periods=num_days, freq='D')
    adj_close = []
    buy_signals = []
    sell_signals = []
    old_signal = 0
    for x in range(1, num_days + 1):
        _, _, curr, new_signal = predict(symbol, current_epoch_seconds, indicator_type)
        adj_close.append(curr)
        print(symbol + ' ' + str(x))
        if new_signal != old_signal:
            old_signal = new_signal
            if new_signal == 1:
                buy_signals.append(curr)
                sell_signals.append(np.nan)
            elif new_signal == -1:
                buy_signals.append(np.nan)
                sell_signals.append(curr)
        else:
            buy_signals.append(np.nan)
            sell_signals.append(np.nan)

        current_epoch_seconds += 86400

    buy_signals[0] = np.nan
    sell_signals[0] = np.nan
    df = pd.DataFrame({'Date': date_range, 'Adj Close': adj_close, 'Buy Signal': buy_signals, 'Sell Signal': sell_signals})
    return df


def plot_backtest(df, symbol, indicator_type):
    if indicator_type == 'SMA':
        sup_title = "30-day / 100-day SMA Backtest"
    elif indicator_type == 'MACD':
        sup_title = "12-day / 26-day MACD Backtest"
    else:
        raise Exception("Invalid Indicator Type")

    plt.figure(figsize=(10, 7.5))

    plt.plot(df['Date'], df['Adj Close'], label='Adj Close', color='c', alpha=0.5)
    plt.scatter(df['Date'], df['Buy Signal'], label="Buy Signal", marker="^", color='g')
    plt.scatter(df['Date'], df['Sell Signal'], label="Sell Signal", marker="v", color='r')

    plt.title(symbol)
    plt.suptitle(sup_title)
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid()
    plt.show()


def plot_4_backtests(s1, df1, s2, df2, s3, df3, s4, df4, indicator_type):
    if indicator_type == 'SMA':
        sup_title = "30-day / 100-day SMA Backtesting"
    elif indicator_type == 'MACD':
        sup_title = "12-day / 26-day MACD Backtesting"
    else:
        raise Exception("Invalid Indicator Type")

    fig, axs = plt.subplots(2, 2, figsize=(10, 7.5))

    axs[0, 0].plot(df1['Date'], df1['Adj Close'], label='Adj Close', color='c', alpha=0.5)
    axs[0, 0].scatter(df1['Date'], df1['Buy Signal'], label="Buy Signal", marker="^", color='g')
    axs[0, 0].scatter(df1['Date'], df1['Sell Signal'], label="Sell Signal", marker="v", color='r')
    axs[0, 0].set_title(s1)

    axs[0, 1].plot(df2['Date'], df2['Adj Close'], label='Adj Close', color='tab:purple', alpha=0.5)
    axs[0, 1].scatter(df2['Date'], df2['Buy Signal'], label="Buy Signal", marker="^", color='g')
    axs[0, 1].scatter(df2['Date'], df2['Sell Signal'], label="Sell Signal", marker="v", color='r')
    axs[0, 1].set_title(s2)

    axs[1, 0].plot(df3['Date'], df3['Adj Close'], label='Adj Close', color='tab:orange', alpha=0.5)
    axs[1, 0].scatter(df3['Date'], df3['Buy Signal'], label="Buy Signal", marker="^", color='g')
    axs[1, 0].scatter(df3['Date'], df3['Sell Signal'], label="Sell Signal", marker="v", color='r')
    axs[1, 0].set_title(s3)

    axs[1, 1].plot(df4['Date'], df4['Adj Close'], label='Adj Close', color='tab:blue', alpha=0.5)
    axs[1, 1].scatter(df4['Date'], df4['Buy Signal'], label="Buy Signal", marker="^", color='g')
    axs[1, 1].scatter(df4['Date'], df4['Sell Signal'], label="Sell Signal", marker="v", color='r')
    axs[1, 1].set_title(s4)

    for ax in axs.flat:
        ax.grid(True)
        ax.xaxis.set_major_formatter(DateFormatter('%m-%Y'))
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax.yaxis.set_major_locator(plt.MaxNLocator(6))
        ax.legend(loc='lower right')

    plt.suptitle(sup_title)
    plt.show()


start = 1, 1, 2019
indicator = 'SMA'
s1 = 'S&P500'
df1 = backtest('^GSPC', start, indicator, 365)
s2 = 'DJI'
df2 = backtest('^DJI', start, indicator, 365)
s3 = 'MSFT'
df3 = backtest(s3, start, indicator, 365)
s4 = 'FB'
df4 = backtest(s4, start, indicator, 365)

plot_4_backtests(s1, df1, s2, df2, s3, df3, s4, df4, indicator)
