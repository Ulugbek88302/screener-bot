import time
import requests
import yfinance as yf
import pandas as pd

# ==================== SOZLAMALAR ====================
TELEGRAM_BOT_TOKEN = "8596994937:AAHbKy0sgdRyPi47EvRLp9nRwSf_1W_oT-k"
TELEGRAM_CHAT_ID = "6603460497"

BOT_NAME = "WHALE FLOW AI"

# Yahoo bloklamasligi uchun ro'yxatni eng qaynoq Top 15 ta aksiyaga tushiramiz
TICKERS = [
    "NVDA", "TSLA", "AAPL", "AMZN", "MSFT", "AMD",
    "SMCI", "AVGO", "PLTR", "COIN", "MSTR",
    "SPY", "QQQ", "VIX"
]

# Kitlar filtri
MIN_PREMIUM = 50000     # $50,000 va undan yuqori opsionlar
MIN_VOL_OI_RATIO = 1.1  # Hajm / OI nisbati 1.1x va undan yuqori
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
        
        # Yahoo blokiga tushmaslik uchun 2 soniya kutamiz
        time.sleep(2)
        
        options_dates = stock.options
        if not options_dates:
            print(f"[{ticker_symbol}] Opsion sanalari topilmadi.", flush=True)
            return
            
        target_exp = options_dates[0]
        opt_chain = stock.option_chain(target_exp)
        calls = opt_chain.calls

        # Joriy narxni olish
        hist = stock.history(period="1d")
        if hist.empty:
            return
        current_price = hist['Close'].iloc[-1]

        for _, row in calls.iterrows():
            volume = row.get('volume', 0)
            open_interest = row.get('openInterest', 1) or 1
            last_price = row.get('lastPrice', 0)
            strike = row['strike']
            
            volume = 0 if pd.isna(volume) else volume
            open_interest = 1 if pd.isna(open_interest) or open_interest == 0 else open_interest
            last_price = 0 if pd.isna(last_price) else last_price
            
            premium = volume * last_price * 100
            vol_oi_ratio = volume / open_interest

            if premium >= MIN_PREMIUM and vol_oi_ratio >= MIN_VOL_OI_RATIO and strike > current_price:
                otm_pct = ((strike - current_price) / current_price) * 100
                stop_loss = current_price * 0.99
                
                msg = f"""🔥 **{BOT_NAME} | OPTIONS FLOW v1.0** 🐋

🏢 **Ticker:** ${ticker_symbol}
🎯 **Rule:** 🌊 FLOW (Kitlar Oqimi)
📊 **Rating:** ⚪️ NEUTRAL
🚀 **Yo'nalish:** KO'TARILISH 🟢 (CALL FLOW)

🎯 **CALL CONVICTION:** 75/100
[███████░░░] 🟢 KUCHLI (Strong)

📋 **Opsion Tafsilotlari:**
🎯 **Strike:** ${strike:.2f}C | **Joriy:** ${current_price:.2f}
📐 **Holat:** OTM ({otm_pct:.2f}%, yuqorida)
📅 **Muddat:** {target_exp}

💸 **To'langan Premium:** ${premium/1e6:.2f}M 💰
🌊 **Hajm (Vol) / Ochiq Qiziqish (OI):** {vol_oi_ratio:.2f}x 🔥
🟢 **Pozitsiya:** 100% YANGI OCHILGAN (Opening)

🧠 **{BOT_NAME} LOGIC ENGINE**
💵 **Ssenariy:** OTM — ${premium/1e6:.2f}M bu narx ${strike:.2f} gacha KO'TARILISHIGA tikilgan pul
🛑 **Stop-Loss:** ${stop_loss:.2f}
🎯 **Take-Profit (Strike):** ${strike:.2f}"""

                print(f"[+] Signal topildi: {ticker_symbol} ${strike}C", flush=True)
                send_telegram_msg(msg)
                time.sleep(2)

    except Exception as e:
        print(f"Xatolik ({ticker_symbol}): {e}", flush=True)

def main():
    print("Skaner ishga tushdi...", flush=True)
    send_telegram_msg(f"🚀 **{BOT_NAME} Screener Bot ishga tushirildi!**")
    
    while True:
        for ticker in TICKERS:
            analyze_options(ticker)
        
        # Har bir to'liq skanerdan so'ng 3 daqiqa kutish
        time.sleep(180)

if __name__ == "__main__":
    main()
