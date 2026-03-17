import time
from datetime import datetime

from trader import BinanceTrader
from config import SELL_TIMEOUT, STOP_LOSS, SYMBOL, CAPITAL_PER_TRADE, SELL_TARGET
from trade_logger import TradeLogger
from order_logger import OrderLogger
from state_manager import StateManager


MAX_CYCLES = 5
SLEEP_BETWEEN_CYCLES = 15


def wait_for_order_fill(trader, order_id, timeout_seconds=30):
    for i in range(timeout_seconds):
        status = trader.get_order(order_id)
        print(f"[{i+1:02d}s] Status: {status['status']}")
        if status["status"] == "FILLED":
            return status
        time.sleep(1)
    return None


def monitor_sell_with_stop(trader, sell_order_id, stop_loss_price, timeout_seconds=120):
    for i in range(timeout_seconds):
        sell_status = trader.get_order(sell_order_id)
        current_price = trader.get_price()

        print(
            f"[{i+1:03d}s] SELL status={sell_status['status']} | "
            f"preço atual={current_price:.2f} | stop={stop_loss_price:.2f}"
        )

        if sell_status["status"] == "FILLED":
            return {"result": "TAKE_PROFIT_FILLED", "order": sell_status}

        if current_price <= stop_loss_price:
            return {"result": "STOP_LOSS_TRIGGERED", "order": sell_status}

        time.sleep(1)

    return {"result": "TIMEOUT", "order": trader.get_order(sell_order_id)}


