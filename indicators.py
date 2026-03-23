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


def calculate_sma(close: pd.Series, period=20):
    return close.rolling(window=period).mean()


def calculate_ema(close: pd.Series, period=20):
    return close.ewm(span=period, adjust=False).mean()


def calculate_atr(df: pd.DataFrame, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(window=period).mean()


def calculate_supertrend(df: pd.DataFrame, period=10, multiplier=3):
    atr = calculate_atr(df, period)
    hl2 = (df['high'] + df['low']) / 2
    final_upperband = hl2 + (multiplier * atr)
    final_lowerband = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    for i in range(period, len(df)):
        if df['close'].iloc[i] > final_upperband.iloc[i-1]:
            direction.iloc[i] = 1
        elif df['close'].iloc[i] < final_lowerband.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1]
            if direction.iloc[i] == 1 and final_lowerband.iloc[i] < final_lowerband.iloc[i-1]:
                final_lowerband.iloc[i] = final_lowerband.iloc[i-1]
            if direction.iloc[i] == -1 and final_upperband.iloc[i] > final_upperband.iloc[i-1]:
                final_upperband.iloc[i] = final_upperband.iloc[i-1]

        supertrend.iloc[i] = final_lowerband.iloc[i] if direction.iloc[i] == 1 else final_upperband.iloc[i]

    return supertrend, direction


def calculate_adx(df: pd.DataFrame, period=14):
    up_move = df['high'] - df['high'].shift(1)
    down_move = df['low'].shift(1) - df['low']
    
    pos_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    neg_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    pos_dm = pd.Series(pos_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean()
    neg_dm = pd.Series(neg_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean()
    
    atr = calculate_atr(df, period)
    
    pdi = 100 * (pos_dm / atr)
    mdi = 100 * (neg_dm / atr)
    
    dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    adx = dx.ewm(alpha=1/period, adjust=False).mean()
    return adx, pdi, mdi


def find_signals(df: pd.DataFrame):
    """
    Tüm göstergelerden gelen Al/Sat sinyallerini tespit eder.
    Her sinyal için kaynağı (RSI, MACD, vs.) ve yönü döner.
    Artık indikatör verilerini de içerir.
    """
    signals = []
    
    for i in range(2, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]
        
        t = df.index[i]
        date_str = t.strftime('%Y-%m-%d %H:%M') if (t.hour != 0 or t.minute != 0) else t.strftime('%Y-%m-%d')
        
        price = round(float(row['close']), 2)
        rsi_val = round(float(row['rsi']), 1) if 'rsi' in row else 0
        stoch_k = round(float(row['stoch_k']), 1) if 'stoch_k' in row else 0
        macd_h = round(float(row['macd_hist']), 4) if 'macd_hist' in row else 0
        st_dir = int(row['st_dir']) if 'st_dir' in row else 0

        # Genel Trend (Filtreleme amaçlı)
        trend_up = row.get('st_dir', 1) == 1 and row.get('ema20', 0) > row.get('sma20', 0)

        common_data = {
            'date': date_str, 
            'price': price, 
            'rsi': rsi_val,
            'stoch_k': stoch_k,
            'macd_h': macd_h,
            'trend': 'BOĞA' if trend_up else 'AYI'
        }

        # RSI Sinyalleri
        if prev['rsi'] < 35 and row['rsi'] >= 35:
            signals.append({**common_data, 'type': 'Buy', 'indicator': 'RSI', 'reason': 'RSI 35 Yukarı Kesti'})
        elif prev['rsi'] > 65 and row['rsi'] <= 65:
            signals.append({**common_data, 'type': 'Sell', 'indicator': 'RSI', 'reason': 'RSI 65 Aşağı Kesti'})
            
        # Stoch RSI Sinyalleri
        if prev['stoch_k'] < prev['stoch_d'] and row['stoch_k'] > row['stoch_d'] and row['stoch_k'] < 80:
            signals.append({**common_data, 'type': 'Buy', 'indicator': 'StochRSI', 'reason': 'Stoch K, D yi Yukarı Kesti'})
        elif prev['stoch_k'] > prev['stoch_d'] and row['stoch_k'] < prev['stoch_d'] and row['stoch_k'] > 20:
            signals.append({**common_data, 'type': 'Sell', 'indicator': 'StochRSI', 'reason': 'Stoch K, D yi Aşağı Kesti'})
            
        # Hareketli Ortalamalar Sinyalleri (EMA, SMA)
        if prev['ema20'] < prev['sma20'] and row['ema20'] > row['sma20']:
            signals.append({**common_data, 'type': 'Buy', 'indicator': 'HA_Kesişim', 'reason': 'EMA20, SMA20 yi Yukarı Kesti'})
        elif prev['ema20'] > prev['sma20'] and row['ema20'] < row['sma20']:
            signals.append({**common_data, 'type': 'Sell', 'indicator': 'HA_Kesişim', 'reason': 'EMA20, SMA20 yi Aşağı Kesti'})
            
        # MACD Sinyalleri
        if prev['macd_hist'] < 0 and row['macd_hist'] > 0:
            signals.append({**common_data, 'type': 'Buy', 'indicator': 'MACD', 'reason': 'MACD Yukarı Kesti'})
        elif prev['macd_hist'] > 0 and row['macd_hist'] < 0:
            signals.append({**common_data, 'type': 'Sell', 'indicator': 'MACD', 'reason': 'MACD Aşağı Kesti'})
            
        # Supertrend Sinyalleri
        if 'st_dir' in df.columns:
            if prev['st_dir'] == -1 and row['st_dir'] == 1:
                signals.append({**common_data, 'type': 'Buy', 'indicator': 'Supertrend', 'reason': 'Supertrend Al'})
            elif prev['st_dir'] == 1 and row['st_dir'] == -1:
                signals.append({**common_data, 'type': 'Sell', 'indicator': 'Supertrend', 'reason': 'Supertrend Sat'})

    return signals


def simulate_spot_trades(signals: list):
    """
    Sinyal listesini zaman sırasına göre okuyup, her indikatör için ayrı ayrı
    ilk 'Buy' sinyalinde spot işlem girip ilk 'Sell' sinyalinde çıkarak kâr/zarar durumunu hesaplar.
    """
    signals_sorted = sorted(signals, key=lambda x: x['date'])
    trades = []
    
    positions = {}
    
    for sig in signals_sorted:
        ind = sig['indicator']
        if ind not in positions:
            positions[ind] = {'in_position': False, 'entry_signal': None}
            
        pos = positions[ind]
        
        if not pos['in_position'] and sig['type'] == 'Buy':
            pos['in_position'] = True
            pos['entry_signal'] = sig
        elif pos['in_position'] and sig['type'] == 'Sell':
            exit_price = sig['price']
            entry_signal = pos['entry_signal']
            entry_price = entry_signal['price']
            ret_pct = round((exit_price / entry_price - 1) * 100, 2)
            
            trades.append({
                'entry_date': entry_signal['date'],
                'entry_price': entry_price,
                'entry_reason': entry_signal['reason'],
                'entry_indicator': entry_signal['indicator'],
                'exit_date': sig['date'],
                'exit_price': exit_price,
                'exit_reason': sig['reason'],
                'exit_indicator': sig['indicator'],
                'profit_pct': ret_pct
            })
            pos['in_position'] = False
            
    trades = sorted(trades, key=lambda x: x['entry_date'])
    return trades
