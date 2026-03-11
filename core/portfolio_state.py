from __future__ import annotations

from typing import Dict, List


def positions_to_map(positions: List[dict]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for p in positions:
        out[p.get("symbol", "")] = float(p.get("qty", 0) or 0)
    return out


def calc_target_qty(equity: float, target_weight: float, price: float) -> int:
    if price <= 0:
        return 0
    notional = max(equity * target_weight, 0.0)
    return int(notional // price)
