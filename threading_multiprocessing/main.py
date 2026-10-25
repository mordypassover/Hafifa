import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


SOURCE_FILES = {
    os.environ["BITCOIN_SYMBOL"]: os.environ["BITCOIN_FILE"],
    os.environ["AMAZON_SYMBOL"]: os.environ["AMAZON_FILE"],
    os.environ["GOOGLE_SYMBOL"]: os.environ["GOOGLE_FILE"],
}
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
MAX_WORKERS = 3


def read_hours(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return [
            datetime.strptime(line.strip(), DATE_FORMAT)
            for line in file
            if line.strip()
        ]


def fetch_prices(symbol, start, end):
    stock = yf.Ticker(symbol)

    return stock.history( start=start, end=end, interval="1h", timeout=20)


def calculate_change(hour, prices, symbol):

    requested_time = pd.Timestamp(hour, tz="UTC")

    change = None

    # Find the latest available candle at or before the requested time
    available_prices = prices.loc[prices.index <= requested_time]

    if len(available_prices) >= 2:
        current_price = available_prices.iloc[-1]
        previous_price = available_prices.iloc[-2]

        if previous_price != 0:
            change = (
                (current_price - previous_price)
                / previous_price
            ) * 100

    return {
        "hour": hour.strftime(DATE_FORMAT),
        "stock type": symbol,
        "percentage change": change,
    }


def process_file(symbol, filename):
    hours = read_hours(BASE_DIR / filename)

    if not hours:
        return []

    earliest = min(hours).replace(
        minute=0, second=0, microsecond=0
    )
    latest = max(hours).replace(
        minute=0, second=0, microsecond=0
    )

    start = earliest - timedelta(days=7)
    end = latest + timedelta(hours=1)

    history = fetch_prices(symbol, start, end)

    if history.empty:
        return [calculate_change(hour, pd.Series(dtype=float),symbol) for hour in hours]

    history.index = history.index.tz_convert("UTC")
    prices = history["Close"]

    return [
        calculate_change(hour, prices, symbol) for hour in hours
    ]


def main():
    destination_file = os.environ["DESTINATION_FILE"]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results_by_file = list(
            executor.map(
                process_file,
                SOURCE_FILES.keys(),
                SOURCE_FILES.values(),
            )
        )

    results = []

    for file_results in results_by_file:
        for result in file_results:
            results.append(result)

    output_path = BASE_DIR / destination_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        results,
        columns=["hour", "stock type", "percentage change"],
    ).to_csv(output_path, index=False)

    print(f"Saved {len(results)} rows to {output_path}")


if __name__ == "__main__":
    main()