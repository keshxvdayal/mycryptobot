# API KEY= 0e8860cf5bd69a68c62fb45b16b5f55d2582f2e45be80bd86cffab5aeb4d07f6
# SECRET KEY = cf38c35222ee745ffbf6dd215b70ac2614e6121abc5c32c3b1a95982e4b01250
import requests
import time
import json
import random
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlencode
from cryptography.hazmat.primitives.asymmetric import ed25519
from telegram.ext import Application, CommandHandler
from telegram.ext import ContextTypes
from telegram import Update

load_dotenv()

API_KEY = os.getenv("COINSWITCH_API_KEY")
SECRET_KEY = os.getenv("COINSWITCH_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def safe_float(val, fmt="{:.4f}"):
    try:
        if val is not None and val != "":
            return fmt.format(float(val))
    except Exception:
        pass
    return "N/A"

async def fetch_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /fetch command from chat_id: {update.effective_chat.id}")

    params = {
        "exchange": "EXCHANGE_2"
    }
    endpoint = "/trade/api/v2/futures/all-pairs/ticker"
    method = "GET"
    epoch_time = str(int(time.time() * 1000))
    endpoint_with_params = endpoint
    if method == "GET" and len(params) != 0:
        endpoint_with_params += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
        unquote_endpoint = endpoint_with_params
    else:
        unquote_endpoint = endpoint
    signature_msg = method + unquote_endpoint + epoch_time
    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(SECRET_KEY)
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()
    url = "https://coinswitch.co" + endpoint
    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': API_KEY,
        'X-AUTH-EPOCH': epoch_time
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        print("Response JSON:", data)
        
        
        formatted_data = []
        if isinstance(data, dict) and len(data) > 0:
            currency_keys = list(data.keys())
            for i, currency in enumerate(currency_keys, 1):
                # Add ID to the currency data itself
                currency_data = data[currency].copy()
                currency_data["id"] = i
                currency_data["symbol"] = currency
                
                formatted_data.append(currency_data)
        
    
        timestamp = int(time.time())
        filename = f"crypto_data_with_ids_1751147426.json"
        with open(filename, 'w') as f:
            json.dump(formatted_data, f, indent=2)
        
        print(f"Data with IDs stored in {filename}")
        print(f"Total currencies stored: {len(formatted_data)}")
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Data fetched and stored with IDs!\n📁 File: {filename}\n📊 Total currencies: {len(formatted_data)}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {e}")

async def test2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /test2 command from chat_id: {update.effective_chat.id}")
    
    
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'crypto' in f.lower()]
    if not json_files:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No stored data found. Please use /fetch to get data first.")
        return
    
    
    latest_file = max(json_files, key=os.path.getctime)
    print(f"Reading from {latest_file}")
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            
            currencies_obj = data[0]
            if isinstance(currencies_obj, dict):
                currency_keys = list(currencies_obj.keys())
                selected_currency = random.choice(currency_keys)
                currency_data = currencies_obj[selected_currency]
                
                print(f"Selected currency: {selected_currency}")
                
                
                symbol = currency_data.get('symbol', selected_currency)
                last_price = safe_float(currency_data.get('last_price'))
                price_change_24h = safe_float(currency_data.get('price_24h_pcnt'), "{:.2f}%")
                volume_24h = safe_float(currency_data.get('base_asset_volume_24h'), "{:.0f}")
                mark_price = safe_float(currency_data.get('mark_price'))
                funding_rate = safe_float(currency_data.get('funding_rate'), "{:.6f}")
                open_interest = safe_float(currency_data.get('open_interest'), "{:.0f}")
                low_24h = safe_float(currency_data.get('low_price_24h'))
                high_24h = safe_float(currency_data.get('high_price_24h'))
                
                
                message = f"🚀 {symbol}\n"
                message += f"🔗 https://coinswitch.co/trade/futures/{symbol}\n\n"
                message += f"💰 Last Price: ${last_price}   📊 Mark Price: ${mark_price}\n"
                message += f"📈 24h Change: {price_change_24h}\n"
                message += f"📊 24h Low: ${low_24h}   📈 24h High: ${high_24h}\n"
                message += f"💧 24h Volume: {volume_24h}\n"
                message += f"🏦 Funding Rate: {funding_rate}\n"
                message += f"📊 Open Interest: {open_interest}"
                
                print('Fetched message:')
                print(message)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                print('Message sent to Telegram!')
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid data structure in stored file.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No token data found in stored file.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {e}")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("fetch", fetch_data_command))
    app.add_handler(CommandHandler("test2", test2_command))
    print("Bot is running. Use /fetch to get data with IDs, then /test2 to get a random currency.")
    app.run_polling()