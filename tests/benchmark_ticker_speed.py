import time
import statistics

from app.ticker import fetch_company_context

TICKERS = {
    # 🇺🇸 United States
    "NVDA":"NVIDIA",
    "AAPL":"Apple",
    "MSFT":"Microsoft",
    "AMZN":"Amazon",
    "GOOGL":"Alphabet",
    "META":"Meta",
    "TSLA":"Tesla",
    "BRK-B":"Berkshire Hathaway",
    "JPM":"JPMorgan Chase",
    "WMT":"Walmart",
    "AMD":"AMD",
    "NFLX":"Netflix",
    "COST":"Costco",
    "UNH":"UnitedHealth",
    "KO":"Coca-Cola",

    # 🇮🇳 India
    "RELIANCE.NS":"Reliance Industries",
    "TCS.NS":"Tata Consultancy Services",
    "INFY.NS":"Infosys",
    "HDFCBANK.NS":"HDFC Bank",
    "ICICIBANK.NS":"ICICI Bank",
    "SBIN.NS":"State Bank of India",
    "IRCTC.NS":"IRCTC",
    "LT.NS":"Larsen & Toubro",
    "SUNPHARMA.NS":"Sun Pharma",
    "BHARTIARTL.NS":"Bharti Airtel",

    # 🇯🇵 Japan
    "TM":"Toyota",
    "SONY":"Sony Group",
    "7203.T":"Toyota (Tokyo Listing)",
    "6758.T":"Sony (Tokyo Listing)",

    # 🇰🇷 South Korea
    "005930.KS":"Samsung Electronics",
    "000660.KS":"SK Hynix",

    # 🇨🇳 China / Hong Kong
    "BABA":"Alibaba",
    "0700.HK":"Tencent",
    "9988.HK":"Alibaba HK",

    # 🇹🇼 Taiwan
    "TSM":"TSMC",

    # 🇳🇱 Netherlands
    "ASML":"ASML Holding",

    # 🇩🇰 Denmark
    "NVO":"Novo Nordisk",

    # 🇬🇧 United Kingdom
    "SHEL":"Shell",
    "AZN":"AstraZeneca",
    "UL":"Unilever ADR",

    # 🇫🇷 France
    "MC.PA":"LVMH",
    "AIR.PA":"Airbus",

    # 🇩🇪 Germany
    "SIEGY":"Siemens ADR",
    "SAP":"SAP",

    # 🇨🇭 Switzerland
    "NESN.SW":"Nestlé",

    # 🇸🇦 Saudi Arabia
    "2222.SR":"Saudi Aramco",

    # 🇦🇺 Australia
    "BHP.AX":"BHP Group",

    # 🇨🇦 Canada
    "SHOP":"Shopify",

    # 🇸🇪 Sweden
    "ERIC":"Ericsson",

    # 🇧🇷 Brazil
    "PBR":"Petrobras",
}

results = []
success = 0

print("="*80)
print("MONEYMAP AI REIMAGINED — GLOBAL 50 COMPANY BENCHMARK")
print("="*80)

for ticker, company in TICKERS.items():
    start = time.perf_counter()

    try:
        fetch_company_context(ticker)

        elapsed = time.perf_counter() - start
        results.append((ticker, company, elapsed))
        success += 1

        print(f"✅ {ticker:<15} {elapsed:5.2f}s   {company}")

    except Exception as e:
        results.append((ticker, company, None))
        print(f"❌ {ticker:<15} FAILED — {e}")

times = [r[2] for r in results if r[2] is not None]

print("\n"+"="*80)
print("SUMMARY")
print("="*80)

print(f"Companies Tested      : {len(TICKERS)}")
print(f"Successful Fetches    : {success}")
print(f"Success Rate          : {success/len(TICKERS)*100:.1f}%")
print(f"Average Fetch Time    : {statistics.mean(times):.2f}s")
print(f"Median Fetch Time     : {statistics.median(times):.2f}s")
print(f"Fastest Fetch         : {min(times):.2f}s")
print(f"Slowest Fetch         : {max(times):.2f}s")

print("\nTop 10 Fastest")
for ticker, company, t in sorted(results, key=lambda x: x[2] if x[2] else 999)[:10]:
    print(f"{ticker:<15} {t:.2f}s   {company}")

print("\nTop 10 Slowest")
for ticker, company, t in sorted(results, key=lambda x: x[2] if x[2] else 0, reverse=True)[:10]:
    if t:
        print(f"{ticker:<15} {t:.2f}s   {company}")