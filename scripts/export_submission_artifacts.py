from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def main() -> None:
    submissions = ROOT / "submissions"
    submissions.mkdir(parents=True, exist_ok=True)

    orders = _read_jsonl(ROOT / "state" / "live_orders.jsonl")
    orders = sorted(orders, key=lambda x: x.get("ts", ""))
    with (submissions / "orders.jsonl").open("w", encoding="utf-8") as f:
        for o in orders:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    account = {"equity": 100000.0, "cash": 100000.0}
    p = ROOT / "state" / "live_positions.json"
    if p.exists():
        account = json.loads(p.read_text(encoding="utf-8")).get("account", account)

    daily_csv = submissions / "daily_stock.csv"
    with daily_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "equity", "cash", "positions_count"])
        w.writeheader()
        w.writerow(
            {
                "date": datetime.now(timezone.utc).date().isoformat(),
                "equity": account.get("equity", 0),
                "cash": account.get("cash", 0),
                "positions_count": 0,
            }
        )

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "portfolio_value": account.get("equity", 0),
        "cash": account.get("cash", 0),
        "positions": [],
    }
    (submissions / "final_portfolio_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[ok] wrote submissions under {submissions}")


if __name__ == "__main__":
    main()
