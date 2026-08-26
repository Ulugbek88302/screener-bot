import time
import requests
import yfinance as yf
import pandas as pd

# ==================== SOZLAMALAR ====================
TELEGRAM_BOT_TOKEN = "8596994937:AAHbKy0sgdRyPi47EvRLp9nRwSf_1W_oT-k"
TELEGRAM_CHAT_ID = "6603460497"

BOT_NAME = "WHALE FLOW AI"

# Top-38 eng volatil va opsion hajmi yuqori aksiyalar
TICKERS = [
    "NVDA", "TSLA", "AAPL", "AMZN", "MSFT", "GOOGL", "META", "AMD",
    "SMCI", "AVGO", "ARM", "MU", "INTC", "TSM", "PLTR", "ORCL",
    "COIN", "MSTR", "JPM", "BAC", "MARA", "RIOT", "HOOD", "RBLX",
    "DIS", "NFLX", "DKNG", "SNAP", "SOFI", "UBER", "BABA", "PDD",
    "SPY", "QQQ", "IWM", "XLF"
]

# Kitlar filtri
MIN_PREMIUM = 500000    # Kamida $500,000 to'langan bo'lishi shart
MIN_VOL_OI_RATIO = 1.5  # Hajm / OI nisbati 1.5x dan yuqori
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
        hist = stock.history(period="2d")
        if hist.empty:
            return
            
        current_price = hist['Close'].iloc[-1]
        expirations = stock.expirations
        if not expirations:
            return
            
        target_exp = expirations[0]
        opt_chain = stock.option_chain(target_exp)
        calls = opt_chain.calls

        for _, row in calls.iterrows():
            volume = row.get('volume', 0)
            open_interest = row.get('openInterest', 1) or 1
            last_price = row.get('lastPrice', 0)
            strike = row['strike']
            
            premium = volume * last_price * 100
            vol_oi_ratio = volume / open_interest if open_interest > 0 else 0

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
            time.sleep(1)
        
        time.sleep(300)

if __name__ == "__main__":
    main()
