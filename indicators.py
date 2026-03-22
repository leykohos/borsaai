import pandas as pd
import numpy as np


def calculate_macd(close: pd.Series, fast=12, slow=26, signal=9):
    """MACD, Signal ve Histogram hesaplar."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_rsi(close: pd.Series, period=14):
    """RSI hesaplar (0-100 arası)."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_stoch_rsi(close: pd.Series, rsi_period=14, stoch_period=14, smooth_k=3, smooth_d=3):
    """Stochastic RSI hesaplar (%K ve %D döner)."""
    rsi = calculate_rsi(close, rsi_period)
    rsi_min = rsi.rolling(window=stoch_period).min()
    rsi_max = rsi.rolling(window=stoch_period).max()
    stoch_rsi_raw = (rsi - rsi_min) / (rsi_max - rsi_min + 1e-10)
    k = stoch_rsi_raw.rolling(window=smooth_k).mean() * 100
    d = k.rolling(window=smooth_d).mean()
    return k, d


def calculate_bollinger(close: pd.Series, period=20, std_dev=2):
    """Bollinger Bantları hesaplar (üst, orta, alt)."""
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def find_buy_signals(df: pd.DataFrame):
    """
    Al sinyallerini tespit eder.
    Kriter: RSI < 35 VE (MACD histogram 0'ın üstüne çıktı) VE fiyat Bollinger alt bandına yakın/altında
    """
    signals = []
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        rsi_oversold = row['rsi'] < 35
        macd_crossover = (prev['macd_hist'] < 0) and (row['macd_hist'] > 0)
        near_lower_band = row['close'] <= row['bb_lower'] * 1.02  # %2 tolerans

        if rsi_oversold or (macd_crossover and near_lower_band):
            reason = []
            if rsi_oversold:
                reason.append("RSI Aşırı Satım")
            if macd_crossover:
                reason.append("MACD Kesişim")
            if near_lower_band:
                reason.append("Bollinger Alt Band")

            signals.append({
                'date': df.index[i].strftime('%Y-%m-%d'),
                'price': round(float(row['close']), 2),
                'rsi': round(float(row['rsi']), 1),
                'macd_hist': round(float(row['macd_hist']), 4),
                'reason': ' + '.join(reason),
            })

    return signals


def compute_signal_returns(df: pd.DataFrame, signals: list):
    """Her al sinyali sonrasında 1W, 2W, 1M, 3M getirilerini hesaplar."""
    results = []
    close = df['close']
    dates = df.index

    for sig in signals:
        sig_date = pd.Timestamp(sig['date'])
        idx_list = dates.get_indexer([sig_date], method='nearest')
        idx = idx_list[0]
        entry_price = sig['price']

        def pct(days_ahead):
            target_idx = idx + days_ahead
            if target_idx < len(close):
                return round((close.iloc[target_idx] / entry_price - 1) * 100, 2)
            return None

        results.append({
            **sig,
            'ret_1w': pct(5),
            'ret_2w': pct(10),
            'ret_1m': pct(21),
            'ret_3m': pct(63),
        })

    return results
