import os
import json
import urllib.request
import urllib.error
import yfinance as yf
import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from indicators import (
    calculate_macd,
    calculate_rsi,
    calculate_stoch_rsi,
    calculate_bollinger,
    find_buy_signals,
    compute_signal_returns,
)

load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

SYMBOL = "ALBRK.IS"

# desteklenen periyotlar
INTERVALS = {
    "1h":  {"period": "5d",  "yf_interval": "1h"},
    "1d":  {"period": "3y",  "yf_interval": "1d"},
    "1wk": {"period": "5y",  "yf_interval": "1wk"},
    "1mo": {"period": "10y", "yf_interval": "1mo"},
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


def fetch_data(interval: str = "1d"):
    """ALBRK hissesini Yahoo Finance'den çeker ve indikatörleri ekler."""
    cfg = INTERVALS.get(interval, INTERVALS["1d"])
    ticker = yf.Ticker(SYMBOL)
    df = ticker.history(period=cfg["period"], interval=cfg["yf_interval"])
    df.index = pd.to_datetime(df.index.tz_localize(None) if df.index.tz else df.index)
    df.columns = [c.lower() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].dropna()

    # İndikatörleri hesapla
    df["macd"], df["macd_signal"], df["macd_hist"] = calculate_macd(df["close"])
    df["rsi"] = calculate_rsi(df["close"])
    df["stoch_k"], df["stoch_d"] = calculate_stoch_rsi(df["close"])
    df["bb_upper"], df["bb_middle"], df["bb_lower"] = calculate_bollinger(df["close"])

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
        if interval not in INTERVALS:
            interval = "1d"
        df = fetch_data(interval)

        def to_list(series):
            return [round(float(x), 4) if pd.notna(x) else None for x in series]

        return jsonify({
            "symbol": SYMBOL,
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
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/signals")
def api_signals():
    """Al sinyallerini ve getiri analizini döner (daima günlük periyotta)."""
    try:
        df = fetch_data("1d")
        signals = find_buy_signals(df)
        results = compute_signal_returns(df, signals)
        return jsonify({"signals": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze")
def api_analyze():
    """Gemini API ile mevcut duruma göre AI yorumu üretir."""
    try:
        df = fetch_data()
        last = df.iloc[-1]
        prev = df.iloc[-2]

        # Son sinyaller
        signals = find_buy_signals(df)
        last_signals = signals[-5:] if len(signals) >= 5 else signals

        # Özet metni oluştur
        summary = f"""
ALBRK.IS (Albaraka Türk) Hisse Analiz Özeti ({df.index[-1].strftime('%Y-%m-%d')}):

Son Fiyat: {last['close']:.2f} TL
RSI (14): {last['rsi']:.1f} {'(Aşırı Satım < 35)' if last['rsi'] < 35 else '(Aşırı Alım > 70)' if last['rsi'] > 70 else '(Normal Bölge)'}
MACD: {last['macd']:.4f}, Signal: {last['macd_signal']:.4f}, Histogram: {last['macd_hist']:.4f}
Stochastic RSI K: {last['stoch_k']:.1f}, D: {last['stoch_d']:.1f}
Bollinger Üst: {last['bb_upper']:.2f} | Orta: {last['bb_middle']:.2f} | Alt: {last['bb_lower']:.2f}
Fiyat Durumu: Bollinger {'alt bandının altında' if last['close'] < last['bb_lower'] else 'üst bandının üstünde' if last['close'] > last['bb_upper'] else 'bantlar arasında'}

Son 5 Al Sinyali:
"""
        for s in last_signals:
            summary += f"  - {s['date']}: {s['price']} TL ({s['reason']}) | 1M getiri: {s.get('ret_1m', 'N/A')}%\n"

        prompt = f"""Sen bir Türk borsası teknik analiz uzmanısın. 
Aşağıdaki ALBRK hissesi teknik analiz verilerini inceleyerek:
1. Mevcut teknik görünüm hakkında kısa bir yorum yap
2. İndikatörlerin ne söylediğini açıkla
3. Kısa vadeli (1-4 hafta) olası senaryo hakkında fikir ver
4. Risk faktörlerini belirt

Yanıtını Türkçe ver ve 4-5 paragraf tut.

{summary}"""

        analysis = gemini_generate(prompt)
        return jsonify({"analysis": analysis, "date": df.index[-1].strftime("%Y-%m-%d")})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Borsa AI Robot başlatılıyor...")
    print(f"📈 Hisse: {SYMBOL}")
    print("🌐 http://localhost:5000 adresini açın")
    app.run(debug=True, port=5000)
