from pathlib import Path
import sqlite3
import pandas as pd


def save_dataframe_csv(
    df: pd.DataFrame,
    symbol: str,
    base_dir: str = "data",
) -> None:
    """
    Persist transformed price data to disk as CSV (snapshot behavior).

    Each run overwrites the existing file.

    Directory structure:
    data/
      processed/
        prices_<SYMBOL>.csv
    """
    if df.empty:
        return

    base_path = Path(base_dir)
    processed_dir = base_path / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    output_path = processed_dir / f"prices_{symbol}.csv"
    df.to_csv(output_path, index=False)


def save_dataframe_sqlite(
    df: pd.DataFrame,
    symbol: str,
    db_path: str = "data/market_data.db",
) -> None:
    """
    Persist transformed price data into a local SQLite database
    in an idempotent way.

    Table: prices
    Unique key: (symbol, date)
    """
    if df.empty:
        return

    df_to_save = df.copy()
    df_to_save["symbol"] = symbol
    df_to_save["date"] = pd.to_datetime(df_to_save["date"], errors="raise").dt.strftime(
        "%Y-%m-%d"
    )

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Ensure table exists without uniqueness constraint
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prices (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER
            )
            """
        )

        # Enforce idempotency even if the table already existed without constraints
        try:
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_prices_symbol_date ON prices(symbol, date)"
            )
        except sqlite3.IntegrityError:
            # Existing duplicates prevent index creation → de-duplicate once
            cursor.execute(
                """
                CREATE TABLE prices_dedup AS
                SELECT
                    symbol,
                    date,
                    open,
                    high,
                    low,
                    close,
                    volume
                FROM prices
                GROUP BY symbol, date
                """
            )
            cursor.execute("DROP TABLE prices")
            cursor.execute("ALTER TABLE prices_dedup RENAME TO prices")
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_prices_symbol_date ON prices(symbol, date)"
            )

        # Insert rows safely (ignore duplicates)
        for _, row in df_to_save.iterrows():
            cursor.execute(
                """
                INSERT OR IGNORE INTO prices
                (symbol, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["symbol"],
                    row["date"],
                    row["open"],
                    row["high"],
                    row["low"],
                    row["close"],
                    row["volume"],
                ),
            )

        conn.commit()
