import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
import os

TICKERS = {
    "ALFEN.AS": {"name": "Alfen N.V.", "exchange": "Euronext Amsterdam", "currency": "EUR"},
    "PNDORA.CO": {"name": "Pandora A/S", "exchange": "Nasdaq Copenhagen", "currency": "DKK"},
    "AZA.ST": {"name": "Avanza Bank", "exchange": "Nasdaq Stockholm", "currency": "SEK"},
    "NOVO-B.CO": {"name": "Novo Nordisk", "exchange": "Nasdaq Copenhagen", "currency": "DKK"},
    "GLOB": {"name": "Globant", "exchange": "NYSE", "currency": "USD"},
    "NVDA": {"name": "NVIDIA", "exchange": "Nasdaq", "currency": "USD"},
    "AAPL": {"name": "Apple", "exchange": "Nasdaq", "currency": "USD"},
    "JPM": {"name": "JPMorgan Chase", "exchange": "NYSE", "currency": "USD"},
}
#  this will yield one csv per ticker:
def fetch_and_save():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    os.makedirs("data", exist_ok=True)

    for ticker, meta in TICKERS.items():
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty:
            print(f"No data for {ticker} (market likely closed)")
            continue
        df["ticker"] = ticker
        df["company"] = meta["name"]
        df["exchange"] = meta["exchange"]
        df["currency"] = meta["currency"]
        df["fetched_at_utc"] = timestamp

        outfile = f"data/{ticker}.csv"
        file_exists = os.path.exists(outfile)
        df.to_csv(outfile, mode="a", header=not file_exists)
        print(f"Appended {ticker} data to {outfile}")

if __name__ == "__main__":
    fetch_and_save()