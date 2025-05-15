import yfinance as yf
import pandas as pd
from utils import get_sp500_tickers

# List of example tickers (can load from file later)
TICKERS7 = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']

TICKERS = get_sp500_tickers()[:100]

# Factors we care about
FIELDS = {
    'trailingPE': 'P/E',
    'priceToBook': 'P/B',
    'returnOnEquity': 'ROE',
    'debtToEquity': 'D/E',
    'earningsGrowth': 'EPS Growth',
    'marketCap': 'Market Cap'
}


def fetch_fundamentals(tickers):
    all_data = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            row = {'Ticker': ticker}
            for field in FIELDS:
                row[FIELDS[field]] = info.get(field, None)
            all_data.append(row)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return pd.DataFrame(all_data)


def screen_stocks(df):
    # Drop rows with missing data
    df = df.dropna(subset=['P/E', 'P/B', 'ROE', 'D/E', 'EPS Growth'])

    # Optional: Apply hard filters (customize as needed)
    print("Before filter", df.shape)
    df = df[
        (df['P/E'] < 25) &
        (df['ROE'] > 0.10) &
        (df['D/E'] < 100.0)
    ]

    # Normalize factors (Z-score or min-max for simplicity)
    for col in ['P/E', 'P/B', 'ROE', 'EPS Growth']:
        if col in df.columns:
            df[col + '_score'] = (df[col] - df[col].min()) / \
                (df[col].max() - df[col].min())

    # Scoring: higher ROE and EPS growth is better; lower P/E and P/B is better
    df['Factor Score'] = (
        (1 - df['P/E_score']) +
        (1 - df['P/B_score']) +
        df['ROE_score'] +
        df['EPS Growth_score']
    )

    df = df.sort_values(by='Factor Score', ascending=False)

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/fundamentals_snapshot.csv")
    df_clean = screen_stocks(df)
    print(df_clean[['Ticker', 'P/E', 'ROE',
          'EPS Growth', 'Factor Score']].head(10))
    df_clean.to_csv("data/screened_stocks.csv", index=False)
