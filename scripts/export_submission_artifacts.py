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


def _validate(schema_path: Path, payload: dict) -> None:
    try:
        import jsonschema  # type: ignore

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(payload, schema)
    except ModuleNotFoundError:
        return


def main() -> None:
    submissions = ROOT / "submissions"
    submissions.mkdir(parents=True, exist_ok=True)

    orders = _read_jsonl(ROOT / "state" / "live_orders.jsonl")
    orders = sorted(orders, key=lambda x: x.get("ts", ""))

    order_schema = ROOT / "schemas" / "order_event.schema.json"
    for o in orders:
        _validate(order_schema, o)

    with (submissions / "orders.jsonl").open("w", encoding="utf-8") as f:
        for o in orders:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    account = {"equity": 100000.0, "cash": 100000.0}
    positions = []
    p = ROOT / "state" / "live_positions.json"
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        account = data.get("account", account)
        positions = data.get("positions", [])

    row = {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "equity": float(account.get("equity", 0)),
        "cash": float(account.get("cash", 0)),
        "positions_count": len(positions),
    }
    _validate(ROOT / "schemas" / "daily_stock.schema.json", row)

    daily_csv = submissions / "daily_stock.csv"
    with daily_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "equity", "cash", "positions_count"])
        w.writeheader()
        w.writerow(row)

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "portfolio_value": float(account.get("equity", 0)),
        "cash": float(account.get("cash", 0)),
        "positions": positions,
    }
    _validate(ROOT / "schemas" / "final_snapshot.schema.json", snapshot)

    (submissions / "final_portfolio_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[ok] wrote submissions under {submissions}")


if __name__ == "__main__":
    main()
