from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional
from src.fx import get_latest_fx_rate


@dataclass(frozen=True)
class SymbolSnapshot:
    symbol: str
    latest_date: str
    latest_close: float
    prev_date: Optional[str]
    prev_close: Optional[float]
    daily_return_pct: Optional[float]


def _connect(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def _fetch_symbol_snapshot(
    con: sqlite3.Connection, symbol: str
) -> Optional[SymbolSnapshot]:
    """Fetch latest + previous close for a symbol and compute 1-day return."""
    cur = con.cursor()

    cur.execute(
        """
        SELECT date, close
        FROM prices
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT 1;
        """,
        (symbol,),
    )
    latest = cur.fetchone()
    if not latest:
        return None

    latest_date, latest_close = str(latest[0]), float(latest[1])

    cur.execute(
        """
        SELECT date, close
        FROM prices
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT 1 OFFSET 1;
        """,
        (symbol,),
    )
    prev = cur.fetchone()

    prev_date: Optional[str] = None
    prev_close: Optional[float] = None
    ret_pct: Optional[float] = None

    if prev:
        prev_date, prev_close = str(prev[0]), float(prev[1])
        if prev_close != 0:
            ret_pct = (latest_close - prev_close) / prev_close * 100.0

    return SymbolSnapshot(
        symbol=symbol,
        latest_date=latest_date,
        latest_close=latest_close,
        prev_date=prev_date,
        prev_close=prev_close,
        daily_return_pct=ret_pct,
    )


def _db_row_count(con: sqlite3.Connection) -> Optional[int]:
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM prices;")
        row = cur.fetchone()
        return int(row[0]) if row else None
    except Exception:
        return None


def generate_daily_report_md(
    symbols: List[str],
    db_path: str = "data/market_data.db",
    out_path: Optional[str] = None,
) -> str:
    """Generate a markdown daily report from SQLite and write it to out_path.

    Returns the output path.
    """
    if out_path is None:
        out_path = f"data/reports/daily_report_{date.today().isoformat()}.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.isfile(db_path):
        content = (
            "# Stock ETL Daily Report\n\n"
            f"Generated: {run_ts}\n\n"
            f"**ERROR:** Database not found at `{db_path}`\n"
        )
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        return out_path

    fx_latest = get_latest_fx_rate(db_path, "USD", "THB")

    con = _connect(db_path)
    try:
        total_rows = _db_row_count(con)
        snapshots: List[SymbolSnapshot] = []
        missing: List[str] = []

        for sym in symbols:
            snap = _fetch_symbol_snapshot(con, sym)
            if snap is None:
                missing.append(sym)
            else:
                snapshots.append(snap)
    finally:
        con.close()

    lines: List[str] = []
    lines.append("# Stock ETL Daily Report")
    lines.append("")
    lines.append(f"Generated: {run_ts}")
    lines.append("")
    lines.append(f"Symbols: {', '.join(symbols)}")
    lines.append("")
    lines.append(
        f"DB rows (prices): {total_rows if total_rows is not None else 'unknown'}"
    )
    lines.append("")

    if fx_latest:
        fx_date, fx_rate = fx_latest
        lines.append(f"FX (USD/THB): {fx_rate:,.4f} (as of {fx_date})")
    else:
        lines.append("FX (USD/THB): —")

    lines.append("")
    lines.append("## Latest Close & 1-Day Return")
    lines.append("")
    lines.append(
        "| Symbol | Latest Date | Latest Close | Prev Date | Prev Close | 1D Return |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")

    for s in snapshots:
        latest_close = f"{s.latest_close:,.2f}"
        prev_date = s.prev_date or "—"
        prev_close = f"{s.prev_close:,.2f}" if s.prev_close is not None else "—"
        ret = f"{s.daily_return_pct:+.2f}%" if s.daily_return_pct is not None else "—"
        lines.append(
            f"| {s.symbol} | {s.latest_date} | {latest_close} | {prev_date} | {prev_close} | {ret} |"
        )

    if missing:
        lines.append("")
        lines.append("## Notes")
        lines.append("")
        lines.append("Missing symbols in DB (no rows found):")
        for sym in missing:
            lines.append(f"- {sym}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return out_path


def main() -> None:
    symbols = ["AAPL", "MSFT", "NVDA"]
    out = generate_daily_report_md(symbols)
    print(out)


if __name__ == "__main__":
    main()
