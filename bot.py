import hashlib
import hmac
import requests
import time
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

base_url = 'https://api.delta.exchange'
api_key = os.getenv('DELTA_API_KEY')
api_secret = os.getenv('DELTA_API_SECRET')

# Set Telegram bot token and chat id directly
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def generate_signature(secret, message):
    message = bytes(message, 'utf-8')
    secret = bytes(secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    return hash.hexdigest()

# Get open orders
method = 'GET'
timestamp = str(int(time.time()))
path = '/v2/orders'
url = f'{base_url}{path}'
query_string = '?product_id=1&state=open'
payload = ''
signature_data = method + timestamp + path + query_string + payload
signature = generate_signature(api_secret, signature_data)

req_headers = {
  'api-key': api_key,
  'timestamp': timestamp,
  'signature': signature,
  'User-Agent': 'python-rest-client',
  'Content-Type': 'application/json'
}

query = {"product_id": 1, "state": 'open'}

response = requests.request(
    method, url, data=payload, params=query, timeout=(3, 27), headers=req_headers
)

# Place new order
method = 'POST'
timestamp = str(int(time.time()))
path = '/v2/orders'
url = f'{base_url}{path}'
query_string = ''
payload = "{\"order_type\":\"limit_order\",\"size\":3,\"side\":\"buy\",\"limit_price\":\"0.0005\",\"product_id\":16}"
signature_data = method + timestamp + path + query_string + payload
signature = generate_signature(api_secret, signature_data)

req_headers = {
  'api-key': api_key,
  'timestamp': timestamp,
  'signature': signature,
  'User-Agent': 'rest-client',
  'Content-Type': 'application/json'
}

response = requests.request(
    method, url, data=payload, params={}, timeout=(3, 27), headers=req_headers
)

def fetch_tickers():
    url = f'{base_url}/v2/tickers'
    headers = {
        'api-key': api_key,
        'User-Agent': 'python-rest-client',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data or 'result' not in data or not data['result']:
        print('No ticker data found.')
        return None
    ticker = data['result'][0]
    name = ticker.get('description', 'Unknown')
    symbol = ticker.get('symbol', 'N/A')
    market_cap = ticker.get('oi_value_usd', '0.00')
    liquidity = ticker.get('mark_price', '0.00')
    vol_24h = ticker.get('mark_change_24h', '0.00')
    score = 2
    rating = 4
    buys_1m = 2125.49
    sells_1m = 989.19
    buy_sell_ratio = 2.15
    unique_wallets = 55
    dev_percent = 0.00
    top10_percent = 16.72
    url = ticker.get('symbol', 'N/A')
    message = f"""
    🚀 {name} ({symbol})\n🔗 {url}\n\n📊 Score: {score}/10   ⭐️ Rating: {rating}/10\n\n💰 Market Cap: ${float(market_cap):,.2f}   💧 Liquidity: ${float(liquidity):,.2f}\n\n📈 24h Vol: ${float(vol_24h):,.2f}\n\n🟢 Buys (1m): ${buys_1m:,.2f}   🔴 Sells (1m): ${sells_1m:,.2f}\n\n🔄 Buy/Sell Ratio: {buy_sell_ratio}   👥 Unique Wallets (1m): {unique_wallets}\n\n🛠️ Dev: {dev_percent:.2f}%   🏆 Top 10: {top10_percent:.2f}%\n"""
    print('Fetched message:')
    print(message)
    return message

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)
    print('Message sent to Telegram!')

# Handler for /news command
async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /news command from chat_id: {update.effective_chat.id}")
    url = f'{base_url}/v2/tickers'
    headers = {
        'api-key': api_key,
        'User-Agent': 'python-rest-client',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data or 'result' not in data or not data['result']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No news available.")
        print('No news available message sent to Telegram!')
        return
    ticker = data['result'][0]
    # Build message only with real API fields
    name = ticker.get('description')
    symbol = ticker.get('symbol')
    market_cap = ticker.get('oi_value_usd')
    liquidity = ticker.get('mark_price')
    vol_24h = ticker.get('mark_change_24h')
    # Generate a link to the Delta Exchange product page in the correct format
    base = symbol[:-3] if symbol and len(symbol) > 3 else symbol
    link = f"https://www.delta.exchange/app/futures/trade/{base}/{symbol}" if symbol else None

    message = f"🚀 {name} ({symbol})\n"
    if link:
        message += f"🔗 {link}\n"
    if market_cap is not None and liquidity is not None:
        message += f"\n💰 Market Cap: ${float(market_cap):,.2f}   💧 Liquidity: ${float(liquidity):,.2f}"
    elif market_cap is not None:
        message += f"\n💰 Market Cap: ${float(market_cap):,.2f}"
    elif liquidity is not None:
        message += f"\n💧 Liquidity: ${float(liquidity):,.2f}"
    if vol_24h is not None:
        message += f"\n\n📈 24h Vol: ${float(vol_24h):,.2f}"

    print('Fetched message:')
    print(message)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    print('Message sent to Telegram!')

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("news", news_command))
    print("Bot is running. Send /news in your Telegram chat to get the latest news.")
    app.run_polling()