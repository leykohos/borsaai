import os
import json
import urllib.request
import urllib.error
import yfinance as yf
import pandas as pd
import concurrent.futures
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from indicators import (
    calculate_macd,
    calculate_rsi,
    calculate_stoch_rsi,
    calculate_bollinger,
    calculate_sma,
    calculate_ema,
    calculate_atr,
    calculate_supertrend,
    calculate_adx,
    find_signals,
    simulate_spot_trades,
)

load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

BIST30_SYMBOLS = [
    "AKBNK.IS", "ALARK.IS", "ALBRK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS",
    "BRISA.IS", "CCOLA.IS", "CWENE.IS", "DOAS.IS", "EKGYO.IS",
    "ENKAI.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS", "GUBRF.IS",
    "HEKTS.IS", "ISCTR.IS", "KCHOL.IS", "KONTR.IS", "KOZAA.IS",
    "KOZAL.IS", "KRDMD.IS", "MGROS.IS", "ODAS.IS", "PETKM.IS",
    "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "SMRTG.IS",
    "TCELL.IS", "THYAO.IS", "TOASO.IS", "TUPRS.IS", "YKBNK.IS"
]

# desteklenen periyotlar
INTERVALS = {
    "1h":  {"period": "730d", "yf_interval": "1h"},
    "1d":  {"period": "3y",   "yf_interval": "1d"},
    "1wk": {"period": "5y",   "yf_interval": "1wk"},
    "1mo": {"period": "10y",  "yf_interval": "1mo"},
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def gemini_generate(prompt: str) -> str:
    """Gemini API'ye direkt HTTP isteği gönderir."""
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err_body = json.loads(e.read().decode())
        code = err_body.get("error", {}).get("code", e.code)
        msg  = err_body.get("error", {}).get("message", str(e))
        if code == 429:
            raise RuntimeError("Gemini API kota limiti aşıldı (429). Lütfen 1-2 dakika bekleyip tekrar deneyin.")
        if code == 400:
            raise RuntimeError(f"Geçersiz API key (400). .env dosyasındaki GEMINI_API_KEY değerini kontrol edin. Detay: {msg}")
        raise RuntimeError(f"Gemini API hatası ({code}): {msg}")


def fetch_data(symbol: str = "AKBNK.IS", interval: str = "1d"):
    """Seçilen hisseyi Yahoo Finance'den çeker ve indikatörleri ekler."""
    if symbol not in BIST30_SYMBOLS:
        symbol = BIST30_SYMBOLS[0]
    cfg = INTERVALS.get(interval, INTERVALS["1d"])
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=cfg["period"], interval=cfg["yf_interval"])
    df.index = pd.to_datetime(df.index.tz_localize(None) if df.index.tz else df.index)
    df.columns = [c.lower() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].dropna()

    # İndikatörleri hesapla
    df["macd"], df["macd_signal"], df["macd_hist"] = calculate_macd(df["close"])
    df["rsi"] = calculate_rsi(df["close"])
    df["stoch_k"], df["stoch_d"] = calculate_stoch_rsi(df["close"])
    df["bb_upper"], df["bb_middle"], df["bb_lower"] = calculate_bollinger(df["close"])
    df["sma20"] = calculate_sma(df["close"], 20)
    df["ema20"] = calculate_ema(df["close"], 20)
    df["atr"] = calculate_atr(df, 14)
    st_line, st_dir = calculate_supertrend(df, 10, 2)
    df["st_line"] = st_line
    df["st_dir"] = st_dir

    return df.dropna()


def fmt_dates(df, interval):
    """Saatlik veride tarih+saat, diğerlerinde sadece tarih döner."""
    if interval == "1h":
        return df.index.strftime("%Y-%m-%dT%H:%M:%S").tolist()
    return df.index.strftime("%Y-%m-%d").tolist()


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


from flask import request as flask_request