def run_cycle():
    trader = BinanceTrader()
    trade_logger = TradeLogger()
    order_logger = OrderLogger()
    state_manager = StateManager()

    current_state = state_manager.load_state()
    if current_state.get("has_open_position"):
        print("⚠️ Já existe posição aberta. Nenhum novo ciclo será iniciado.")
        print(current_state)
        return

    cycle_id = datetime.now().strftime("%Y%m%d%H%M%S")
    start_time = time.time()

    print("\n==============================")
    print(f"Iniciando ciclo {cycle_id}")
    print("==============================")

    state_manager.save_state({
        "symbol": SYMBOL,
        "cycle_id": cycle_id,
        "has_open_position": False,
        "buy_order_id": "",
        "sell_order_id": "",
        "last_status": "STARTED",
        "notes": "Ciclo iniciado"
    })

    current_price = trader.get_price()
    quantity = trader.normalize_quantity(CAPITAL_PER_TRADE / current_price)

    usdt_before = trader.get_asset_balance("USDT")
    btc_before = trader.get_asset_balance("BTC")

    print("=== STATUS DO BOT ===")
    print(f"Par: {SYMBOL}")
    print(f"Preço atual: {current_price:.2f}")
    print(f"Quantidade para MARKET BUY: {quantity:.8f}")
    print()
    print("=== SALDOS ANTES ===")
    print(f"USDT: {usdt_before:.8f}")
    print(f"BTC : {btc_before:.8f}")

    print("\nEnviando MARKET BUY no TESTNET...")
    buy_order = trader.create_market_buy_order(quantity)
    buy_order_id = buy_order["orderId"]

    order_logger.log_order(
        cycle_id=cycle_id,
        order_id=buy_order_id,
        symbol=SYMBOL,
        side="BUY",
        order_type="MARKET",
        price=current_price,
        quantity=quantity,
        status=buy_order["status"],
        notes="Entrada do ciclo"
    )

    state_manager.save_state({
        "symbol": SYMBOL,
        "cycle_id": cycle_id,
        "has_open_position": True,
        "buy_order_id": str(buy_order_id),
        "sell_order_id": "",
        "last_status": buy_order["status"],
        "notes": "BUY enviada"
    })

    print(f"✅ BUY enviada. Order ID: {buy_order_id}")
    print(f"Status inicial BUY: {buy_order['status']}")

    print("\nAguardando execução da BUY...\n")
    filled_buy = wait_for_order_fill(trader, buy_order_id, timeout_seconds=10)

    if not filled_buy:
        duration = time.time() - start_time

        trade_logger.log_trade(
            cycle_id=cycle_id,
            symbol=SYMBOL,
            duration_seconds=duration,
            usdt_before=usdt_before,
            usdt_after=trader.get_asset_balance("USDT"),
            btc_before=btc_before,
            btc_after=trader.get_asset_balance("BTC"),
            buy_order_id=buy_order_id,
            sell_order_id="",
            buy_type="MARKET",
            sell_type="",
            buy_price=0,
            sell_price=0,
            quantity=quantity,
            buy_quote_qty=0,
            sell_quote_qty=0,
            profit_usdt=0,
            status="BUY_TIMEOUT",
            notes="Compra não executou no prazo"
        )

        state_manager.save_state({
            "symbol": SYMBOL,
            "cycle_id": cycle_id,
            "has_open_position": False,
            "buy_order_id": str(buy_order_id),
            "sell_order_id": "",
            "last_status": "BUY_TIMEOUT",
            "notes": "Compra não executou no prazo"
        })

        print("❌ BUY não executou no prazo.")
        return

    print("✅ BUY executada!")

    executed_qty = float(filled_buy["executedQty"])
    buy_quote_qty = float(filled_buy["cummulativeQuoteQty"])
    avg_buy_price = buy_quote_qty / executed_qty

    sell_price = trader.normalize_price(avg_buy_price * (1 + SELL_TARGET / 100))
    stop_loss_price = trader.normalize_price(avg_buy_price * (1 - STOP_LOSS / 100))

    print(f"Preço médio da BUY : {avg_buy_price:.2f}")
    print(f"Take profit        : {sell_price:.2f}")
    print(f"Stop loss          : {stop_loss_price:.2f}")

    print("\nEnviando LIMIT SELL no TESTNET...")
    sell_order = trader.create_limit_sell_order(executed_qty, sell_price)
    sell_order_id = sell_order["orderId"]

    order_logger.log_order(
        cycle_id=cycle_id,
        order_id=sell_order_id,
        symbol=SYMBOL,
        side="SELL",
        order_type="LIMIT",
        price=sell_price,
        quantity=executed_qty,
        status=sell_order["status"],
        notes="Take profit enviado"
    )

    state_manager.save_state({
        "symbol": SYMBOL,
        "cycle_id": cycle_id,
        "has_open_position": True,
        "buy_order_id": str(buy_order_id),
        "sell_order_id": str(sell_order_id),
        "last_status": sell_order["status"],
        "notes": "SELL LIMIT enviada"
    })

    print(f"✅ SELL enviada. Order ID: {sell_order_id}")
    print(f"Status inicial SELL: {sell_order['status']}")
    print("\nMonitorando take profit / stop loss...\n")

    monitor_result = monitor_sell_with_stop(
        trader=trader,
        sell_order_id=sell_order_id,
        stop_loss_price=stop_loss_price,
        timeout_seconds=SELL_TIMEOUT
    )

    if monitor_result["result"] == "TAKE_PROFIT_FILLED":
        filled_sell = monitor_result["order"]

        sell_quote_qty = float(filled_sell["cummulativeQuoteQty"])
        avg_sell_price = sell_quote_qty / executed_qty
        profit = sell_quote_qty - buy_quote_qty

        usdt_after = trader.get_asset_balance("USDT")
        btc_after = trader.get_asset_balance("BTC")
        duration = time.time() - start_time

        print("✅ TAKE PROFIT executado!")
        print("\n=== SALDOS DEPOIS ===")
        print(f"USDT: {usdt_after:.8f}")
        print(f"BTC : {btc_after:.8f}")
        print(f"\n💰 Resultado real do ciclo: {profit:.8f} USDT")

        trade_logger.log_trade(
            cycle_id=cycle_id,
            symbol=SYMBOL,
            duration_seconds=duration,
            usdt_before=usdt_before,
            usdt_after=usdt_after,
            btc_before=btc_before,
            btc_after=btc_after,
            buy_order_id=buy_order_id,
            sell_order_id=sell_order_id,
            buy_type="MARKET",
            sell_type="LIMIT",
            buy_price=avg_buy_price,
            sell_price=avg_sell_price,
            quantity=executed_qty,
            buy_quote_qty=buy_quote_qty,
            sell_quote_qty=sell_quote_qty,
            profit_usdt=profit,
            status="CLOSED_WITH_LIMIT_SELL",
            notes="Ciclo completo com venda no alvo"
        )

        state_manager.save_state({
            "symbol": SYMBOL,
            "cycle_id": cycle_id,
            "has_open_position": False,
            "buy_order_id": str(buy_order_id),
            "sell_order_id": str(sell_order_id),
            "last_status": "CLOSED_WITH_LIMIT_SELL",
            "notes": "Ciclo fechado com limit sell"
        })
        return

    elif monitor_result["result"] == "STOP_LOSS_TRIGGERED":
        print("⚠️ Stop loss atingido. Cancelando LIMIT SELL...")

        cancel_result = trader.cancel_order(sell_order_id)
        order_logger.log_order(
            cycle_id=cycle_id,
            order_id=sell_order_id,
            symbol=SYMBOL,
            side="SELL",
            order_type="LIMIT",
            price=sell_price,
            quantity=executed_qty,
            status=cancel_result["status"],
            notes="Take profit cancelado por stop loss"
        )

        print(f"SELL cancelada. Status final: {cancel_result['status']}")

        print("\nEnviando MARKET SELL por stop loss...")
        market_sell = trader.create_market_sell_order(executed_qty)
        market_sell_id = market_sell["orderId"]

        order_logger.log_order(
            cycle_id=cycle_id,
            order_id=market_sell_id,
            symbol=SYMBOL,
            side="SELL",
            order_type="MARKET",
            price=None,
            quantity=executed_qty,
            status=market_sell["status"],
            notes="Saída por stop loss"
        )

        filled_market_sell = wait_for_order_fill(trader, market_sell_id, timeout_seconds=10)

        if not filled_market_sell:
            duration = time.time() - start_time

            trade_logger.log_trade(
                cycle_id=cycle_id,
                symbol=SYMBOL,
                duration_seconds=duration,
                usdt_before=usdt_before,
                usdt_after=trader.get_asset_balance("USDT"),
                btc_before=btc_before,
                btc_after=trader.get_asset_balance("BTC"),
                buy_order_id=buy_order_id,
                sell_order_id=market_sell_id,
                buy_type="MARKET",
                sell_type="MARKET",
                buy_price=avg_buy_price,
                sell_price=0,
                quantity=executed_qty,
                buy_quote_qty=buy_quote_qty,
                sell_quote_qty=0,
                profit_usdt=0,
                status="STOP_LOSS_TIMEOUT",
                notes="Venda a mercado do stop loss não executou no prazo"
            )

            state_manager.save_state({
                "symbol": SYMBOL,
                "cycle_id": cycle_id,
                "has_open_position": True,
                "buy_order_id": str(buy_order_id),
                "sell_order_id": str(market_sell_id),
                "last_status": "STOP_LOSS_TIMEOUT",
                "notes": "Venda a mercado do stop loss não executou"
            })

            print("❌ MARKET SELL do stop loss não executou no prazo.")
            return

        sell_quote_qty = float(filled_market_sell["cummulativeQuoteQty"])
        avg_sell_price = sell_quote_qty / executed_qty
        real_profit = sell_quote_qty - buy_quote_qty

        usdt_after = trader.get_asset_balance("USDT")
        btc_after = trader.get_asset_balance("BTC")
        duration = time.time() - start_time

        print("✅ STOP LOSS executado!")
        print("\n=== SALDOS DEPOIS ===")
        print(f"USDT: {usdt_after:.8f}")
        print(f"BTC : {btc_after:.8f}")
        print(f"\n💰 Resultado real do ciclo: {real_profit:.8f} USDT")

        trade_logger.log_trade(
            cycle_id=cycle_id,
            symbol=SYMBOL,
            duration_seconds=duration,
            usdt_before=usdt_before,
            usdt_after=usdt_after,
            btc_before=btc_before,
            btc_after=btc_after,
            buy_order_id=buy_order_id,
            sell_order_id=market_sell_id,
            buy_type="MARKET",
            sell_type="MARKET",
            buy_price=avg_buy_price,
            sell_price=avg_sell_price,
            quantity=executed_qty,
            buy_quote_qty=buy_quote_qty,
            sell_quote_qty=sell_quote_qty,
            profit_usdt=real_profit,
            status="CLOSED_WITH_STOP_LOSS",
            notes="Ciclo fechado por stop loss"
        )

        state_manager.save_state({
            "symbol": SYMBOL,
            "cycle_id": cycle_id,
            "has_open_position": False,
            "buy_order_id": str(buy_order_id),
            "sell_order_id": str(market_sell_id),
            "last_status": "CLOSED_WITH_STOP_LOSS",
            "notes": "Ciclo fechado por stop loss"
        })
        return

    else:
        duration = time.time() - start_time
        usdt_after = trader.get_asset_balance("USDT")
        btc_after = trader.get_asset_balance("BTC")

        print("⏳ Timeout operacional. Posição mantida aberta.")
        print("\n=== SALDOS ATUAIS ===")
        print(f"USDT: {usdt_after:.8f}")
        print(f"BTC : {btc_after:.8f}")

        trade_logger.log_trade(
            cycle_id=cycle_id,
            symbol=SYMBOL,
            duration_seconds=duration,
            usdt_before=usdt_before,
            usdt_after=usdt_after,
            btc_before=btc_before,
            btc_after=btc_after,
            buy_order_id=buy_order_id,
            sell_order_id=sell_order_id,
            buy_type="MARKET",
            sell_type="LIMIT",
            buy_price=avg_buy_price,
            sell_price=0,
            quantity=executed_qty,
            buy_quote_qty=buy_quote_qty,
            sell_quote_qty=0,
            profit_usdt=0,
            status="POSITION_HELD",
            notes="Timeout sem alvo nem stop; posição mantida aberta"
        )

        state_manager.save_state({
            "symbol": SYMBOL,
            "cycle_id": cycle_id,
            "has_open_position": True,
            "buy_order_id": str(buy_order_id),
            "sell_order_id": str(sell_order_id),
            "last_status": "POSITION_HELD",
            "notes": "Timeout sem alvo nem stop; posição mantida aberta"
        })
        return


def main():
    print("Bot iniciado em modo loop controlado.")
    print(f"Máximo de ciclos: {MAX_CYCLES}")
    print(f"Intervalo entre ciclos: {SLEEP_BETWEEN_CYCLES}s")
    print("Para parar manualmente: Ctrl + C\n")

    try:
        for i in range(1, MAX_CYCLES + 1):
            print(f"\n########## CICLO {i}/{MAX_CYCLES} ##########")
            run_cycle()

            if i < MAX_CYCLES:
                print(f"\nAguardando {SLEEP_BETWEEN_CYCLES}s para o próximo ciclo...\n")
                time.sleep(SLEEP_BETWEEN_CYCLES)

        print("\nBot finalizado após atingir o número máximo de ciclos.")

    except KeyboardInterrupt:
        print("\n⛔ Bot interrompido manualmente pelo usuário.")


if __name__ == "__main__":
    main()