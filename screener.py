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
BOT_TOKEN = "8596994937:AAHbKy0sgdRyPi47EvRLp9nRwSf_1W_oT-k"  # O'zingizning Tokeningizni yozing
CHAT_ID = "6603460497"      # O'zingizning Chat ID'ingizni yozing

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
                # Skanerlash mantiqiy kodi shu yerda bajariladi
                print(f"Skanerlanmoqda: {ticker}")
            except Exception as e:
                print(f"Xatolik {ticker}: {e}")
            time.sleep(2)  # Bloklanishning oldini olish uchun pauza
            
        print("Barcha aksiyalar skanerlandi. 5 daqiqa kutilmoqda...")
        time.sleep(300)

if __name__ == "__main__":
    # Veb-serverni orqa fonda (background thread) yurgizish
    t = Thread(target=run_web_server)
    t.start()
    
    # Skanerni ishga tushirish
    run_screener()
