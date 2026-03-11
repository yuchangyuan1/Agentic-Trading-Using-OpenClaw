from __future__ import annotations

import json
from math import sqrt
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _max_drawdown(curve: pd.Series) -> float:
    peak = curve.cummax()
    dd = (curve - peak) / peak.replace(0, pd.NA)
    return float(dd.min()) if len(dd) else 0.0


def main() -> None:
    eq_path = ROOT / "state" / "equity_curve.csv"
    if not eq_path.exists():
        # bootstrap 1-day curve
        pd.DataFrame([{"date": pd.Timestamp.utcnow().date().isoformat(), "equity": 100000.0}]).to_csv(
            eq_path, index=False
        )

    df = pd.read_csv(eq_path)
    df["equity"] = pd.to_numeric(df["equity"], errors="coerce").ffill()
    df["ret"] = df["equity"].pct_change().fillna(0.0)

    cr = float(df["equity"].iloc[-1] / df["equity"].iloc[0] - 1.0) if len(df) > 1 else 0.0
    dv = float(df["ret"].std(ddof=0))
    av = float(dv * sqrt(252))
    sr = float((df["ret"].mean() / dv) * sqrt(252)) if dv > 0 else 0.0
    md = _max_drawdown(df["equity"])

    out = {"CR": cr, "SR": sr, "MD": md, "DV": dv, "AV": av}
    out_path = ROOT / "outputs" / "eval_metrics.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    main()
