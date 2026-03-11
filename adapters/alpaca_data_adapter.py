from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlpacaDataAdapter:
    """Thin Alpaca market data wrapper.

    If alpaca-py is unavailable or credentials are missing, callers should handle the
    raised RuntimeError and fallback to dry-run data.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("ALPACA_API_KEY", "")
        self.api_secret = os.getenv("ALPACA_API_SECRET", "")

    def _require_client(self):
        if not (self.api_key and self.api_secret):
            raise RuntimeError("Missing ALPACA_API_KEY / ALPACA_API_SECRET")
        try:
            from alpaca.data.historical import StockHistoricalDataClient
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("alpaca-py not installed") from exc
        return StockHistoricalDataClient(self.api_key, self.api_secret)

    def get_latest_snapshot(self, symbols: list[str]) -> dict[str, Any]:
        client = self._require_client()
        from alpaca.data.requests import StockLatestQuoteRequest

        req = StockLatestQuoteRequest(symbol_or_symbols=symbols)
        quotes = client.get_stock_latest_quote(req)
        out: dict[str, Any] = {}
        for sym in symbols:
            q = quotes.get(sym)
            if q is None:
                continue
            out[sym] = {
                "symbol": sym,
                "bid_price": float(getattr(q, "bid_price", 0.0) or 0.0),
                "ask_price": float(getattr(q, "ask_price", 0.0) or 0.0),
                "price": float(getattr(q, "ask_price", 0.0) or getattr(q, "bid_price", 0.0) or 0.0),
                "ts": str(getattr(q, "timestamp", _utc_now_iso())),
            }
        return out
