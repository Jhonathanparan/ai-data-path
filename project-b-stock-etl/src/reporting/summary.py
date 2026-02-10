from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class RunSummary:
    """Operational summary of a single ETL run."""

    run_ts: str
    symbols: List[str]
    processed_csv_files: List[str]
    db_total_rows: Optional[int]
    notes: List[str]


def _db_row_count(db_path: str) -> Optional[int]:
    """Return total rows in the `prices` table, or None if unavailable."""
    if not os.path.isfile(db_path):
        return None

    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM prices;")
        row = cur.fetchone()
        con.close()
        if not row:
            return None
        return int(row[0])
    except Exception:
        return None


def build_summary(
    symbols: List[str],
    processed_dir: str = "data/processed",
    db_path: str = "data/market_data.db",
) -> RunSummary:
    """Build a RunSummary including attachments and basic DB sanity info."""
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notes: List[str] = []

    processed_csv_files: List[str] = []
    if not os.path.isdir(processed_dir):
        notes.append(f"Processed directory missing: {processed_dir}")
    else:
        for symbol in symbols:
            expected = os.path.join(processed_dir, f"prices_{symbol}.csv")
            if os.path.isfile(expected):
                processed_csv_files.append(expected)
            else:
                notes.append(f"Missing CSV for {symbol}: {expected}")

    db_total_rows = _db_row_count(db_path)
    if db_total_rows is None:
        notes.append("Could not determine DB row count (missing DB or table mismatch).")

    return RunSummary(
        run_ts=run_ts,
        symbols=symbols,
        processed_csv_files=processed_csv_files,
        db_total_rows=db_total_rows,
        notes=notes,
    )


def format_email(summary: RunSummary) -> str:
    """Format a RunSummary into a plain-text email body."""
    lines: List[str] = []
    lines.append(f"Stock ETL Run Summary — {summary.run_ts}")
    lines.append("")
    lines.append(f"Symbols: {', '.join(summary.symbols)}")

    if summary.db_total_rows is not None:
        lines.append(f"DB rows (prices): {summary.db_total_rows}")
    else:
        lines.append("DB rows (prices): unknown")

    lines.append(f"Attachments: {len(summary.processed_csv_files)} CSV file(s)")
    for path in summary.processed_csv_files:
        lines.append(f"- {os.path.basename(path)}")

    if summary.notes:
        lines.append("")
        lines.append("Notes / Warnings:")
        for note in summary.notes:
            lines.append(f"- {note}")

    return "\n".join(lines)
