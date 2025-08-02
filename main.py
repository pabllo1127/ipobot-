import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask
import os

# === CONFIG (Use environment variables for security) ===
TELEGRAM_BOT_TOKEN = os.getenv('8394355650:AAH--hYYBwkyLfn9aHN_r_SOmig9jFKXsxo')
CHAT_ID = os.getenv('8162201982')
FINNHUB_API_KEY = os.getenv('d22h8mhr01qr7ajlf95gd22h8mhr01qr7ajlf960')
GNEWS_API_KEY = os.getenv('5d53c4541a8e693df4da98e78c01f142')

# === TELEGRAM ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

# === IPOs ===
def fetch_ipo_news():
    today = datetime.now().strftime("%Y-%m-%d")
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    url = f"https://finnhub.io/api/v1/calendar/ipo?from={today}&to={future}&token={FINNHUB_API_KEY}"
    try:
        res = requests.get(url)
        ipos = res.json().get("ipoCalendar", [])
        return [f"📈 {i['name']} | {i['exchange']} | {i['date']} | ${i['price']}" 
                for i in ipos if 'name' in i and 'exchange' in i and 'price' in i]
    except Exception as e:
        print(f"❌ IPO Error: {e}")
        return []

# === GNews Fetch ===
def fetch_gnews_articles(query):
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&token={GNEWS_API_KEY}&max=5"
    try:
        res = requests.get(url)
        articles = res.json().get("articles", [])
        return [f"📰 {a['title']}\n{a['url']}" for a in articles]
    except Exception as e:
        print(f"❌ GNews Error for query '{query}': {e}")
        return []

# === Congress Trades (QuiverQuant Scraper) ===
def fetch_congress_trades():
    try:
        url = 'https://www.quiverquant.com/congresstrading'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tbody tr')[:5]  # Get top 5
        trades = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                name = cols[0].text.strip()
                ticker = cols[1].text.strip()
                amount = cols[3].text.strip()
                date = cols[4].text.strip()
                trades.append(f"🧾 {name} | {ticker} | {amount} | {date}")
        return trades if trades else ["No recent congress trades found."]
    except Exception as e:
        print(f"❌ Congress Scrape Error: {e}")
        return ["❌ Error fetching Congress Trades data"]

# === HOUSE STOCK WATCHER PLACEHOLDER ===
def fetch_housewatcher_error():
    return ["❌ Error fetching HouseStockWatcher data: HTTPSConnectionPool(host='housestockwatcher.com', port=443): Max retries exceeded with url: /transactions (Caused by NameResolutionError('<urllib3.connection object>: Failed to resolve'))"]

# === AGGREGATOR ===
def run_all_news_tasks():
    ipo_news = fetch_ipo_news()
    ma_news = fetch_gnews_articles("merger OR acquisition OR takeover")
    geo_news = fetch_gnews_articles("military contract OR reconstruction OR geopolitical")
    med_news = fetch_gnews_articles("medical breakthrough OR FDA approval OR new drug")
    ai_news = fetch_gnews_articles("AI OR robotics OR artificial intelligence")
    energy_news = fetch_gnews_articles("energy OR oil OR gas OR solar")
    mining_news = fetch_gnews_articles("rare earth OR lithium OR copper OR gold discovery")
    tech_news = fetch_gnews_articles("smartphone OR semiconductor OR PC OR chip")
    quiver_trades = fetch_congress_trades()
    house_trades = fetch_housewatcher_error()

    message_parts = []
    message_parts.extend(["🔝 Top 5 QuiverQuant Trades:"] + quiver_trades + [""])
    message_parts.extend(["🕒 HouseStockWatcher - Last 24h:"] + house_trades + [""])
    message_parts.append("📢 Upcoming IPOs:")
    message_parts.extend(ipo_news or ["No recent IPOs."])
    message_parts.append("")
    message_parts.append("💼 M&A News:")
    message_parts.extend(ma_news or ["No recent M&A headlines."])
    message_parts.append("")
    message_parts.append("🌍 Geopolitics & Contract News:")
    message_parts.extend(geo_news or ["No recent 🌍 news."])
    message_parts.append("")
    message_parts.append("🧬 Medical Breakthroughs:")
    message_parts.extend(med_news or ["No recent 🧬 news."])
    message_parts.append("")
    message_parts.append("🤖 AI & Robotics News:")
    message_parts.extend(ai_news or ["No recent 🤖 news."])
    message_parts.append("")
    message_parts.append("⚡️ Energy Sector News:")
    message_parts.extend(energy_news or ["No recent ⚡️ news."])
    message_parts.append("")
    message_parts.append("⛏️ Mining & Commodities:")
    message_parts.extend(mining_news or ["No recent ⛏️ news."])
    message_parts.append("")
    message_parts.append("📱 Tech & Devices:")
    message_parts.extend(tech_news or ["No recent 📱 news."])

    message = "\n".join(message_parts)
    send_telegram(message)

# === FLASK APP FOR RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    run_all_news_tasks()
    return "✅ Market Intel Bot is running and sent the news."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
