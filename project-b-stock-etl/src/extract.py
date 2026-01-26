import requests
import pandas as pd
from typing import Dict

from src.config import ALPHAVANTAGE_API_KEY

# Alpha Vantage base endpoint for all API queries
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"


def fetch_daily_adjusted(symbol: str) -> pd.DataFrame:
    """
    Fetch daily adjusted equity price data for a single ticker from Alpha Vantage.

    The function is responsible for:
    - calling the external API
    - validating the response structure
    - converting the returned JSON time series into a tabular DataFrame

    No business logic or persistence is performed here.
    """
    params: Dict[str, str] = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_API_KEY,
        "outputsize": "compact",  # last ~100 trading days
        "datatype": "json",
    }

    response = requests.get(
        ALPHAVANTAGE_BASE_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    # Alpha Vantage returns error messages as valid JSON,
    # so we must explicitly validate the expected payload.
    if "Time Series (Daily)" not in data:
        raise ValueError(f"Unexpected API response for symbol {symbol}: {data}")

    time_series = data["Time Series (Daily)"]

    # Convert nested JSON into a tabular structure and normalize column names
    df = pd.DataFrame.from_dict(time_series, orient="index").rename(
        columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume",
        }
    )

    df.index.name = "date"
    df.reset_index(inplace=True)

    return df
