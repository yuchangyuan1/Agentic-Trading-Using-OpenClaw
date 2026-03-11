from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def init_files() -> None:
    (ROOT / "state").mkdir(parents=True, exist_ok=True)
    eq = ROOT / "state" / "equity_curve.csv"
    if not eq.exists():
        with eq.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["date", "equity"])
            w.writeheader()
            w.writerow({"date": datetime.now(timezone.utc).date().isoformat(), "equity": 100000.0})

    lp = ROOT / "state" / "live_positions.json"
    if not lp.exists():
        lp.write_text(
            json.dumps({"data_ts": None, "account": {"equity": 100000.0, "cash": 100000.0}, "positions": []}),
            encoding="utf-8",
        )


def append_equity() -> None:
    lp = ROOT / "state" / "live_positions.json"
    data = json.loads(lp.read_text(encoding="utf-8")) if lp.exists() else {}
    equity = float(data.get("account", {}).get("equity", 100000.0))
    row = {"date": datetime.now(timezone.utc).date().isoformat(), "equity": equity}

    eq = ROOT / "state" / "equity_curve.csv"
    existing = []
    if eq.exists():
        with eq.open("r", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
            normalized = []
            for r in existing:
                nr = {str(k).replace("\ufeff", ""): v for k, v in r.items()}
                normalized.append({"date": nr.get("date", ""), "equity": nr.get("equity", "")})
            existing = normalized
    if existing and existing[-1].get("date") == row["date"]:
        existing[-1] = row
    else:
        existing.append(row)

    with eq.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "equity"])
        w.writeheader()
        w.writerows(existing)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    if args.init:
        init_files()
    append_equity()
    print("[ok] end_of_day_rollup done")
