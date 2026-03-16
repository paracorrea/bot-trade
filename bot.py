import time
from trader import BinanceTrader
from config import SYMBOL, CAPITAL_PER_TRADE, SELL_TARGET


def wait_for_order_fill(trader, order_id, timeout_seconds=30):
    for i in range(timeout_seconds):
        status = trader.get_order(order_id)
        print(f"[{i+1:02d}s] Status: {status['status']}")
        if status["status"] == "FILLED":
            return status
        time.sleep(1)
    return None


def main():
    trader = BinanceTrader()

    current_price = trader.get_price()
    quantity = trader.normalize_quantity(CAPITAL_PER_TRADE / current_price)

    usdt_balance = trader.get_asset_balance("USDT")
    btc_balance = trader.get_asset_balance("BTC")

    print("=== STATUS DO BOT ===")
    print(f"Par: {SYMBOL}")
    print(f"Preço atual: {current_price:.2f}")
    print(f"Quantidade para MARKET BUY: {quantity:.8f}")
    print()
    print("=== SALDOS ANTES ===")
    print(f"USDT: {usdt_balance:.8f}")
    print(f"BTC : {btc_balance:.8f}")

    print("\nEnviando MARKET BUY no TESTNET...")
    buy_order = trader.create_market_buy_order(quantity)

    buy_order_id = buy_order["orderId"]
    print(f"✅ BUY enviada. Order ID: {buy_order_id}")
    print(f"Status inicial BUY: {buy_order['status']}")

    print("\nAguardando execução da BUY...\n")
    filled_buy = wait_for_order_fill(trader, buy_order_id, timeout_seconds=10)

    if not filled_buy:
        print("❌ BUY não executou no prazo.")
        return

    print("✅ BUY executada!")

    executed_qty = float(filled_buy["executedQty"])
    cummulative_quote_qty = float(filled_buy["cummulativeQuoteQty"])
    avg_buy_price = cummulative_quote_qty / executed_qty

    sell_price = trader.normalize_price(avg_buy_price * (1 + SELL_TARGET / 100))

    print(f"Preço médio da BUY: {avg_buy_price:.2f}")
    print(f"Preço alvo da SELL: {sell_price:.2f}")

    print("\nEnviando LIMIT SELL no TESTNET...")
    sell_order = trader.create_limit_sell_order(executed_qty, sell_price)

    sell_order_id = sell_order["orderId"]
    print(f"✅ SELL enviada. Order ID: {sell_order_id}")
    print(f"Status inicial SELL: {sell_order['status']}")

    print("\nAguardando execução da SELL...\n")
    
    filled_sell = wait_for_order_fill(trader, sell_order_id, timeout_seconds=30)

    if not filled_sell:
        print("⚠️ SELL não executou no prazo. Cancelando ordem LIMIT SELL...")
        cancel_result = trader.cancel_order(sell_order_id)
        print(f"SELL cancelada. Status final: {cancel_result['status']}")

        print("\nEnviando MARKET SELL para encerrar o ciclo...")
        market_sell = trader.create_market_sell_order(executed_qty)
        market_sell_id = market_sell["orderId"]
        print(f"✅ MARKET SELL enviada. Order ID: {market_sell_id}")

        filled_market_sell = wait_for_order_fill(trader, market_sell_id, timeout_seconds=10)

        if not filled_market_sell:
            print("❌ MARKET SELL não executou no prazo.")
            return

        print("✅ MARKET SELL executada!")
        final_usdt = trader.get_asset_balance("USDT")
        final_btc = trader.get_asset_balance("BTC")

        sell_quote_qty = float(filled_market_sell["cummulativeQuoteQty"])
        real_profit = sell_quote_qty - cummulative_quote_qty

        print("\n=== SALDOS DEPOIS ===")
        print(f"USDT: {final_usdt:.8f}")
        print(f"BTC : {final_btc:.8f}")
        print(f"\n💰 Resultado real do ciclo: {real_profit:.8f} USDT")
        return

    print("✅ SELL executada!")

    final_usdt = trader.get_asset_balance("USDT")
    final_btc = trader.get_asset_balance("BTC")

    print("\n=== SALDOS DEPOIS ===")
    print(f"USDT: {final_usdt:.8f}")
    print(f"BTC : {final_btc:.8f}")

    estimated_profit = (sell_price - avg_buy_price) * executed_qty
    print(f"\n💰 Lucro estimado do ciclo: {estimated_profit:.8f} USDT")


if __name__ == "__main__":
    main()