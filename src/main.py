import pandas as pd
import pandas_ta as ta
from binance.client import Client
from binance.exceptions import BinanceAPIException
from decouple import config
from discord_webhook import DiscordWebhook
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout, ConnectionError
import numpy as np
import os
import time

BLACK_LIST_SYMBOL = set()

def send_alert(symbol, price, ifr_value, ifr_trend, price_trend, ifr, interval, keltner_lower, keltner_upper):
    """
    Envia um alerta para o webhook do Discord se o IFR for menor que um limite específico.
    """
    if ifr_value < ifr:  # Ajuste o limite de acordo com suas necessidades
        URL_WEBHOOK = config("URL_WEBHOOK")
        content = (f"Moeda: {symbol}\nPreço: {price}\nIFR: {ifr_value}\nTendência IFR: {ifr_trend}\n"
                   f"Tendência Preço: {price_trend}\nIntervalo: {interval}\n"
                   f"Preço Alvo Compra: ${keltner_lower:.3f}\nPreço Alvo Venda: ${keltner_upper:.3f}\n")
        webhook = DiscordWebhook(url=URL_WEBHOOK, content=f"```\n{content}\n```")
        webhook.execute()

def check_ifr(symbol, interval):
    """
    Verifica se o IFR está abaixo de 20 para um determinado símbolo e intervalo.
    """
    try:
        client = Client(api_key=os.environ["API_KEY_BINANCE"], api_secret=os.environ["API_SECRET_BINANCE"])
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=300)

        df = pd.DataFrame(klines, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 
                                           'Close_time', 'Quote_asset_volume', 'Number_of_trades', 
                                           'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 
                                           'Ignore'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Close'] = df['Close'].astype(float)  
        
        # Calcular IFR
        length = 14
        df.ta.rsi(close='Close', length=length, append=True)
        
        
        # Verificar tendência do IFR
        if df['RSI_14'].values[-1] > df['RSI_14'].shift(1).values[-1]:
            ifr_trend = "Ascendente"
        else:
            ifr_trend = "Descendente"

        # Calcular Canal de Keltner
        ema_length = 20
        atr_length = 10

        df['EMA'] = ta.ema(close= df['Close'], length=ema_length)
        df.fillna(0, inplace=True)

        df['Close'] = df['Close'].astype('float64')
        df['High'] = df['High'].astype('float64')
        df['Low'] = df['Low'].astype('float64')

        df['ATR'] = ta.atr(high= df['High'], low= df['Low'], close= df['Close'], length=atr_length)
        df['Keltner_Lower'] = df['EMA'] - df['ATR']
        df['Keltner_Upper'] = df['EMA'] + df['ATR']
        
        keltner_lower = df['Keltner_Lower'].values[-1]
        keltner_upper = df['Keltner_Upper'].values[-1]

        print(f"Moeda: {symbol}")
        print(f"{symbol} RSI_14: {df['RSI_14'].values[-1]}")

        current_price = df['Close'].values.flatten()[-1]
        target_buy = keltner_lower * 0.98
        target_sell = keltner_upper * 1.01

        # Log dos preços e canais de Keltner
        print(f"Preço: ${current_price:.3f}")
        print(f"Preço Alvo Compra: ${target_buy:.3f}")
        print(f"Preço Alvo Venda: ${target_sell:.3f}")
        if current_price < keltner_lower:
            print(f"Compra {symbol} -> ${current_price}")
        elif current_price > keltner_upper:
            print(f"Venda {symbol} -> ${current_price}")
        else:
            print(f"Espere {symbol}")

        print(f"Canal Inferior de Keltner: {keltner_lower:.3f}, Canal Superior de Keltner: {keltner_upper:.3f}\n")
        return df['RSI_14'].values[-1], ifr_trend, keltner_lower, keltner_upper

    except (BinanceAPIException, ReadTimeoutError, ReadTimeout) as e:
        print(f"Erro ao obter dados para {symbol}: {e}")
        add_black_list(symbol)
        return False, None, None, None
    
    except (KeyError) as e:
        print(f"Erro ao obter dados para {symbol}: {e}")
        return False, None, None, None

def check_price_trend(symbol, interval):
    """
    Verifica a tendência do preço para um determinado símbolo e intervalo.
    """
    try:
        client = Client(api_key=os.environ["API_KEY_BINANCE"], api_secret=os.environ["API_SECRET_BINANCE"])
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=300)

        df = pd.DataFrame(klines, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 
                                           'Close_time', 'Quote_asset_volume', 'Number_of_trades', 
                                           'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 
                                           'Ignore'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Close'] = df['Close'].astype(float)  

        # Verificar tendência do preço
        if df['Close'].values[-1] > df['Close'].shift(1).values[-1]:
            price_trend = "Ascendente"
        else:
            price_trend = "Descendente"

        return price_trend

    except (BinanceAPIException, ReadTimeoutError, ReadTimeout) as e:
        print(f"Erro ao obter dados para {symbol}: {e}")
        add_black_list(symbol)
        return None

def get_all_symbols():
    """
    Obtém todos os símbolos disponíveis na Binance.
    """
    client = Client(api_key=os.environ["API_KEY_BINANCE"], api_secret=os.environ["API_SECRET_BINANCE"])
    exchange_info = client.get_exchange_info()
    symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if "USDT" in symbol['symbol']]
    return symbols

def add_black_list(symbol: str):
    """
    Adiciona simbolo black list
    """
    BLACK_LIST_SYMBOL.add(symbol)

def remove_invalid_symbols(symbols: list):
    """
    """ 
    symbols_set = set(symbols)
    return [symbol for symbol in symbols_set if symbol not in BLACK_LIST_SYMBOL]

def main():
    """
    Função principal que executa o script.
    """
    interval_1min = '1m'
    interval_15min = '15m'
    interval_1h = '2h'
    interval_4h = '4h'
    symbols = sorted(get_all_symbols())

    symbols = [
        "BTCUSDT",
        "ETHUSDT",
        "RNDRUSDT",
        "NEARUSDT",
        "FETUSDT",
        "LINKUSDT",
        "BNBUSDT",
        "SOLUSDT",
        "PEPEUSDT"
    ]

    while True:
        for symbol in symbols:
            ifr_value, ifr_trend, keltner_lower, keltner_upper = check_ifr(symbol, interval_1h)
            if ifr_value is not None and ifr_value != False:
                price_trend = check_price_trend(symbol, interval_1h)
                if price_trend is not None:
                    # Obter o preço atual
                    client = Client(api_key=os.environ["API_KEY_BINANCE"], api_secret=os.environ["API_SECRET_BINANCE"])
                    try:
                        ticker = client.get_ticker(symbol=symbol)
                        current_price = float(ticker['lastPrice'])
                        # Enviar alerta
                        send_alert(symbol, current_price, ifr_value, ifr_trend, price_trend, 33, interval_15min, keltner_lower, keltner_upper)
                    except (BinanceAPIException, ReadTimeoutError, ConnectionError) as e:
                        print(f"Erro ao obter preço para {symbol}: {e}")

        # Removendo symbols invalidos
        symbols = remove_invalid_symbols(symbols=symbols)
        time.sleep(2)

if __name__ == "__main__":
    main()