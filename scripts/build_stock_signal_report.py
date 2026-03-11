from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    snap_path = ROOT / "data" / "market_snapshot.alpaca.stock.json"
    out_path = ROOT / "data" / "signal_report.stock.generated.json"
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    quality = int(snap.get("quality_score", 0))

    signals = []
    for sym in snap.get("symbols", []):
        q = snap.get("quotes", {}).get(sym, {})
        px = float(q.get("price", 0) or 0)
        score = 0.5 if px > 0 else 0.0
        signal = "hold"
        if score >= 0.6:
            signal = "buy"
        elif score <= 0.4:
            signal = "sell"
        signals.append(
            {
                "symbol": sym,
                "signal": signal,
                "score": round(score, 4),
                "confidence": 0.55 if quality >= 60 else 0.25,
                "risk_level": "medium",
                "reasons": ["price_available" if px > 0 else "price_missing", f"quality_score={quality}"],
            }
        )

    out = {
        "data_ts": snap.get("data_ts"),
        "quality_score": quality,
        "source_health": snap.get("source_health"),
        "signals": signals,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    main()
