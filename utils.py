# utils.py

import pandas as pd


def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    sp500_table = tables[0]
    tickers = sp500_table['Symbol'].tolist()
    # Fix tickers with "." (e.g., BRK.B → BRK-B for yfinance)
    tickers = [t.replace('.', '-') for t in tickers]
    return tickers
