import yfinance as yf
import pandas as pd
import requests
import time

# 1. Telegram Sozlamalari
BOT_TOKEN = "8596994937:AAHbKy0sgdRyPi47EvRLp9nRwSf_1W_oT-k"  # BotFather tokenini kiriting
CHAT_ID = "6603460497"      # Chat ID ingizni kiriting

# 2. Skaner qilinadigan aksiyalar ro'yxati
TICKERS = ["NVDA", "TSLA", "AAPL", "AMD", "AMZN", "MSFT", "HIMS", "GOOGL", "SMCI"]

# Yuborilgan signallarni saqlash uchun to'plam (takrorlanmaslik uchun)
sent_signals = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        if not res_data.get("ok"):
            print(f"❌ Telegram xatosi: {res_data.get('description')}")
        else:
            print("✅ Telegramga yuborildi!")
    except Exception as e:
        print(f"Ulanishda xatolik: {e}")

def calculate_conviction(vol_oi_ratio, premium, iv):
    score = 40
    if vol_oi_ratio > 3.0: score += 25
    elif vol_oi_ratio > 1.5: score += 15
    
    if premium > 1_000_000: score += 20
    elif premium > 250_000: score += 10
    
    if iv > 0.50: score += 15
    return min(score, 100)

def scan_market():
    print(f"\n🔍 [{time.strftime('%H:%M:%S')}] Bozor skaner qilinmoqda...")
    
    for symbol in TICKERS:
        try:
            stock = yf.Ticker(symbol)
            history = stock.history(period="1d")
            if history.empty: continue
            current_price = history['Close'].iloc[-1]
            
            expirations = stock.options
            if not expirations: continue
            
            target_date = expirations[0]
            opt_chain = stock.option_chain(target_date)
            calls = opt_chain.calls
            
            # Filtrlash: Vol > 500 va Vol/OI >= 1.5
            filtered = calls[(calls['volume'] > 500) & (calls['openInterest'] > 0)]
            filtered = filtered[filtered['volume'] / filtered['openInterest'] >= 1.5]
            
            for _, row in filtered.iterrows():
                vol_oi_ratio = row['volume'] / row['openInterest']
                premium = row['lastPrice'] * row['volume'] * 100
                
                if premium < 100_000: continue
                
                # Noyob ID yaratish (Takroriy xabar yubormaslik uchun)
                signal_id = f"{symbol}_{row['strike']}_{target_date}_{row['volume']}"
                if signal_id in sent_signals:
                    continue  # Bu signal ilgari yuborilgan, o'tkazib yuboramiz
                
                conviction = calculate_conviction(vol_oi_ratio, premium, row['impliedVolatility'])
                
                message = (
                    f"🔥 *NeXuS AI | WHALE FLOW v4.0* 🐋\n\n"
                    f"🏢 *Ticker:* ${symbol}\n"
                    f"🚀 *Yo'nalish:* KO'TARILISH 🟢 (CALL FLOW)\n"
                    f"🎯 *CALL CONVICTION:* {conviction}/100\n\n"
                    f"📋 *Opsion Tafsilotlari:*\n"
                    f"🎯 *Strike:* ${row['strike']}C | *Joriy:* ${current_price:.2f}\n"
                    f"📅 *Muddat:* {target_date}\n"
                    f"💸 *Premium:* ${premium:,.2f} 💰\n"
                    f"🌊 *Hajm/OI:* {vol_oi_ratio:.2f}x 🔥 (Vol: {int(row['volume'])} | OI: {int(row['openInterest'])})\n"
                    f"📊 *IV:* {row['impliedVolatility']*100:.1f}%\n"
                )
                
                send_telegram_message(message)
                sent_signals.add(signal_id)
                
        except Exception:
            continue

# Cheksiz sikl: Har 5 daqiqada (300 soniya) skaner qiladi
if __name__ == "__main__":
    print("🚀 Whale Flow Bot doimiy rejimda ishga tushdi...")
    while True:
        scan_market()
        time.sleep(300) # 300 soniya = 5 daqiqa
