from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from typing import List, Optional, Tuple


def _connect(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def _fetch_last_n_closes(
    con: sqlite3.Connection, symbol: str, n: int = 30
) -> List[Tuple[str, float]]:
    """Return last N (date, close) points for symbol, sorted ascending by date."""
    cur = con.cursor()
    cur.execute(
        """
        SELECT date, close
        FROM prices
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT ?;
        """,
        (symbol, n),
    )
    rows = cur.fetchall() or []
    pts = [(str(d), float(c)) for d, c in rows]
    pts.reverse()  # ascending
    return pts


def _fetch_latest_and_prev_close(
    con: sqlite3.Connection, symbol: str
) -> Optional[Tuple[str, float, Optional[str], Optional[float], Optional[float]]]:
    """Return (latest_date, latest_close, prev_date, prev_close, daily_return_pct)."""
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

    return latest_date, latest_close, prev_date, prev_close, ret_pct


def _fetch_latest_fx_rate(
    con: sqlite3.Connection, base: str = "USD", quote: str = "THB"
) -> Optional[Tuple[str, float]]:
    """Return (rate_date, rate) for latest FX rate in DB, or None."""
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


def _render_price_chart_png(
    con: sqlite3.Connection,
    symbols: List[str],
    out_png_path: str,
    n_points: int = 30,
) -> None:
    """Render a simple multi-line close-price chart as a PNG."""
    # Import here so the module can still be imported even if matplotlib isn't installed.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime as _dt

    plt.figure()

    for sym in symbols:
        pts = _fetch_last_n_closes(con, sym, n=n_points)
        if not pts:
            continue
        x = [_dt.fromisoformat(d) for d, _ in pts]
        y = [c for _, c in pts]
        plt.plot(x, y, label=sym)

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(ax.xaxis.get_major_locator())
    )

    plt.title(f"Close Prices (last {n_points} trading days)")
    plt.xlabel("Date")
    plt.ylabel("Close")
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.tight_layout()

    os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
    plt.savefig(out_png_path, dpi=150)
    plt.close()


def generate_daily_report_pdf(
    symbols: List[str],
    db_path: str = "data/market_data.db",
    out_path: Optional[str] = None,
) -> str:
    """Generate a one-page PDF daily report and return the PDF path."""
    if out_path is None:
        out_path = f"data/reports/daily_report_{date.today().isoformat()}.pdf"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Import here so this module can be imported even if reportlab isn't installed.
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    if not os.path.isfile(db_path):
        doc = SimpleDocTemplate(out_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Stock ETL Daily Report", styles["Title"]),
            Spacer(1, 0.2 * inch),
            Paragraph(f"Generated: {run_ts}", styles["Normal"]),
            Spacer(1, 0.2 * inch),
            Paragraph(f"ERROR: Database not found at {db_path}", styles["Normal"]),
        ]
        doc.build(story)
        return out_path

    con = _connect(db_path)
    try:
        # Build table rows
        rows: List[List[str]] = [
            [
                "Symbol",
                "Latest Date",
                "Latest Close",
                "Prev Date",
                "Prev Close",
                "1D Return",
            ]
        ]

        for sym in symbols:
            snap = _fetch_latest_and_prev_close(con, sym)
            if snap is None:
                rows.append([sym, "—", "—", "—", "—", "—"])
                continue

            latest_date, latest_close, prev_date, prev_close, ret_pct = snap
            rows.append(
                [
                    sym,
                    latest_date,
                    f"{latest_close:,.2f}",
                    prev_date or "—",
                    f"{prev_close:,.2f}" if prev_close is not None else "—",
                    f"{ret_pct:+.2f}%" if ret_pct is not None else "—",
                ]
            )

        fx_latest = _fetch_latest_fx_rate(con, "USD", "THB")

        # Chart image
        chart_path = os.path.join(os.path.dirname(out_path), "_close_chart.png")
        _render_price_chart_png(con, symbols, chart_path, n_points=30)
    finally:
        con.close()

    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Stock ETL Daily Report", styles["Title"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(f"Generated: {run_ts}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Symbols: {', '.join(symbols)}", styles["Normal"]))
    if fx_latest:
        fx_date, fx_rate = fx_latest
        story.append(
            Paragraph(
                f"FX (USD/THB): {fx_rate:,.4f} (as of {fx_date})", styles["Normal"]
            )
        )
    else:
        story.append(Paragraph("FX (USD/THB): —", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    tbl = Table(rows, hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
            ]
        )
    )

    story.append(tbl)
    story.append(Spacer(1, 0.25 * inch))

    if os.path.isfile(chart_path):
        # Fit chart to page width while preserving aspect ratio.
        img = Image(chart_path)
        img.drawWidth = 7.0 * inch
        img.drawHeight = 3.3 * inch
        story.append(Paragraph("Close price chart", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(img)

    doc.build(story)

    return out_path


def main() -> None:
    symbols = ["AAPL", "MSFT", "NVDA"]
    out = generate_daily_report_pdf(symbols)
    print(out)


if __name__ == "__main__":
    main()
