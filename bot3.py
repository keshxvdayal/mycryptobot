import requests
import time
import json
import random
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

# Binance API credentials (not needed for public market data)
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Telegram bot credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def safe_float(val, fmt="{:.4f}"):
    try:
        if val is not None and val != "":
            return fmt.format(float(val))
    except Exception:
        pass
    return "N/A"

def fetch_binance_data():
    """Fetch data from Binance public API"""
    try:
        # Get 24hr ticker for all symbols
        url = "https://data-api.binance.vision/api/v3/ticker/24hr"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully fetched data for {len(data)} symbols from Binance")
            return data
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return None

def fetch_specific_symbol_data(symbol):
    """Fetch detailed data for a specific symbol"""
    try:
        # Get 24hr ticker for specific symbol
        url = f"https://data-api.binance.vision/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully fetched data for {symbol}")
            return data
        else:
            print(f"Error fetching data for {symbol}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

async def binance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to fetch and display Binance data"""
    print(f"Received /binance command from chat_id: {update.effective_chat.id}")
    
    # Fetch data from Binance
    data = fetch_binance_data()
    
    if data and len(data) > 0:
        # Select a random symbol
        selected_symbol = random.choice(data)
        symbol = selected_symbol.get('symbol', 'Unknown')
        
        print(f"Selected symbol: {symbol}")
        print("Raw data:")
        print(json.dumps(selected_symbol, indent=2))
        
        # Extract important fields
        last_price = safe_float(selected_symbol.get('lastPrice'))
        price_change = safe_float(selected_symbol.get('priceChange'))
        price_change_percent = safe_float(selected_symbol.get('priceChangePercent'), "{:.2f}%")
        high_24h = safe_float(selected_symbol.get('highPrice'))
        low_24h = safe_float(selected_symbol.get('lowPrice'))
        volume = safe_float(selected_symbol.get('volume'), "{:.0f}")
        quote_volume = safe_float(selected_symbol.get('quoteVolume'), "{:.0f}")
        count = selected_symbol.get('count', 'N/A')
        
        # Build message
        message = f"🚀 {symbol} (Binance)\n"
        message += f"🔗 https://www.binance.com/en/trade/{symbol}\n\n"
        message += f"💰 Last Price: ${last_price}\n"
        message += f"📈 24h Change: {price_change_percent} (${price_change})\n"
        message += f"📊 24h High: ${high_24h}   📉 24h Low: ${low_24h}\n"
        message += f"💧 24h Volume: {volume} {symbol.replace('USDT', '')}\n"
        message += f"💵 Quote Volume: ${quote_volume}\n"
        message += f"🔄 Trade Count: {count}"
        
        print('Formatted message:')
        print(message)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        print('Message sent to Telegram!')
        
    else:
        error_msg = "Failed to fetch data from Binance"
        print(error_msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_msg)

async def symbol_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to fetch data for a specific symbol"""
    print(f"Received /symbol command from chat_id: {update.effective_chat.id}")
    
    # Get symbol from command arguments
    if context.args:
        symbol = context.args[0].upper()
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a symbol. Usage: /symbol BTCUSDT")
        return
    
    print(f"Fetching data for symbol: {symbol}")
    
    # Fetch data for specific symbol
    data = fetch_specific_symbol_data(symbol)
    
    if data:
        print("Raw data:")
        print(json.dumps(data, indent=2))
        
        # Extract important fields
        last_price = safe_float(data.get('lastPrice'))
        price_change = safe_float(data.get('priceChange'))
        price_change_percent = safe_float(data.get('priceChangePercent'), "{:.2f}%")
        high_24h = safe_float(data.get('highPrice'))
        low_24h = safe_float(data.get('lowPrice'))
        volume = safe_float(data.get('volume'), "{:.0f}")
        quote_volume = safe_float(data.get('quoteVolume'), "{:.0f}")
        count = data.get('count', 'N/A')
        
        # Build message
        message = f"🚀 {symbol} (Binance)\n"
        message += f"🔗 https://www.binance.com/en/trade/{symbol}\n\n"
        message += f"💰 Last Price: ${last_price}\n"
        message += f"📈 24h Change: {price_change_percent} (${price_change})\n"
        message += f"📊 24h High: ${high_24h}   📉 24h Low: ${low_24h}\n"
        message += f"💧 24h Volume: {volume} {symbol.replace('USDT', '')}\n"
        message += f"💵 Quote Volume: ${quote_volume}\n"
        message += f"🔄 Trade Count: {count}"
        
        print('Formatted message:')
        print(message)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        print('Message sent to Telegram!')
        
    else:
        error_msg = f"Failed to fetch data for {symbol}"
        print(error_msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_msg)

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("binance", binance_command))
    app.add_handler(CommandHandler("symbol", symbol_command))
    print("Bot3 is running. Use /binance to get random symbol data or /symbol BTCUSDT for specific symbol.")
    app.run_polling()
