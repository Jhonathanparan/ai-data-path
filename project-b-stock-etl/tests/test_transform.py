import pandas as pd

from src.transform import transform_prices


def test_transform_prices_basic_structure():
    """
    Smoke test to verify that transform_prices returns a clean,
    well-structured DataFrame with expected columns and ordering.
    """

    raw_data = pd.DataFrame(
        {
            "date": ["2026-01-03", "2026-01-01", "2026-01-02"],
            "open": ["10", "8", "9"],
            "high": ["11", "9", "10"],
            "low": ["9", "7", "8"],
            "close": ["10.5", "8.5", "9.5"],
            "volume": ["1000", "800", "900"],
        }
    )

    result = transform_prices(raw_data)

    # Result should be a DataFrame
    assert isinstance(result, pd.DataFrame)

    # Expected columns must exist
    expected_columns = ["date", "open", "high", "low", "close", "volume"]
    assert list(result.columns) == expected_columns

    # Dates should be sorted ascending
    assert result["date"].is_monotonic_increasing

    # Numeric columns should be numeric types
    for col in ["open", "high", "low", "close", "volume"]:
        assert pd.api.types.is_numeric_dtype(result[col])
