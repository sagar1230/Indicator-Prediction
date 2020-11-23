import math
import numpy as np
from pandas_datareader import get_data_yahoo
import datetime as dt

from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def get_stock_df(symbol, current_epoch_seconds):
    attempt = 1
    while True:
        try:
            df = get_data_yahoo(symbol,
                                start=dt.datetime(2017, 1, 1),
                                end=dt.datetime.fromtimestamp(current_epoch_seconds))
        except ReadTimeout or ConnectionError:
            attempt += 1
            if attempt > 3:
                input('Connection Interrupted. Press enter to proceed')

            else:
                print('Trying connection... Attempt ' + str(attempt))

        else:
            if attempt > 1:
                print('Reconnected!')

            return df


def sig_buy_sell(df):
    sig_price_buy = []
    sig_price_sell = []
    signal = 0
    for i in range(len(df)):
        if df['Short Indicator'][i] > df['Long Indicator'][i]:
            if signal != 1:
                sig_price_buy.append(df['Full'][i])
                sig_price_sell.append(np.nan)
                signal = 1
            else:
                sig_price_buy.append(np.nan)
                sig_price_sell.append(np.nan)
        elif df['Short Indicator'][i] < df['Long Indicator'][i]:
            if signal != -1:
                sig_price_buy.append(np.nan)
                sig_price_sell.append(df['Full'][i])
                signal = -1
            else:
                sig_price_buy.append(np.nan)
                sig_price_sell.append(np.nan)
        else:
            sig_price_buy.append(np.nan)
            sig_price_sell.append(np.nan)
    return sig_price_buy, sig_price_sell, signal


def predict(symbol, epoch_seconds, indicator_type):
    if indicator_type == 'SMA':
        prediction_percent = 0.03
    elif indicator_type == 'MACD':
        prediction_percent = 0.015
    else:
        raise Exception("Invalid Indicator Type")

    df = get_stock_df(symbol, epoch_seconds)
    current_adj_close = df['Adj Close'][-1]
    df_feature = df.loc[:, ['Adj Close', 'Volume']]
    df_feature['volatility'] = (df['High'] - df['Low']) / ((df['High'] + df['Low']) / 2)
    df_feature['pct_change'] = (df['Close'] - df['Open']) / df['Open'] * 100
    prediction_out = int(math.ceil(prediction_percent * len(df_feature)))
    prediction_col = 'Adj Close'
    df_feature['Label'] = df_feature[prediction_col].shift(-prediction_out)
    df_feature.dropna(inplace=True)
    X = np.array(df_feature.drop(['Label'], 1))
    y = np.array(df_feature['Label'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

    lr = LinearRegression()
    lr.fit(X_train, y_train)
    r2 = lr.score(X_test, y_test)

    X_future = X[-prediction_out:]
    y_prediction = lr.predict(X_future)

    df['Prediction'] = np.nan
    current_epoch_seconds = df.iloc[-1].name.timestamp() + 86400 + 18000  # timezone adjustment
    df['Full'] = df[prediction_col]

    for i in y_prediction:
        current_date = dt.datetime.fromtimestamp(current_epoch_seconds)
        df.loc[current_date, 'Prediction'] = i
        df.loc[current_date, 'Full'] = i
        current_epoch_seconds += 86400

    df.dropna(how='all', inplace=True)

    if indicator_type == 'SMA':
        df['Short Indicator'] = df['Full'].rolling(window=30).mean()
        df['Long Indicator'] = df['Full'].rolling(window=100).mean()
    elif indicator_type == 'MACD':
        df['Short Indicator'] = df['Full'].ewm(span=12).mean()
        df['Long Indicator'] = df['Full'].ewm(span=26).mean()
    else:
        raise Exception("Invalid Indicator Type")

    df['Buy Signal'], df['Sell Signal'], signal = sig_buy_sell(df)

    return df, r2, current_adj_close, signal
