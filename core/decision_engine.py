from __future__ import annotations


def decide_action(score: float, buy_score: float = 0.6, sell_score: float = 0.4) -> str:
    if score >= buy_score:
        return "buy"
    if score <= sell_score:
        return "sell"
    return "hold"
