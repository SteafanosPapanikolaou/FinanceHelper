import requests
import csv
from datetime import datetime
from fuzzywuzzy import process


class BinanceDataFetcher:
    def __init__(self):
        self.base_url = 'https://api.binance.com/api/v3/klines'

    def get_klines(self, symbol='', interval='1h', limit=10):
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': limit
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    def save_to_csv(self, data, filename='output.csv'):
        header = [
            'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close Time', 'Quote Asset Volume', 'Number of Trades',
            'Taker Buy Base Volume', 'Taker Buy Quote Volume', 'Ignore'
        ]

        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in data:
                row[0] = datetime.fromtimestamp(row[0] / 1000).isoformat()
                row[6] = datetime.fromtimestamp(row[6] / 1000).isoformat()
                writer.writerow(row)

class BinancePairCheck():
    def __init__(self):
        # ---------- Load Binance pairs ----------
        binance = requests.get("https://api.binance.com/api/v3/exchangeInfo").json()

        self.all_pairs = {
            s["symbol"]
            for s in binance["symbols"]
            if s["status"] == "TRADING"
        }

        # ---------- Load full names from CoinGecko ----------
        coingecko = requests.get(
            "https://api.coingecko.com/api/v3/coins/list"
        ).json()

        # Build lookup: FULL NAME -> SYMBOL
        self.name_to_symbol = {
            c["name"].lower(): c["symbol"].upper()
            for c in coingecko
        }

    def find_best_match(self, name, choices, min_score=70):
        name = name.lower()
        best_match, score = process.extractOne(name, choices)

        if score < min_score:
            return None  # Not found

        return best_match

    def check_binance_pair(self, coin_a, coin_b):
        # Try to correct names
        name_a = self.find_best_match(coin_a, self.name_to_symbol.keys())
        name_b = self.find_best_match(coin_b, self.name_to_symbol.keys())

        if not name_a or not name_b:
            return f"❌ One or both coins not recognized: {coin_a}, {coin_b}"

        # Convert to tickers
        ticker_a = self.name_to_symbol[name_a]
        ticker_b = self.name_to_symbol[name_b]

        pair1 = ticker_a + ticker_b  # e.g. ETHBTC
        pair2 = ticker_b + ticker_a  # e.g. BTCETH

        if pair1 in self.all_pairs:
            return pair1
        elif pair2 in self.all_pairs:
            return pair2

        return f"❌ No direct trading pair exists between {ticker_a} and {ticker_b}"


if __name__ == "__main__":
    fetcher = BinanceDataFetcher()
    data = fetcher.get_klines('BTCUSDT')
    fetcher.save_to_csv(data)

    pairer = BinancePairCheck()
    print(pairer.check_binance_pair("ethereum", "tether"))
    print(pairer.check_binance_pair("etherium", "bitkoin"))
