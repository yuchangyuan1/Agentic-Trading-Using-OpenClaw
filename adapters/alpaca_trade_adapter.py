from __future__ import annotations

import os
from typing import Any


class AlpacaTradeAdapter:
    def __init__(self) -> None:
        self.api_key = os.getenv("ALPACA_API_KEY", "")
        self.api_secret = os.getenv("ALPACA_API_SECRET", "")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    def _require_client(self):
        if not (self.api_key and self.api_secret):
            raise RuntimeError("Missing ALPACA_API_KEY / ALPACA_API_SECRET")
        try:
            from alpaca.trading.client import TradingClient
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("alpaca-py not installed") from exc
        return TradingClient(self.api_key, self.api_secret, paper="paper" in self.base_url)

    def get_account(self) -> dict[str, Any]:
        c = self._require_client()
        a = c.get_account()
        return {
            "equity": float(a.equity),
            "cash": float(a.cash),
            "buying_power": float(a.buying_power),
            "status": str(a.status),
        }

    def get_positions(self) -> list[dict[str, Any]]:
        c = self._require_client()
        items = c.get_all_positions()
        out: list[dict[str, Any]] = []
        for p in items:
            out.append({
                "symbol": p.symbol,
                "qty": float(p.qty),
                "market_value": float(p.market_value),
                "avg_entry_price": float(p.avg_entry_price),
            })
        return out

    def submit_market_order(self, symbol: str, qty: int, side: str, tif: str = "day") -> dict[str, Any]:
        c = self._require_client()
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce

        req = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY if tif.lower() == "day" else TimeInForce.GTC,
        )
        o = c.submit_order(order_data=req)
        return {
            "id": str(o.id),
            "symbol": o.symbol,
            "qty": float(o.qty),
            "side": str(o.side).lower(),
            "status": str(o.status),
            "filled_avg_price": float(o.filled_avg_price or 0.0),
            "submitted_at": str(o.submitted_at),
        }
