import os
import time
import requests
import yfinance as yf
from datetime import datetime
import pytz

# Render muhitidan tokenni olish
TELEGRAM_BOT_TOKEN = os.getenv("8596994937:AAHbKy0sgdRyPi47EvRLp9nRwSf_1W_oT-k")
CHAT_ID = os.getenv("6603460497")

def send_telegram_message(text):
    """Telegramga xabar yuborish"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Xatolik: {e}")

def run_screener():
    # 📌 Kuzatilishi kerak bo'lgan aksiyalar ro'yxati (xohlaganingizni qo'shishingiz mumkin)
    watchlist = ["TSLA", "NVDA", "AAPL", "AMD", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "INTC",
    "SMCI", "GME", "AMC", "HIMS", "SOFI", "SNAP", "ROKU", "UBER", "RIVN", "NIO",
    "COIN", "MSTR", "ARM", "SNDK", "SQ", "SHOP", "BABA", "AXTI", "BA", "AAOI"]
    
    est_tz = pytz.timezone('US/Eastern')
    current_time_est = datetime.now(est_tz).strftime('%H:%M:%S')

    print("Screener tekshiruvni boshladi...")

    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if len(hist) < 2:
                continue

            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
            
            volume = hist['Volume'].iloc[-1]
            info = ticker.info
            avg_volume = info.get('averageVolume', 500000)

            # Narx o'zgarishiga qarab yo'nalish
            direction = "🔴 PUT / SELLLAR" if change < 0 else "🟢 CALL / XARID"
            
            # Xabar formati
            message = f"""
🚨 **KITLAR HARAKATI (WHALE ALERT)** 🚨

📌 Aksiya: `{symbol}`
📊 Yo'nalish: `{direction}`
💵 Hozirgi Narx: `${round(current_price, 2)}`
📈 Kunlik O'zgarish: `{'+' if change > 0 else ''}{round(change, 2)}%`
🔥 Hajm (Volume): `{int(volume):,}` (O'rtacha: `{int(avg_volume):,}`)

⏰ Vaqt (EST): `{current_time_est}`
            """.strip()

            send_telegram_message(message)
            
            # Telegram bloklab qo'ymasligi uchun har bir xabar orasida 1.5 soniya kutamiz
            time.sleep(1.5)
            
        except Exception as e:
            print(f"{symbol} tahlil qilishda xatolik: {e}")

if __name__ == "__main__":
    print("Screener bot ishga tushdi va uzluksiz rejimga o'tdi...")
    while True:
        run_screener()
        # ⏳ Har 1 soatda (3600 soniya) qaytadan tekshiradi. 
        # Vaqtni o'zgartirmoqchi bo'lsangiz, soniyani o'zgartirasiz (masalan, 30 minut uchun 1800)
        time.sleep(1800)
