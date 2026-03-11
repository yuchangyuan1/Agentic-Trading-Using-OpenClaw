from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.alpaca_data_adapter import AlpacaDataAdapter


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def main() -> None:
    cfg = _load_yaml(ROOT / "config" / "alpaca.yaml")
    symbols = cfg.get("symbols", ["AAPL", "MSFT"])
    out_file = ROOT / "data" / "market_snapshot.alpaca.stock.json"

    adapter = AlpacaDataAdapter()
    data_ts = datetime.now(timezone.utc).isoformat()
    try:
        latest = adapter.get_latest_snapshot(symbols)
        source_health = "ok"
        quality = 85
    except Exception as exc:
        latest = {s: {"symbol": s, "price": 0.0, "ts": data_ts} for s in symbols}
        source_health = f"degraded:{type(exc).__name__}"
        quality = 40

    payload = {
        "data_ts": data_ts,
        "market": "US_STOCK",
        "symbols": symbols,
        "quotes": latest,
        "freshness": "realtime",
        "source_health": source_health,
        "quality_score": quality,
    }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote {out_file}")


if __name__ == "__main__":
    main()
