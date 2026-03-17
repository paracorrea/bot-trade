import csv
from pathlib import Path
import matplotlib.pyplot as plt


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def main():
    csv_file = Path("trades.csv")

    if not csv_file.exists():
        print("Arquivo trades.csv não encontrado.")
        return

    with open(csv_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        print("Nenhum trade registrado ainda.")
        return

    trade_numbers = []
    profits = []
    cumulative_profits = []

    total = 0.0

    for i, row in enumerate(rows, start=1):
        profit = to_float(row.get("profit_usdt"))

        trade_numbers.append(i)
        profits.append(profit)

        total += profit
        cumulative_profits.append(total)

    plt.figure(figsize=(12, 6))
    plt.bar(trade_numbers, profits)
    plt.title("Lucro por trade")
    plt.xlabel("Trade")
    plt.ylabel("Lucro (USDT)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(trade_numbers, cumulative_profits, marker="o")
    plt.title("Lucro acumulado")
    plt.xlabel("Trade")
    plt.ylabel("Lucro acumulado (USDT)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()