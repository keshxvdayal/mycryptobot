# Crypto Telegram Bots

This project consists of three separate Telegram bots that fetch cryptocurrency data from different exchanges:

- **`bot.py`**: Connects to the Delta Exchange API to fetch ticker information.
- **`bot2.py`**: Connects to the CoinSwitch API and provides data on various currency pairs.
- **`bot3.py`**: Connects to the Binance API to get ticker data for all symbols or a specific symbol.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**
    Create a `.env` file in the root of the project and add the following environment variables with your API keys and tokens:

    ```env
    # Telegram
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    CHAT_ID="YOUR_TELEGRAM_CHAT_ID"

    # Delta Exchange (bot.py)
    DELTA_API_KEY="YOUR_DELTA_API_KEY"
    DELTA_API_SECRET="YOUR_DELTA_API_SECRET"

    # CoinSwitch (bot2.py)
    COINSWITCH_API_KEY="YOUR_COINSWITCH_API_KEY"
    COINSWITCH_SECRET_KEY="YOUR_COINSWITCH_SECRET_KEY"

    # Binance (bot3.py)
    BINANCE_API_KEY="YOUR_BINANCE_API_KEY"
    BINANCE_API_SECRET="YOUR_BINANCE_API_SECRET"
    ```

## Running the Bots

You can run each bot individually from your terminal:

-   **Delta Exchange Bot:**
    ```bash
    python bot.py
    ```
    -   **/news**: Fetches the latest ticker information.

-   **CoinSwitch Bot:**
    ```bash
    python bot2.py
    ```
    -   **/fetch**: Fetches and stores data from CoinSwitch.
    -   **/test2**: Displays data for a random currency from the stored file.

-   **Binance Bot:**
    ```bash
    python bot3.py
    ```
    -   **/binance**: Fetches data for a random symbol from Binance.
    -   **/symbol <SYMBOL>**: Fetches data for a specific symbol (e.g., `/symbol BTCUSDT`). 