@app.route("/api/data")
def api_data():
    """Ham OHLCV + indikatör verilerini JSON olarak döner."""
    try:
        interval = flask_request.args.get("interval", "1d")
        symbol = flask_request.args.get("symbol", "AKBNK.IS")
        if interval not in INTERVALS:
            interval = "1d"
        df = fetch_data(symbol, interval)

        def to_list(series):
            return [round(float(x), 4) if pd.notna(x) else None for x in series]

        last = df.iloc[-1]
        states = {}
        states["RSI"] = "AL" if last["rsi"] < 40 else "SAT" if last["rsi"] > 60 else "NÖTR"
        states["MACD"] = "AL" if last["macd_hist"] > 0 else "SAT" if last["macd_hist"] < 0 else "NÖTR"
        states["Supertrend"] = "AL" if last["st_dir"] == 1 else "SAT"
        states["Hareketli Ort."] = "AL" if last["ema20"] > last["sma20"] else "SAT"
        states["StochRSI"] = "AL" if last["stoch_k"] > last["stoch_d"] else "SAT"

        try:
            live_price = float(yf.Ticker(symbol).fast_info.last_price)
        except:
            live_price = float(df.iloc[-1]['close'])

        return jsonify({
            "symbol": symbol,
            "interval": interval,
            "dates": fmt_dates(df, interval),
            "close": to_list(df["close"]),
            "open": to_list(df["open"]),
            "high": to_list(df["high"]),
            "low": to_list(df["low"]),
            "volume": to_list(df["volume"]),
            "macd": to_list(df["macd"]),
            "macd_signal": to_list(df["macd_signal"]),
            "macd_hist": to_list(df["macd_hist"]),
            "rsi": to_list(df["rsi"]),
            "stoch_k": to_list(df["stoch_k"]),
            "stoch_d": to_list(df["stoch_d"]),
            "bb_upper": to_list(df["bb_upper"]),
            "bb_middle": to_list(df["bb_middle"]),
            "bb_lower": to_list(df["bb_lower"]),
            "sma20": to_list(df["sma20"]),
            "st_line": to_list(df["st_line"]),
            "st_dir": to_list(df["st_dir"]),
            "current_states": states,
            "live_price": live_price
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/signals")
def api_signals():
    try:
        symbol = flask_request.args.get("symbol", "AKBNK.IS")
        df = fetch_data(symbol, "1h")
        signals = find_signals(df)
        trades = simulate_spot_trades(signals)
        
        # Sinyalleri trade verileriyle eşleştir
        # Her Buy sinyaline, eğer kapanmışsa kar/zarar verisini ekle
        for sig in signals:
            if sig['type'] == 'Buy':
                # Bu Buy sinyalini içeren bir trade var mı?
                matched_trade = next((t for t in trades if t['entry_date'] == sig['date'] and t['entry_indicator'] == sig['indicator']), None)
                if matched_trade:
                    sig['trade_result'] = {
                        'exit_date': matched_trade['exit_date'],
                        'profit_pct': matched_trade['profit_pct'],
                        'status': 'CLOSED'
                    }
                else:
                    sig['trade_result'] = {
                        'status': 'OPEN'
                    }

        # O anki açık (Buy verilmiş, Sell beklenilen) işlemleri bul
        positions = {}
        for sig in sorted(signals, key=lambda x: x['date']):
            ind = sig['indicator']
            if ind not in positions:
                positions[ind] = {'in_pos': False, 'entry_signal': None}
            if not positions[ind]['in_pos'] and sig['type'] == 'Buy':
                positions[ind]['in_pos'] = True
                positions[ind]['entry_signal'] = sig
            elif positions[ind]['in_pos'] and sig['type'] == 'Sell':
                positions[ind]['in_pos'] = False
                
        open_positions = []
        try:
            current_price = round(float(yf.Ticker(symbol).fast_info.last_price), 2)
        except:
            current_price = round(float(df.iloc[-1]['close']), 2)
        
        for ind, pos in positions.items():
            if pos['in_pos']:
                open_positions.append({
                    'indicator': ind,
                    'buy_date': pos['entry_signal']['date'],
                    'buy_price': pos['entry_signal']['price'],
                    'reason': pos['entry_signal']['reason'],
                    'current_price': current_price,
                    'profit_pct': round((current_price / pos['entry_signal']['price'] - 1) * 100, 2)
                })

        return jsonify({
            "signals": signals,
            "trades": trades,
            "open_positions": sorted(open_positions, key=lambda x: x['buy_date'], reverse=True),
            "symbols": BIST30_SYMBOLS
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze")
def api_analyze():
    """Gemini API ile mevcut duruma göre detaylı AI yorumu üretir."""
    try:
        symbol = flask_request.args.get("symbol", "AKBNK.IS")
        df = fetch_data(symbol, "1d")
        last = df.iloc[-1]
        
        signals = find_signals(df)
        last_signals = signals[-5:] if len(signals) >= 5 else signals
        trades = simulate_spot_trades(signals)
        last_trades = trades[-3:] if len(trades) >= 3 else trades

        # İndikatör başarı oranlarını hesapla (Geçmiş işlemlerden)
        ind_stats = {}
        for t in trades:
            ind = t['entry_indicator']
            if ind not in ind_stats:
                ind_stats[ind] = {'wins': 0, 'count': 0, 'profit': 0}
            ind_stats[ind]['count'] += 1
            if t['profit_pct'] > 0: ind_stats[ind]['wins'] += 1
            ind_stats[ind]['profit'] += t['profit_pct']

        summary = f"""
{symbol} Hissesi Güncel Teknik Verileri ({df.index[-1].strftime('%Y-%m-%d')}):
Son Fiyat: {last['close']:.2f} TL
RSI (14): {last['rsi']:.1f} 
MACD Histogram: {last['macd_hist']:.4f}
Supertrend Yönü: {'AL (+1)' if last['st_dir'] == 1 else 'SAT (-1)'}
ATR: {last['atr']:.2f} (Volatilite)
Bollinger: Alt:{last['bb_lower']:.2f} Orta:{last['bb_middle']:.2f} Üst:{last['bb_upper']:.2f}
StochRSI: K:{last['stoch_k']:.1f} D:{last['stoch_d']:.1f}
Hareketli Ort: SMA20:{last['sma20']:.2f} EMA20:{last['ema20']:.2f}
"""

        summary += "\nİndikatörlerin Bu Hissedeki Tarihsel Başarı Oranları (Backtest):\n"
        if ind_stats:
            for ind, s in ind_stats.items():
                rate = (s['wins']/s['count'])*100 if s['count'] > 0 else 0
                avg_p = s['profit']/s['count'] if s['count'] > 0 else 0
                summary += f"- {ind}: %{rate:.0f} Başarı Oranı, {s['count']} işlemde ortalama %{avg_p:.2f} kar/zarar.\n"
        else:
            summary += "- Yeterli geçmiş işlem verisi yok.\n"

        if len(last_signals) > 0:
            summary += "\nSon Gelen Temel Sinyaller:\n"
            for s in last_signals:
                summary += f"  - {s['date']}: {s['type']} ({s['indicator']}) @ {s['price']} TL\n"

        prompt = f"""Sen üst düzey profesyonel bir BIST30 Teknik Analistisin.
Sana {symbol} hissesinin tüm güncel teknik göstergelerini, son sinyallerini ve indikatörlerin bu hisse üzerindeki DÜNYA GERÇEĞİ tarihsel başarı oranlarını (backtest verisini) sunuyorum.
Bu verilere dayanarak yatırıma yön verecek, AŞAĞIDAKİ BAŞLIKLARI KESİN İÇEREN KISA, NET VE YAPISAL BİR RAPOR YAZ:

**📊 GENEL KARAR:**
Mevcut duruma göre net olarak "AL", "SAT" veya "NÖTR" kararı ver. Bunu çok kısa bir gerekçeyle (Örn: Çünkü RSI aşırı satımda ve Supertrend Al verdi) açıkla.

**🎯 ALIM SEVİYESİ:**
"Şu seviyelerde alım yapılabilir:" diyerek güncel fiyatı ve teknik verileri baz alarak net bir fiyat veya aralık ver.

**💸 SATIŞ / KÂR ALMA SEVİYESİ:**
"Şu seviyelerde satılabilir veya kâr alınabilir:" diyerek dirençlere veya ATR volatilite rakamlarına bakarak net bir fiyat/direnç ver.

**🧱 DESTEK VE DİRENÇLER:**
En yakın ve en sağlam destek ve direnç seviyelerini (Bollinger, Ortalamalar, ATR kullanarak) kuruşu kuruşuna yaz.

**📈 İNDİKATÖR ANALİZİ VE BAŞARI ETKİSİ:**
Gönderilen tarihsel başarı oranlarına ÇOK DİKKAT ET (Örneğin bu hissede en çok kazandıran indikatör hangisiyse ona özel önem ver) ve teknik görünümü bu istatistiklerle harmanlayarak kısaca özetle.

Veriler:
{summary}"""

        analysis = gemini_generate(prompt)
        return jsonify({"analysis": analysis, "date": df.index[-1].strftime("%Y-%m-%d")})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_opportunities(df, sym):
    df.index = pd.to_datetime(df.index.tz_localize(None) if df.index.tz else df.index)
    df.columns = [c.lower() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    df["macd"], df["macd_signal"], df["macd_hist"] = calculate_macd(df["close"])
    df["rsi"] = calculate_rsi(df["close"])
    df["stoch_k"], df["stoch_d"] = calculate_stoch_rsi(df["close"])
    df["bb_upper"], df["bb_middle"], df["bb_lower"] = calculate_bollinger(df["close"])
    df["sma20"] = calculate_sma(df["close"], 20)
    df["ema20"] = calculate_ema(df["close"], 20)
    df["atr"] = calculate_atr(df, 14)
    st_line, st_dir = calculate_supertrend(df, 10, 2)
    df["st_line"] = st_line
    df["st_dir"] = st_dir
    df = df.dropna()
    if df.empty: return []
    
    signals = find_signals(df)
    positions = {}
    for sig in sorted(signals, key=lambda x: x['date']):
        ind = sig['indicator']
        if ind not in positions:
            positions[ind] = {'in_pos': False, 'entry_signal': None}
        if not positions[ind]['in_pos'] and sig['type'] == 'Buy':
            positions[ind]['in_pos'] = True
            positions[ind]['entry_signal'] = sig
        elif positions[ind]['in_pos'] and sig['type'] == 'Sell':
            positions[ind]['in_pos'] = False
            
    opps = []
    try:
        current_price = round(float(yf.Ticker(sym).fast_info.last_price), 2)
    except:
        current_price = round(float(df.iloc[-1]['close']), 2)
    
    for ind, pos in positions.items():
        if pos['in_pos']:
            opps.append({
                'symbol': sym,
                'indicator': ind,
                'buy_date': pos['entry_signal']['date'],
                'buy_price': pos['entry_signal']['price'],
                'reason': pos['entry_signal']['reason'],
                'current_price': current_price,
                'profit_pct': round((current_price / pos['entry_signal']['price'] - 1) * 100, 2)
            })
    return opps

def fetch_single_for_scanner(sym):
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period="730d", interval="1h")
        if df.empty: return []
        return extract_opportunities(df, sym)
    except:
        return []

@app.route("/api/scanner")
def api_scanner():
    try:
        all_opps = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_sym = {executor.submit(fetch_single_for_scanner, sym): sym for sym in BIST30_SYMBOLS}
            for future in concurrent.futures.as_completed(future_to_sym):
                opps = future.result()
                if opps:
                    all_opps.extend(opps)
                    
        sorted_opps = sorted(all_opps, key=lambda x: x['buy_date'], reverse=True)
        return jsonify({"opportunities": sorted_opps})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Borsa AI Robot başlatılıyor...")
    print("📈 BIST30 Modu Aktif")
    print("🌐 http://localhost:5000 adresini açın")
    app.run(debug=True, port=5000)
