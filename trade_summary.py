import csv
from pathlib import Path


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_field(row, field_name, default=""):
    return row.get(field_name, default)


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

    total_trades = len(rows)
    total_profit = sum(to_float(get_field(row, "profit_usdt")) for row in rows)
    avg_profit = total_profit / total_trades if total_trades else 0.0

    closed_with_limit = [
        r for r in rows if get_field(r, "status") == "CLOSED_WITH_LIMIT_SELL"
    ]
    closed_with_market = [
        r for r in rows if get_field(r, "status") == "CLOSED_WITH_MARKET_SELL"
    ]

    best_trade = max(rows, key=lambda r: to_float(get_field(r, "profit_usdt")))
    worst_trade = min(rows, key=lambda r: to_float(get_field(r, "profit_usdt")))

    durations = [to_float(get_field(r, "duration_seconds")) for r in rows]
    valid_durations = [d for d in durations if d > 0]
    avg_duration = (
        sum(valid_durations) / len(valid_durations) if valid_durations else 0.0
    )

    print("=== RESUMO DOS TRADES ===")
    print(f"Total de trades               : {total_trades}")
    print(f"Lucro total (USDT)            : {total_profit:.8f}")
    print(f"Lucro médio por trade (USDT)  : {avg_profit:.8f}")
    print(f"Duração média (segundos)      : {avg_duration:.2f}")
    print(f"Fechados com LIMIT SELL       : {len(closed_with_limit)}")
    print(f"Fechados com MARKET SELL      : {len(closed_with_market)}")
    print()

    print("=== MELHOR TRADE ===")
    print(f"Cycle ID   : {get_field(best_trade, 'cycle_id', 'N/A')}")
    print(f"Profit USDT: {to_float(get_field(best_trade, 'profit_usdt')):.8f}")
    print(f"Status     : {get_field(best_trade, 'status', 'N/A')}")
    print()

    print("=== PIOR TRADE ===")
    print(f"Cycle ID   : {get_field(worst_trade, 'cycle_id', 'N/A')}")
    print(f"Profit USDT: {to_float(get_field(worst_trade, 'profit_usdt')):.8f}")
    print(f"Status     : {get_field(worst_trade, 'status', 'N/A')}")


if __name__ == "__main__":
    main()