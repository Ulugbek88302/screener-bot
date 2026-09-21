import time
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ==================== SOZLAMALAR ====================
TELEGRAM_BOT_TOKEN = "8596994937:AAHbKy0sgdRyPi47EvRLp9nRwSf_1W_oT-k"
TELEGRAM_CHAT_ID = "6603460497"

TICKERS = [
    "NVDA", "TSLA", "AAPL", "AMZN", "MSFT", "AMD",
    "SMCI", "AVGO", "PLTR", "COIN", "MSTR",
    "SPY", "QQQ", "VIX"
]

MIN_PREMIUM = 50000     # $50,000+
MIN_VOL_OI_RATIO = 1.1  # 1.1x va undan yuqori
# ====================================================

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram xatosi: {e}", flush=True)

def analyze_options(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # Render'da 5 minutlik interval ham, Yahoo Finance ham muammosiz ishlaydi
        hist = stock.history(period="1d", interval="5m")
        if hist.empty or len(hist) < 2:
            return
            
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change_5m = ((current_price - prev_price) / prev_price) * 100
        avg_volume = hist['Volume'].mean()
        
        options_dates = stock.options
        if not options_dates:
            return
            
        target_exp = options_dates[0]
        opt_chain = stock.option_chain(target_exp)
        
        for opt_type, chain in [("CALL", opt_chain.calls), ("PUT", opt_chain.puts)]:
            for _, row in chain.iterrows():
                volume = row.get('volume', 0)
                open_interest = row.get('openInterest', 1) or 1
                last_price = row.get('lastPrice', 0)
                strike = row['strike']
                
                volume = 0 if pd.isna(volume) else volume
                open_interest = 1 if pd.isna(open_interest) or open_interest == 0 else open_interest
                last_price = 0 if pd.isna(last_price) else last_price
                
                premium = volume * last_price * 100
                vol_oi_ratio = volume / open_interest

                if premium >= MIN_PREMIUM and vol_oi_ratio >= MIN_VOL_OI_RATIO:
                    est_tz = pytz.timezone('US/Eastern')
                    time_est = datetime.now(est_tz).strftime('%H:%M:%S')
                    
                    if opt_type == "CALL" and strike > current_price:
                        direction = "🟢 CALL / BUYLAR"
                    elif opt_type == "PUT" and strike < current_price:
                        direction = "🔴 PUT / SELLLAR"
                    else:
                        continue

                    msg = f"""🚨 **KITLAR HARAKATI (WHALE ALERT)** 🚨

📌 **Aksiya:** {ticker_symbol}
📊 **Yo'nalish:** {direction}
💵 **Hozirgi Narx:** ${current_price:.2f}
📈 **5 Min O'zgarish:** {change_5m:+.2f}%
🔥 **Hajm (Volume):** {volume:,.0f} (O'rtacha: {avg_volume:,.0f})

⏰ **Vaqt (EST):** {time_est}"""

                    print(f"[+] Signal: {ticker_symbol} {opt_type} ${strike}", flush=True)
                    send_telegram_msg(msg)
                    time.sleep(2)

    except Exception as e:
        print(f"Xatolik ({ticker_symbol}): {e}", flush=True)

def main():
    print("Screener ishga tushdi...", flush=True)
    send_telegram_msg("🚀 **Screener Bot Render'da ishga tushirildi!**")
    
    while True:
        for ticker in TICKERS:
            analyze_options(ticker)
        
        time.sleep(180)

if __name__ == "__main__":
    main()
