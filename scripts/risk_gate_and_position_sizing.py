from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def main() -> None:
    strategy = _load_yaml(ROOT / "config" / "strategy_stock.yaml")
    sig = json.loads((ROOT / "data" / "signal_report.stock.generated.json").read_text(encoding="utf-8"))

    min_quality = int(strategy.get("risk", {}).get("min_quality_score", 60))
    max_pos_pct = float(strategy.get("risk", {}).get("max_pos_pct", 0.1))

    intents = []
    blocked = sig.get("quality_score", 0) < min_quality
    for row in sig.get("signals", []):
        action = "hold"
        if not blocked:
            action = row.get("signal", "hold")
        if action == "buy":
            target_weight = max_pos_pct
        elif action == "sell":
            target_weight = 0.0
        else:
            target_weight = None

        intents.append(
            {
                "symbol": row.get("symbol"),
                "action": action,
                "target_weight": target_weight,
                "reason": "; ".join(row.get("reasons", [])),
                "signal_score": row.get("score", 0),
            }
        )

    out = {
        "data_ts": sig.get("data_ts"),
        "blocked_new_buy": blocked,
        "trade_intents": intents,
    }
    out_path = ROOT / "outputs" / "trade_intents.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    main()
