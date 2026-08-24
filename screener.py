import os
import time
import requests
import pandas as pd
import yfinance as yf
from threading import Thread
from flask import Flask

# Render serveri uchun mini veb-server
app = Flask('')

@app.route('/')
def home():
    return "Whale Screener is Running 24/7!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# TELEGRAM SOZLAMALARI
BOT_TOKEN = "8596994937:AAHbKy0sgdRyPi47EvRLp9nRwSf_1W_oT-k"
CHAT_ID = "6603460497"

# Kuzatiladigan Top aksiyalar ro'yxati
TICKERS = [
    "NVDA", "TSLA", "AAPL", "AMD", "AMZN", "MSFT", "META", "GOOGL", "NFLX", "AVGO", 
    "PLTR", "SMCI", "JPM", "BAC", "GS", "MS", "C", "MA", "V", "INTC", 
    "MU", "QCOM", "ARM", "BA", "CAT", "WMT", "COST", "DIS", "NKE", "XOM", 
    "CVX", "LLY", "UNH", "SPY", "QQQ"
]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram xatosi: {e}")

def run_screener():
    print("Whale Screener ishga tushdi...")
    send_telegram("🚀 **Whale Screener Bot Render'da 24/7 ishga tushirildi!**")
    
    while True:
        for ticker in TICKERS:
            try:
                stock = yf.Ticker(ticker)
                # Oxirgi 2 kunlik 5 daqiqalik ma'lumotlarni olish
                df = stock.history(period="1d", interval="5m")
                
                if not df.empty and len(df) > 1:
                    last_row = df.iloc[-1]
                    prev_row = df.iloc[-2]
                    
                    price = last_row['Close']
                    volume = last_row['Volume']
                    avg_volume = df['Volume'].mean()
                    
                    # O'sish yoki tushish foizi
                    price_change = ((price - prev_row['Close']) / prev_row['Close']) * 100
                    
                    # SHART: Hajm o'rtachadan 2.5 baravar ko'p va narx 0.8% dan ko'p o'zgargan bo'lsa (Kitlar kirishi)
                    if volume > (avg_volume * 2.5) and abs(price_change) >= 0.8:
                        direction = "🟢 CALL / BUYLAR" if price_change > 0 else "🔴 PUT / SELLLAR"
                        
                        msg = (
                            f"🚨 **KITLAR HARAKATI (WHALE ALERT)** 🚨\n\n"
                            f"📌 **Aksiya:** `{ticker}`\n"
                            f"📊 **Yo'nalish:** {direction}\n"
                            f"💵 **Hozirgi Narx:** `${price:.2f}`\n"
                            f"📈 **5 Min O'zgarish:** `{price_change:.2f}%`\n"
                            f"🔥 **Hajm (Volume):** `{volume:,}` (O'rtacha: `{int(avg_volume):,}`)\n\n"
                            f"⏰ *Vaqt (EST):* {last_row.name.strftime('%H:%M:%S')}"
                        )
                        send_telegram(msg)
                        print(f"SIGNAL YUBORILDI: {ticker}")
                    else:
                        print(f"Skanerlandi: {ticker} | Narx: ${price:.2f} | Hajm: {volume}")
                        
            except Exception as e:
                print(f"Xatolik {ticker}: {e}")
                
            time.sleep(2)  # Bloklanishning oldini olish uchun
            
        print("Barcha aksiyalar skanerlandi. 5 daqiqa kutilmoqda...")
        time.sleep(300)

if __name__ == "__main__":
    t = Thread(target=run_web_server)
    t.start()
    run_screener()
