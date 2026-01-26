import pandas as pd


def transform_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Canonical structural transformations for raw daily price data.

    Responsibilities:
    - Parse 'date' into datetime
    - Enforce numeric dtypes for OHLCV
    - Sort by date ascending (time-series correctness)
    - Return a clean DataFrame (no persistence, no reporting)
    """
    if df.empty:
        return df.copy()

    out = df.copy()

    # Normalize types
    out["date"] = pd.to_datetime(out["date"], errors="raise")

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="raise")

    # Ensure chronological order for downstream time-series operations
    out = out.sort_values("date").reset_index(drop=True)

    return out
