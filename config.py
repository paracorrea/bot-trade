from dotenv import dotenv_values

env = dotenv_values(".env")

API_KEY = env.get("BINANCE_API_KEY")
API_SECRET = env.get("BINANCE_API_SECRET")

SYMBOL = env.get("SYMBOL", "BTCUSDT")
CAPITAL_PER_TRADE = float(env.get("CAPITAL_PER_TRADE", "50"))
BUY_DISCOUNT = float(env.get("BUY_DISCOUNT", "0.2"))
SELL_TARGET = float(env.get("SELL_TARGET", "0.6"))