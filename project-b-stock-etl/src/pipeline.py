import logging
import sys
import time
from src.load import save_dataframe_csv, save_dataframe_sqlite
from src.extract import fetch_daily_adjusted
from src.transform import transform_prices

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Entry point for the stock ETL pipeline.

    This stage orchestrates extract → transform with
    logging and rate-limit safety.
    """
    symbols = ["AAPL", "MSFT", "NVDA"]

    try:
        logger.info("Starting the stock ETL pipeline.")

        for symbol in symbols:
            try:
                df = fetch_daily_adjusted(symbol)
                df = transform_prices(df)
                save_dataframe_csv(df, symbol)
                save_dataframe_sqlite(df, symbol)
                logger.info(f"Fetched {len(df)} rows for {symbol}")
                logger.info("Saved processed data for %s (CSV + SQLite)", symbol)

                preview = df.tail(10).reset_index(drop=True)
                preview.index = preview.index + 1
                logger.info("\n%s", preview)

                # Respect Alpha Vantage free-tier rate limits
                time.sleep(12)

            except Exception:
                logger.exception("Failed processing symbol: %s", symbol)
                continue

        logger.info("Pipeline run completed.")

    except Exception:
        logger.exception("An error occurred during the pipeline execution.")
        raise


if __name__ == "__main__":
    main()
