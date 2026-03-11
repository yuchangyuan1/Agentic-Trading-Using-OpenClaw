from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _score_from_window(close: np.ndarray, vol: np.ndarray, i: int) -> float:
    ret_5d = close[i] / close[i - 5] - 1
    ret_20d = close[i] / close[i - 20] - 1
    daily_ret = close[max(1, i - 20) : i + 1]
    daily_ret = daily_ret[1:] / daily_ret[:-1] - 1
    vol_20d = float(np.std(daily_ret)) if len(daily_ret) else 0.0
    vol_ratio_5d = (float(np.mean(vol[i - 4 : i + 1])) / float(np.mean(vol[i - 19 : i + 1]))) if np.mean(vol[i - 19 : i + 1]) > 0 else 1.0

    momentum_score = float(np.clip((ret_20d + ret_5d) / 0.12, -1, 1))
    vol_score = float(np.clip(1 - vol_20d / 0.04, -1, 1))
    liq_score = float(np.clip((vol_ratio_5d - 0.8) / 0.7, -1, 1))
    return float(np.clip(0.50 + 0.25 * momentum_score + 0.15 * vol_score + 0.10 * liq_score, 0, 1))


def main() -> None:
    snap = json.loads((ROOT / "data" / "market_snapshot.alpaca.stock.json").read_text(encoding="utf-8"))
    rows = []

    for sym in snap.get("symbols", []):
        bars = snap.get("daily_bars", {}).get(sym, [])
        if len(bars) < 25:
            continue
        close = np.array([float(x.get("c", 0) or 0) for x in bars], dtype=float)
        vol = np.array([float(x.get("v", 0) or 0) for x in bars], dtype=float)

        pos = 0
        eq = 1.0
        for i in range(21, len(close) - 1):
            score = _score_from_window(close, vol, i)
            if score >= 0.62:
                pos = 1
            elif score <= 0.38:
                pos = 0
            ret_next = close[i + 1] / close[i] - 1
            eq *= 1 + pos * ret_next

        rows.append({"symbol": sym, "equity_curve_end": eq, "cum_return": eq - 1})

    if rows:
        df = pd.DataFrame(rows).sort_values("cum_return", ascending=False)
        avg_ret = float(df["cum_return"].mean())
        best_symbol = str(df.iloc[0]["symbol"])
    else:
        avg_ret = 0.0
        best_symbol = None

    out = {
        "symbols": rows,
        "avg_cum_return": avg_ret,
        "best_symbol": best_symbol,
    }
    out_path = ROOT / "outputs" / "backtest_stock_signal_report.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    main()
