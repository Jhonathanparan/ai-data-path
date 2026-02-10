from __future__ import annotations

import logging
import sys
from datetime import date

from dotenv import load_dotenv

from src.notify.sendgrid_emailer import send_email
from src.pipeline import run_pipeline
from src.fx import fetch_fx_rate, upsert_fx_rate
from src.reporting.summary import build_summary, format_email
from src.reporting.daily_report import generate_daily_report_md
from src.reporting.pdf_report import generate_daily_report_pdf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
    force=True,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the ETL pipeline and email a daily summary with CSV attachments."""
    load_dotenv()
    logger.info("Starting run_daily")

    symbols = ["AAPL", "MSFT", "NVDA"]
    logger.info("Symbols configured: %s", symbols)

    # 1) Run ETL
    try:
        logger.info("Running ETL for symbols: %s", symbols)
        run_pipeline(symbols)
        logger.info("ETL completed.")
    except Exception:
        # Still attempt to email a summary (which will include warnings).
        logger.exception("ETL failed.")

    # 1b) Fetch + store FX rate (2nd data source)
    try:
        fx = fetch_fx_rate("USD", "THB")
        upsert_fx_rate("data/market_data.db", fx)
        logger.info(
            "Stored FX %s/%s=%s on %s", fx.base, fx.quote, fx.rate, fx.rate_date
        )
    except Exception:
        # Do not fail the run if FX is unavailable.
        logger.exception("FX fetch/store failed.")

    # 2) Build summary + attachments
    summary = build_summary(symbols)
    body = format_email(summary)
    subject = f"Stock ETL Report — {date.today().isoformat()}"

    # 2b) Generate markdown daily report
    report_path = None
    try:
        report_path = generate_daily_report_md(symbols)
        logger.info("Generated daily report: %s", report_path)
    except Exception:
        logger.exception("Failed to generate daily report.")

    # 2c) Generate PDF daily report
    pdf_report_path = None
    try:
        pdf_report_path = generate_daily_report_pdf(symbols)
        logger.info("Generated PDF report: %s", pdf_report_path)
    except Exception:
        logger.exception("Failed to generate PDF report.")

    # 3) Send email
    attachments = list(summary.processed_csv_files)
    if report_path:
        attachments.append(report_path)
    if pdf_report_path:
        attachments.append(pdf_report_path)

    send_email(subject=subject, body_text=body, attachments=attachments)
    logger.info("Email queued via SendGrid.")


if __name__ == "__main__":
    main()
