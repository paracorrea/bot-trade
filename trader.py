from math import floor
from binance.client import Client
from config import API_KEY, API_SECRET, SYMBOL, CAPITAL_PER_TRADE, BUY_DISCOUNT, SELL_TARGET


class BinanceTrader:
    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)
        self.client.API_URL = "https://testnet.binance.vision/api"

    def get_price(self):
        price = self.client.get_symbol_ticker(symbol=SYMBOL)
        return float(price["price"])

    def get_account(self):
        return self.client.get_account()

    def get_asset_balance(self, asset):
        balance = self.client.get_asset_balance(asset=asset)
        if balance:
            return float(balance["free"])
        return 0.0

    def calculate_buy_price(self, current_price):
        return current_price * (1 - BUY_DISCOUNT / 100)

    def calculate_sell_price(self, buy_price):
        return buy_price * (1 + SELL_TARGET / 100)

    def calculate_quantity(self, buy_price):
        return CAPITAL_PER_TRADE / buy_price

    def get_symbol_info(self):
        return self.client.get_symbol_info(SYMBOL)

    def get_symbol_filters(self):
        info = self.get_symbol_info()
        return {f["filterType"]: f for f in info["filters"]}

    def normalize_price(self, price):
        filters = self.get_symbol_filters()
        tick_size = float(filters["PRICE_FILTER"]["tickSize"])
        return floor(price / tick_size) * tick_size

    def normalize_quantity(self, quantity):
        filters = self.get_symbol_filters()
        step_size = float(filters["LOT_SIZE"]["stepSize"])
        return floor(quantity / step_size) * step_size

    def calculate_notional(self, price, quantity):
        return price * quantity

    def create_test_order(self, side, order_type, quantity, price=None, time_in_force="GTC"):
        params = {
            "symbol": SYMBOL,
            "side": side,
            "type": order_type,
            "quantity": f"{quantity:.8f}"
        }

        if price is not None:
            params["price"] = f"{price:.2f}"
        if time_in_force:
            params["timeInForce"] = time_in_force

        return self.client.create_test_order(**params)

    def create_limit_buy_test_order(self, quantity, price):
        return self.create_test_order(
            side="BUY",
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force="GTC"
        )

    def create_limit_buy_order(self, quantity, price):
        return self.client.create_order(
            symbol=SYMBOL,
            side="BUY",
            type="LIMIT",
            timeInForce="GTC",
            quantity=f"{quantity:.8f}",
            price=f"{price:.2f}"
        )

    def get_order(self, order_id):
        return self.client.get_order(symbol=SYMBOL, orderId=order_id)
    
    def create_limit_sell_order(self, quantity, price):
        return self.client.create_order(
            symbol=SYMBOL,
            side="SELL",
            type="LIMIT",
            timeInForce="GTC",
            quantity=f"{quantity:.8f}",
            price=f"{price:.2f}"
        )

    def cancel_order(self, order_id):
        return self.client.cancel_order(symbol=SYMBOL, orderId=order_id)
    
    def create_market_buy_order(self, quantity):
        return self.client.create_order(
            symbol=SYMBOL,
            side="BUY",
            type="MARKET",
            quantity=f"{quantity:.8f}"
        )
    
    def create_market_sell_order(self, quantity):
        return self.client.create_order(
            symbol=SYMBOL,
            side="SELL",
            type="MARKET",
            quantity=f"{quantity:.8f}"
        )
    