from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _factor_score(bars: list[dict], px: float, w_m: float, w_v: float, w_l: float) -> tuple[float, list[str]]:
    reasons: list[str] = []
    if len(bars) < 22:
        return 0.5 if px > 0 else 0.0, ["insufficient_bars(<22)"]

    close = np.array([float(x.get("c", 0) or 0) for x in bars], dtype=float)
    vol = np.array([float(x.get("v", 0) or 0) for x in bars], dtype=float)
    if np.any(close <= 0):
        return 0.3, ["invalid_close"]

    ret_5d = close[-1] / close[-6] - 1 if len(close) >= 6 else 0.0
    ret_20d = close[-1] / close[-21] - 1 if len(close) >= 21 else 0.0
    daily_ret = close[1:] / close[:-1] - 1
    vol_20d = float(np.std(daily_ret[-20:])) if len(daily_ret) >= 20 else float(np.std(daily_ret))
    vol_ratio_5d = (float(np.mean(vol[-5:])) / float(np.mean(vol[-20:]))) if np.mean(vol[-20:]) > 0 else 1.0

    momentum_score = float(np.clip((ret_20d + ret_5d) / 0.12, -1, 1))
    vol_score = float(np.clip(1 - vol_20d / 0.04, -1, 1))
    liq_score = float(np.clip((vol_ratio_5d - 0.8) / 0.7, -1, 1))

    score = 0.50 + w_m * momentum_score + w_v * vol_score + w_l * liq_score
    score = float(np.clip(score, 0, 1))

    reasons.extend(
        [
            f"ret_5d={ret_5d:.4f}",
            f"ret_20d={ret_20d:.4f}",
            f"vol_20d={vol_20d:.4f}",
            f"volume_ratio_5d={vol_ratio_5d:.3f}",
            f"weights(m/v/l)=({w_m:.2f}/{w_v:.2f}/{w_l:.2f})",
        ]
    )
    return score, reasons


def main() -> None:
    snap_path = ROOT / "data" / "market_snapshot.alpaca.stock.json"
    out_path = ROOT / "data" / "signal_report.stock.generated.json"
    strategy = _load_yaml(ROOT / "config" / "strategy_stock.yaml")
    buy_score = float(strategy.get("signal", {}).get("buy_score", 0.6))
    sell_score = float(strategy.get("signal", {}).get("sell_score", 0.4))

    factors = strategy.get("signal", {}).get("factors", {})
    w_m = float(factors.get("momentum_weight", 0.25))
    w_v = float(factors.get("volatility_weight", 0.15))
    w_l = float(factors.get("liquidity_weight", 0.10))

    # normalize if overweight
    total = abs(w_m) + abs(w_v) + abs(w_l)
    if total > 0.5:
        scale = 0.5 / total
        w_m, w_v, w_l = w_m * scale, w_v * scale, w_l * scale

    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    quality = int(snap.get("quality_score", 0))

    signals = []
    for sym in snap.get("symbols", []):
        q = snap.get("quotes", {}).get(sym, {})
        bars = snap.get("daily_bars", {}).get(sym, [])
        px = float(q.get("price", 0) or 0)
        score, reasons = _factor_score(bars, px, w_m=w_m, w_v=w_v, w_l=w_l)

        signal = "hold"
        if score >= buy_score:
            signal = "buy"
        elif score <= sell_score:
            signal = "sell"

        confidence = min(0.95, 0.35 + 0.5 * abs(score - 0.5) * 2)
        confidence = confidence * (1.0 if quality >= 60 else 0.6)
        risk_level = "low" if score > 0.65 else ("high" if score < 0.35 else "medium")

        signals.append(
            {
                "symbol": sym,
                "signal": signal,
                "score": round(score, 4),
                "confidence": round(float(confidence), 4),
                "risk_level": risk_level,
                "reasons": reasons + [f"quality_score={quality}"],
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
