import csv
import os
from datetime import datetime


class TradeLogger:
    def __init__(self, filename="trades.csv"):
        self.filename = filename
        self.headers = [
            "cycle_id",
            "timestamp",
            "symbol",
            "duration_seconds",
            "usdt_before",
            "usdt_after",
            "btc_before",
            "btc_after",
            "buy_order_id",
            "sell_order_id",
            "buy_type",
            "sell_type",
            "buy_price",
            "sell_price",
            "quantity",
            "buy_quote_qty",
            "sell_quote_qty",
            "profit_usdt",
            "status",
            "notes"
        ]
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def log_trade(
        self,
        cycle_id,
        symbol,
        duration_seconds,
        usdt_before,
        usdt_after,
        btc_before,
        btc_after,
        buy_order_id,
        sell_order_id,
        buy_type,
        sell_type,
        buy_price,
        sell_price,
        quantity,
        buy_quote_qty,
        sell_quote_qty,
        profit_usdt,
        status,
        notes=""
    ):
        with open(self.filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                cycle_id,
                datetime.now().isoformat(sep=" ", timespec="seconds"),
                symbol,
                f"{duration_seconds:.2f}" if duration_seconds is not None else "",
                f"{usdt_before:.8f}" if usdt_before is not None else "",
                f"{usdt_after:.8f}" if usdt_after is not None else "",
                f"{btc_before:.8f}" if btc_before is not None else "",
                f"{btc_after:.8f}" if btc_after is not None else "",
                buy_order_id,
                sell_order_id,
                buy_type,
                sell_type,
                f"{buy_price:.8f}" if buy_price is not None else "",
                f"{sell_price:.8f}" if sell_price is not None else "",
                f"{quantity:.8f}" if quantity is not None else "",
                f"{buy_quote_qty:.8f}" if buy_quote_qty is not None else "",
                f"{sell_quote_qty:.8f}" if sell_quote_qty is not None else "",
                f"{profit_usdt:.8f}" if profit_usdt is not None else "",
                status,
                notes
            ])