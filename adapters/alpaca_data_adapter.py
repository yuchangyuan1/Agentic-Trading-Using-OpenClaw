from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
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

    def get_daily_bars(self, symbols: list[str], lookback_days: int = 40) -> dict[str, list[dict[str, Any]]]:
        client = self._require_client()
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=max(lookback_days * 2, 20))
        req = StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Day, start=start, end=end)
        bars = client.get_stock_bars(req)

        out: dict[str, list[dict[str, Any]]] = {}
        for sym in symbols:
            rows = bars.data.get(sym, []) if hasattr(bars, "data") else []
            out[sym] = [
                {
                    "t": str(getattr(r, "timestamp", "")),
                    "o": float(getattr(r, "open", 0.0) or 0.0),
                    "h": float(getattr(r, "high", 0.0) or 0.0),
                    "l": float(getattr(r, "low", 0.0) or 0.0),
                    "c": float(getattr(r, "close", 0.0) or 0.0),
                    "v": float(getattr(r, "volume", 0.0) or 0.0),
                }
                for r in rows[-lookback_days:]
            ]
        return out
