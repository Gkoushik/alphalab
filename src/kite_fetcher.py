import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _get_kite():
    """Initialize and return an authenticated KiteConnect instance."""
    try:
        from kiteconnect import KiteConnect
    except ImportError:
        raise ImportError("Run: pip install kiteconnect")

    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")

    if not api_key or not access_token:
        raise EnvironmentError(
            "KITE_API_KEY and KITE_ACCESS_TOKEN must be set in your .env file."
        )

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite


def generate_access_token():
    """
    One-time flow to generate an access token from a request token.
    Run this once after logging in via the Kite login URL.

    Steps:
        1. Go to: https://kite.trade/connect/login?api_key=<your_api_key>
        2. After login, copy the request_token from the redirect URL
        3. Call this function with that request_token
        4. Paste the printed access_token into your .env file
    """
    from kiteconnect import KiteConnect

    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")

    if not api_key or not api_secret:
        raise EnvironmentError("KITE_API_KEY and KITE_API_SECRET must be set in .env")

    request_token = input("Paste your request_token here: ").strip()

    kite = KiteConnect(api_key=api_key)
    session = kite.generate_session(request_token, api_secret=api_secret)
    access_token = session["access_token"]

    print(f"\nAdd this to your .env file:\nKITE_ACCESS_TOKEN={access_token}")
    return access_token


def fetch(
    instrument_token: int,
    from_date: str,
    to_date: str = None,
    interval: str = "day",
    save: bool = False,
    ticker_label: str = None,
) -> pd.DataFrame:
    """
    Fetch OHLCV historical data from Kite Connect.

    Args:
        instrument_token: Kite instrument token (e.g. 738561 for RELIANCE)
        from_date:        "YYYY-MM-DD"
        to_date:          "YYYY-MM-DD" (defaults to today)
        interval:         "minute", "3minute", "5minute", "15minute",
                          "30minute", "60minute", "day"
        save:             Save result as CSV to data/
        ticker_label:     Label used for the saved filename (e.g. "RELIANCE")

    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    kite = _get_kite()

    to_date = to_date or datetime.today().strftime("%Y-%m-%d")

    records = kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval=interval,
    )

    df = pd.DataFrame(records)
    df.rename(columns={"date": "date"}, inplace=True)
    df.set_index("date", inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df[["open", "high", "low", "close", "volume"]]

    if save and ticker_label:
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        path = data_dir / f"{ticker_label}_{interval}.csv"
        df.to_csv(path)
        print(f"Saved to {path}")

    return df


def search_instrument(query: str, exchange: str = "NSE") -> pd.DataFrame:
    """
    Search for instruments by name to find their instrument_token.

    Args:
        query:    e.g. "RELIANCE", "INFY"
        exchange: "NSE", "BSE", "NFO", etc.

    Returns:
        DataFrame of matching instruments with tradingsymbol and instrument_token
    """
    kite = _get_kite()
    instruments = kite.instruments(exchange)
    df = pd.DataFrame(instruments)
    mask = df["tradingsymbol"].str.contains(query.upper(), na=False)
    return df[mask][["instrument_token", "tradingsymbol", "name", "exchange", "instrument_type"]]
