from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> None:
    day = datetime.now(timezone.utc).date().isoformat()
    base = ROOT / "archives" / day

    # submissions
    _copy_if_exists(ROOT / "submissions" / "orders.jsonl", base / "submissions" / "orders.jsonl")
    _copy_if_exists(ROOT / "submissions" / "daily_stock.csv", base / "submissions" / "daily_stock.csv")
    _copy_if_exists(
        ROOT / "submissions" / "final_portfolio_snapshot.json",
        base / "submissions" / "final_portfolio_snapshot.json",
    )

    # outputs/state snapshots
    _copy_if_exists(ROOT / "outputs" / "eval_metrics.json", base / "outputs" / "eval_metrics.json")
    _copy_if_exists(ROOT / "outputs" / "trade_intents.json", base / "outputs" / "trade_intents.json")
    _copy_if_exists(ROOT / "state" / "live_positions.json", base / "state" / "live_positions.json")
    _copy_if_exists(ROOT / "state" / "live_orders.jsonl", base / "state" / "live_orders.jsonl")

    print(f"[ok] archived daily artifacts to {base}")


if __name__ == "__main__":
    main()
