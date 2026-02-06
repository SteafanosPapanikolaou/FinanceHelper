import requests
import csv
from datetime import datetime


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


if __name__ == "__main__":
    fetcher = BinanceDataFetcher()
    data = fetcher.get_klines('BTCUSDT')
    fetcher.save_to_csv(data)
