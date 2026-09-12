from app.ticker import fetch_company_context
from app.chat import build_company_context

company = fetch_company_context("NVDA")

profile = str(company["profile"])
market = str(company["market"])
balance = company["balance_sheet"].to_string()
income = company["income_statement"].to_string()
cash = company["cash_flow"].to_string()

raw_context = profile + market + balance + income + cash

compressed_context = build_company_context(company)

raw_chars = len(raw_context)
compressed_chars = len(compressed_context)

reduction = (1 - compressed_chars / raw_chars) * 100

print("PROMPT COMPRESSION BENCHMARK\n")

print(f"Raw Context Size        : {raw_chars:,} characters")
print(f"Compressed Context Size : {compressed_chars:,} characters")
print(f"Reduction               : {reduction:.2f}%")