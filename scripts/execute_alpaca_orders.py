from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.alpaca_trade_adapter import AlpacaTradeAdapter
from core.order_logger import append_order_event
from core.portfolio_state import calc_target_qty, positions_to_map


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _load_snapshot_quotes() -> dict:
    p = ROOT / "data" / "market_snapshot.alpaca.stock.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get("quotes", {})


def main() -> None:
    intents = json.loads((ROOT / "outputs" / "trade_intents.json").read_text(encoding="utf-8"))
    strategy = _load_yaml(ROOT / "config" / "strategy_stock.yaml")
    min_order_notional = float(strategy.get("execution", {}).get("min_order_notional", 500))

    adapter = AlpacaTradeAdapter()
    log_path = ROOT / "state" / "live_orders.jsonl"
    quotes = _load_snapshot_quotes()
    results = []

    try:
        account = adapter.get_account()
        equity = float(account["equity"])
    except Exception:
        account = {"equity": 100000.0, "cash": 100000.0, "status": "dry_run"}
        equity = 100000.0

    try:
        positions = adapter.get_positions()
    except Exception:
        positions = []
    pos_map = positions_to_map(positions)

    for intent in intents.get("trade_intents", []):
        symbol = intent.get("symbol")
        action = intent.get("action")
        if action not in {"buy", "sell"}:
            continue

        price = float(quotes.get(symbol, {}).get("price", 0.0) or 0.0)
        target_weight = float(intent.get("target_weight") or 0.0)
        target_qty = calc_target_qty(equity=equity, target_weight=target_weight, price=price)
        current_qty = int(pos_map.get(symbol, 0))
        delta = target_qty - current_qty

        if delta == 0:
            continue
        side = "buy" if delta > 0 else "sell"
        qty = abs(int(delta))
        if qty <= 0:
            continue

        est_notional = qty * price
        if est_notional < min_order_notional:
            continue

        try:
            order = adapter.submit_market_order(symbol=symbol, qty=qty, side=side)
            status = "submitted"
        except Exception as exc:
            order = {
                "id": "dry-run",
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "status": f"dry_run:{type(exc).__name__}",
                "filled_avg_price": 0.0,
                "submitted_at": intents.get("data_ts"),
            }
            status = "dry_run"

        event = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "order_type": "market",
            "status": status,
            "filled_avg_price": order.get("filled_avg_price", 0.0),
            "reason": intent.get("reason", ""),
            "signal_score": intent.get("signal_score", 0),
        }
        append_order_event(log_path, event)
        results.append(order)

    (ROOT / "state" / "live_positions.json").write_text(
        json.dumps(
            {
                "data_ts": intents.get("data_ts"),
                "account": account,
                "positions": positions,
                "orders_submitted": len(results),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"orders": len(results), "account": account}, ensure_ascii=False))


if __name__ == "__main__":
    main()
