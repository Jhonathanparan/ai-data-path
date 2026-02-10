from __future__ import annotations

import json
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Tuple


FRANKFURTER_BASE_URL = "https://api.frankfurter.dev/v1/latest"
DEFAULT_SOURCE = "frankfurter"


@dataclass(frozen=True)
class FxRate:
    rate_date: str
    base: str
    quote: str
    rate: float
    source: str
    fetched_at: str


def fetch_fx_rate(base: str = "USD", quote: str = "THB") -> FxRate:
    """Fetch latest FX rate from Frankfurter.

    Frankfurter docs: https://frankfurter.dev/
    Endpoint pattern: /v1/latest?base=USD&symbols=THB
    """
    base = base.upper().strip()
    quote = quote.upper().strip()

    params = {"base": base, "symbols": quote}
    url = f"{FRANKFURTER_BASE_URL}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(
        url,
        headers={
            # Some CDNs/WAFs reject the default Python-urllib user-agent.
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) StockETL/1.0",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"FX API HTTP error: {e.code} {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"FX API connection error: {e.reason}") from e
    except Exception as e:
        raise RuntimeError(f"FX API parse/unknown error: {e}") from e

    # Frankfurter returns: {"amount":1.0,"base":"USD","date":"2026-02-10","rates":{"THB":35.12}}
    rate_date = str(payload.get("date") or date.today().isoformat())
    rates = payload.get("rates") or {}

    if quote not in rates:
        raise RuntimeError(f"FX API response missing rate for {quote}: {payload}")

    rate = float(rates[quote])
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return FxRate(
        rate_date=rate_date,
        base=base,
        quote=quote,
        rate=rate,
        source=DEFAULT_SOURCE,
        fetched_at=fetched_at,
    )


def upsert_fx_rate(db_path: str, fx: FxRate) -> None:
    """Upsert a single FX rate into SQLite (idempotent by PK)."""
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO fx_rates (rate_date, base, quote, rate, source, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(rate_date, base, quote)
            DO UPDATE SET
              rate = excluded.rate,
              source = excluded.source,
              fetched_at = excluded.fetched_at;
            """,
            (fx.rate_date, fx.base, fx.quote, fx.rate, fx.source, fx.fetched_at),
        )
        con.commit()
    finally:
        con.close()


def get_latest_fx_rate(
    db_path: str, base: str = "USD", quote: str = "THB"
) -> Optional[Tuple[str, float]]:
    """Return (rate_date, rate) for the latest stored FX rate, or None."""
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(
            """
            SELECT rate_date, rate
            FROM fx_rates
            WHERE base = ? AND quote = ?
            ORDER BY rate_date DESC
            LIMIT 1;
            """,
            (base.upper().strip(), quote.upper().strip()),
        )
        row = cur.fetchone()
        if not row:
            return None
        return str(row[0]), float(row[1])
    finally:
        con.close()


def main() -> None:
    db_path = "data/market_data.db"

    fx = fetch_fx_rate("USD", "THB")
    upsert_fx_rate(db_path, fx)

    latest = get_latest_fx_rate(db_path, "USD", "THB")
    print(f"Stored FX: {latest}")


if __name__ == "__main__":
    main()
