from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.alpaca_trade_adapter import AlpacaTradeAdapter
from core.order_logger import append_order_event


def main() -> None:
    intents = json.loads((ROOT / "outputs" / "trade_intents.json").read_text(encoding="utf-8"))
    adapter = AlpacaTradeAdapter()
    log_path = ROOT / "state" / "live_orders.jsonl"
    results = []

    try:
        account = adapter.get_account()
        equity = float(account["equity"])
    except Exception:
        account = {"equity": 100000.0, "cash": 100000.0, "status": "dry_run"}
        equity = 100000.0

    for intent in intents.get("trade_intents", []):
        action = intent.get("action")
        if action not in {"buy", "sell"}:
            continue
        symbol = intent["symbol"]
        target_weight = float(intent.get("target_weight") or 0)
        notional = equity * target_weight
        qty = max(int(notional // 100), 1)  # MVP: coarse qty proxy

        try:
            order = adapter.submit_market_order(symbol=symbol, qty=qty, side=action)
            status = "submitted"
        except Exception as exc:
            order = {
                "id": "dry-run",
                "symbol": symbol,
                "qty": qty,
                "side": action,
                "status": f"dry_run:{type(exc).__name__}",
                "filled_avg_price": 0.0,
                "submitted_at": intents.get("data_ts"),
            }
            status = "dry_run"

        event = {
            "symbol": symbol,
            "side": action,
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
        json.dumps({"data_ts": intents.get("data_ts"), "account": account}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"orders": len(results), "account": account}, ensure_ascii=False))


if __name__ == "__main__":
    main()
