# Alert-Price-Cript-Binance
RSI and Keltner Channel Crypto Trading Bot Alert
# RSI and Keltner Channel Crypto Trading Bot

## Description

This project implements a bot alert for trading that monitors various cryptocurrency pairs on Binance and sends alerts to a Discord webhook when certain trading conditions are met. The bot uses the Relative Strength Index (RSI) and the Keltner Channel to identify buy and sell opportunities.

## Features

- **Cryptocurrency Monitoring:** Monitors various cryptocurrency pairs at defined time intervals.
- **Technical Indicator Calculation:** Uses RSI and Keltner Channel to determine trading conditions.
- **Trading Alerts:** Sends alerts to a Discord webhook when trading conditions are met.
- **Error Handling:** Manages exceptions and adds invalid symbols to a blacklist.

## Requirements

- Python 3.8+
- `pandas` library
- `pandas_ta` library
- `binance` library
- `decouple` library
- `discord_webhook` library
- `urllib3` library
- `requests` library

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/GabrielFonsecaNunes/Alert-Price-Cript-Binance.git
   cd rsi-keltner-bot
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your Binance API keys and Discord webhook URL in a `.env` file:
   ```
   API_KEY_BINANCE=your_api_key
   API_SECRET_BINANCE=your_api_secret
   URL_WEBHOOK=your_webhook_url
   ```

## Usage

Run the main script:
```bash
python main.py
```

## Code Structure

- `main.py`: Main script that runs the bot.
- `check_ifr(symbol, interval)`: Checks the RSI and Keltner Channel for a specific symbol and interval.
- `send_alert(symbol, price, ifr_value, ifr_trend, price_trend, ifr, interval, keltner_lower, keltner_upper)`: Sends an alert to the Discord webhook.
- `check_price_trend(symbol, interval)`: Checks the price trend for a specific symbol and interval.
- `get_all_symbols()`: Retrieves all available symbols on Binance.
- `add_black_list(symbol)`: Adds a symbol to the blacklist.
- `remove_invalid_symbols(symbols)`: Removes invalid symbols from the symbol list.

## Contributions

Contributions are welcome! Feel free to open issues and pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
