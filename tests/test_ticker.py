from app.ticker import fetch_company_context

# Change ticker here for testing
ticker = "IRCTC.NS"  # Example: Apple Inc. (AAPL), Microsoft Corp. (MSFT), Tesla Inc. (TSLA)

company = fetch_company_context(ticker)

print("=" * 60)
print("COMPANY PROFILE")
print("=" * 60)
print(company["profile"]["name"])
print(company["profile"]["sector"])
print(company["profile"]["industry"])
print(company["profile"]["country"])

print("\n" + "=" * 60)
print("MARKET DATA")
print("=" * 60)
print("Price:", company["market"]["current_price"])
print("Market Cap:", company["market"]["market_cap"])
print("P/E:", company["market"]["trailing_pe"])
print("52W High:", company["market"]["fifty_two_week_high"])

print("\n" + "=" * 60)
print("BALANCE SHEET")
print("=" * 60)
print(company["balance_sheet"].head())

print("\n" + "=" * 60)
print("INCOME STATEMENT")
print("=" * 60)
print(company["income_statement"].head())

print("\n" + "=" * 60)
print("CASH FLOW")
print("=" * 60)
print(company["cash_flow"].head())

print("\n" + "=" * 60)
print("PRICE HISTORY")
print("=" * 60)
print(company["price_history"][["date", "close"]].tail())