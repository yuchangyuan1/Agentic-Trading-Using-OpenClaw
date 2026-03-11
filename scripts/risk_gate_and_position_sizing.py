from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _parse_ts(ts: str | None) -> datetime:
    if not ts:
        return datetime.now(timezone.utc) - timedelta(days=365)
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc) - timedelta(days=365)


def main() -> None:
    strategy = _load_yaml(ROOT / "config" / "strategy_stock.yaml")
    sig = json.loads((ROOT / "data" / "signal_report.stock.generated.json").read_text(encoding="utf-8"))

    min_quality = int(strategy.get("risk", {}).get("min_quality_score", 60))
    max_pos_pct = float(strategy.get("risk", {}).get("max_pos_pct", 0.1))
    cooldown_hours = int(strategy.get("execution", {}).get("cooldown_hours", 24))

    last_actions_path = ROOT / "state" / "last_actions.json"
    if last_actions_path.exists():
        last_actions = json.loads(last_actions_path.read_text(encoding="utf-8"))
    else:
        last_actions = {}

    now = _parse_ts(sig.get("data_ts"))
    intents = []
    blocked = sig.get("quality_score", 0) < min_quality

    for row in sig.get("signals", []):
        symbol = row.get("symbol")
        raw_action = row.get("signal", "hold")
        action = "hold"

        if not blocked:
            action = raw_action

        la = last_actions.get(symbol, {})
        last_action = la.get("action")
        last_ts = _parse_ts(la.get("ts"))
        in_cooldown = (now - last_ts) < timedelta(hours=cooldown_hours)
        if action in {"buy", "sell"} and action == last_action and in_cooldown:
            action = "hold"

        if action == "buy":
            target_weight = max_pos_pct
        elif action == "sell":
            target_weight = 0.0
        else:
            target_weight = None

        intents.append(
            {
                "symbol": symbol,
                "action": action,
                "target_weight": target_weight,
                "reason": "; ".join(row.get("reasons", [])),
                "signal_score": row.get("score", 0),
            }
        )

        if action in {"buy", "sell"}:
            last_actions[symbol] = {"action": action, "ts": now.isoformat()}

    out = {
        "data_ts": sig.get("data_ts"),
        "blocked_new_buy": blocked,
        "trade_intents": intents,
    }
    out_path = ROOT / "outputs" / "trade_intents.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    last_actions_path.write_text(json.dumps(last_actions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    main()
