import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"

# API configuration
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

if not ALPHAVANTAGE_API_KEY:
    raise ValueError("Missing ALPHAVANTAGE_API_KEY environment variable")


# Symbols configuration (optional override via env)
# Example: SYMBOLS="AAPL,MSFT,NVDA" or "AAPL MSFT NVDA"
_raw_symbols = (os.getenv("SYMBOLS") or "").strip()

if _raw_symbols:
    STOCK_SYMBOLS = [
        s.strip().upper() for s in _raw_symbols.replace(",", " ").split() if s.strip()
    ]
else:
    STOCK_SYMBOLS = ["AAPL", "MSFT", "NVDA"]
