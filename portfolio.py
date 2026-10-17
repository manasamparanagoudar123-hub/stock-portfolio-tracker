import csv
import os
from datetime import datetime

DATASET_FILE = "sample_prices.csv"     # Datheon dataset (list of companies)
SUMMARY_FILE = "portfolio_summary.csv"


def load_companies(filename):
    """Read Symbol -> Company name from the dataset CSV."""
    companies = {}
    if not os.path.exists(filename):
        print(f"{filename} not found. Any ticker will be accepted.")
        return companies

    with open(filename, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k.strip().lower(): v for k, v in row.items() if k}
            symbol = row.get("symbol") or row.get("ticker")
            name = row.get("security") or row.get("name") or ""
            if symbol:
                companies[symbol.strip().upper()] = name.strip()

    print(f"Loaded {len(companies)} companies from {filename}")
    return companies


def get_live_price(ticker):
    """Try to fetch the latest closing price with yfinance. Returns None on failure."""
    try:
        import yfinance as yf
        data = yf.Ticker(ticker.replace(".", "-")).history(period="5d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception:
        pass
    return None


def read_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if value > 0:
                return value
            print("Value must be greater than 0.")
        except ValueError:
            print("Please enter a valid number.")


def get_current_price(ticker):
    price = get_live_price(ticker)
    if price is not None:
        print(f"Live price for {ticker}: {price:.2f}")
        return price
    print("Could not fetch a live price (yfinance missing or no internet).")
    return read_positive_float(f"Enter current price of {ticker} manually: ")


def is_valid_ticker(ticker):
    return ticker.replace(".", "").replace("-", "").isalpha()


def collect_positions(companies):
    """Ask the user for holdings. Stored as a dictionary of dictionaries."""
    portfolio = {}
    print("\nEnter your holdings. Type 'done' as the ticker when finished.")
    print("Example tickers: AAPL, MSFT, GOOGL, AMZN, TSLA")

    while True:
        ticker = input("\nTicker symbol: ").strip().upper()
        if ticker == "DONE":
            break
        if not is_valid_ticker(ticker):
            print("Please enter a valid ticker (letters only).")
            continue
        if companies and ticker not in companies:
            print(f"{ticker} was not found in the dataset. Try another ticker.")
            continue

        name = companies.get(ticker, "")
        if name:
            print(f"Company: {name}")

        buy_price = read_positive_float("Buy price per share: ")
        quantity = read_positive_float("Number of shares: ")

        if ticker in portfolio:
            # Merge with existing holding using weighted average cost
            old = portfolio[ticker]
            total_qty = old["quantity"] + quantity
            avg_price = (old["buy_price"] * old["quantity"] + buy_price * quantity) / total_qty
            old["buy_price"] = avg_price
            old["quantity"] = total_qty
        else:
            current_price = get_current_price(ticker)
            portfolio[ticker] = {
                "name": name,
                "buy_price": buy_price,
                "quantity": quantity,
                "current_price": current_price,
            }
        print(f"Added {ticker}.")

    return portfolio


def calculate_results(portfolio):
    results = []
    for ticker, pos in portfolio.items():
        invested = pos["buy_price"] * pos["quantity"]
        market_value = pos["current_price"] * pos["quantity"]
        gain = market_value - invested
        gain_pct = (gain / invested) * 100
        results.append({
            "ticker": ticker,
            "name": pos["name"],
            "quantity": pos["quantity"],
            "buy_price": pos["buy_price"],
            "current_price": pos["current_price"],
            "invested": invested,
            "market_value": market_value,
            "gain": gain,
            "gain_pct": gain_pct,
        })
    return results


def print_report(results):
    line = "-" * 88
    print("\n" + "=" * 88)
    print("PORTFOLIO PERFORMANCE REPORT".center(88))
    print("=" * 88)
    print(f"{'Ticker':<8}{'Qty':>8}{'Buy':>12}{'Current':>12}{'Invested':>14}{'Value':>14}{'Gain/Loss %':>14}")
    print(line)
    for r in results:
        print(f"{r['ticker']:<8}{r['quantity']:>8.2f}{r['buy_price']:>12.2f}"
              f"{r['current_price']:>12.2f}{r['invested']:>14.2f}"
              f"{r['market_value']:>14.2f}{r['gain_pct']:>13.2f}%")
    print(line)

    total_invested = sum(r["invested"] for r in results)
    total_value = sum(r["market_value"] for r in results)
    total_gain = total_value - total_invested
    total_pct = (total_gain / total_invested) * 100 if total_invested else 0

    print(f"Total invested capital : {total_invested:,.2f}")
    print(f"Current market value   : {total_value:,.2f}")
    status = "GAIN" if total_gain >= 0 else "LOSS"
    print(f"Overall {status:<14}: {total_gain:,.2f} ({total_pct:+.2f}%)")
    print("=" * 88)
    return total_invested, total_value, total_gain, total_pct


def save_summary(results, totals, filename):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_invested, total_value, total_gain, total_pct = totals

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Ticker", "Company", "Quantity", "Buy Price",
                         "Current Price", "Invested", "Market Value",
                         "Gain/Loss", "Gain/Loss %"])
        for r in results:
            writer.writerow([timestamp, r["ticker"], r["name"], f"{r['quantity']:.2f}",
                             f"{r['buy_price']:.2f}", f"{r['current_price']:.2f}",
                             f"{r['invested']:.2f}", f"{r['market_value']:.2f}",
                             f"{r['gain']:.2f}", f"{r['gain_pct']:.2f}"])
        writer.writerow([timestamp, "TOTAL", "", "", "", "",
                         f"{total_invested:.2f}", f"{total_value:.2f}",
                         f"{total_gain:.2f}", f"{total_pct:.2f}"])
    print(f"\nSummary saved to {filename}")


def main():
    companies = load_companies(DATASET_FILE)
    portfolio = collect_positions(companies)

    if not portfolio:
        print("No holdings entered. Exiting.")
        return

    results = calculate_results(portfolio)
    totals = print_report(results)
    save_summary(results, totals, SUMMARY_FILE)


if __name__ == "__main__":
    main()