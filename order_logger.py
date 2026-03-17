import csv
import os
from datetime import datetime


class OrderLogger:
    def __init__(self, filename="orders.csv"):
        self.filename = filename
        self.headers = [
            "timestamp",
            "cycle_id",
            "order_id",
            "symbol",
            "side",
            "type",
            "price",
            "quantity",
            "status",
            "notes"
        ]
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def log_order(
        self,
        cycle_id,
        order_id,
        symbol,
        side,
        order_type,
        price,
        quantity,
        status,
        notes=""
    ):
        with open(self.filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().isoformat(sep=" ", timespec="seconds"),
                cycle_id,
                order_id,
                symbol,
                side,
                order_type,
                f"{price:.8f}" if price is not None else "",
                f"{quantity:.8f}" if quantity is not None else "",
                status,
                notes
            ])