# Stock Portfolio Performance Tracker

A Python console utility that tracks an investment portfolio. Enter stock tickers, buy prices, and share quantities to see total portfolio value and the percentage gain or loss for each holding. Results are logged to a CSV file.

## Features

- Validates tickers against a company dataset (`sample_prices.csv`)
- Fetches live prices with `yfinance` (manual price entry as a fallback)
- Calculates invested capital, current market value, and gain/loss % per holding
- Combines repeated tickers using the weighted average buy price
- Prints a formatted console report
- Saves a transaction summary to `portfolio_summary.csv` using the built-in `csv` module
- Input validation for tickers, prices, and quantities

## Requirements

- Python 3
- `yfinance` (optional, for live prices): `py -m pip install yfinance`

## How to Run

1. Keep `portfolio.py` and `sample_prices.csv` in the same folder.
2. Run:

   py portfolio.py

3. Enter a ticker, buy price, and number of shares for each holding.
4. Type `done` to see the report and generate `portfolio_summary.csv`.

## Sample Output

AAPL  10 shares  Buy 200.00  Current 343.46  Gain 71.73%
MSFT   5 shares  Buy 400.00  Current 529.05  Gain 32.26%
Total invested: 4,000.00 | Market value: 6,079.85 | Gain: +52.00%

## Concepts Used

- Dictionaries for portfolio storage
- File I/O and the `csv` module
- Working with an external library (`yfinance`)
- Functions and modular code
- Error handling and input validation

