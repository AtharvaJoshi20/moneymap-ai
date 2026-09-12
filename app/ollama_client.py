import json
import os
from urllib import request, error


OLLAMA_URL = "http://localhost:11434/api/generate"


def answer_with_ollama(
    user_question,
    company_context=None,
    finance_summary=None,
    model_name=None,
):
    """Generate a local AI response through Ollama."""

    if model_name is None:
        model_name = os.getenv(
            "OLLAMA_MODEL",
            "llama3.2",
        )

    sections = []

    if company_context:
        profile = company_context.get("profile", {})
        market = company_context.get("market", {})

        sections.append(
            f"""
Company Information
-------------------
Name: {profile.get("name", "Unknown")}
Ticker: {profile.get("ticker", "Unknown")}
Sector: {profile.get("sector", "Unknown")}
Industry: {profile.get("industry", "Unknown")}
Country: {profile.get("country", "Unknown")}

Market Information
------------------
Current Price: {market.get("current_price", "N/A")}
Market Cap: {market.get("market_cap", "N/A")}
Trailing P/E: {market.get("trailing_pe", "N/A")}
Forward P/E: {market.get("forward_pe", "N/A")}
EPS: {market.get("eps", "N/A")}
Dividend Yield: {market.get("dividend_yield", "N/A")}
52 Week High: {market.get("fifty_two_week_high", "N/A")}
52 Week Low: {market.get("fifty_two_week_low", "N/A")}
Beta: {market.get("beta", "N/A")}
""".strip()
        )

    if finance_summary:
        totals = finance_summary.get("totals", {})
        ratios = finance_summary.get("ratios", {})

        sections.append(
            f"""
Financial Health
----------------
Health Score: {finance_summary.get("health_score", "N/A")}/100

Total Assets: {totals.get("total_assets", "N/A")}
Total Liabilities: {totals.get("total_liabilities", "N/A")}
Shareholders' Equity: {totals.get("shareholders_equity", "N/A")}
Working Capital: {totals.get("working_capital", "N/A")}

Current Ratio: {ratios.get("current_ratio", "N/A")}
Debt-to-Equity: {ratios.get("debt_to_equity", "N/A")}
Cash Ratio: {ratios.get("cash_ratio", "N/A")}
Equity Ratio: {ratios.get("equity_ratio", "N/A")}
""".strip()
        )

    context = (
        "\n\n".join(sections)
        if sections
        else "No financial context is currently available."
    )

    prompt = f"""
You are MoneyMap AI, an AI Financial Analyst.

Rules:
- Answer only the user's question.
- Do not introduce yourself.
- Use only the provided financial information.
- Never invent financial metrics, events, or facts.
- If information is missing, say:
  "Not available in the provided company data."
- Keep the answer concise, educational, and clear.
- Use Markdown where useful.

========================
FINANCIAL CONTEXT
========================

{context}

========================
USER QUESTION
========================

{user_question}
""".strip()

    payload = json.dumps(
        {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")

    req = request.Request(
        OLLAMA_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=120) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        answer = data.get("response", "").strip()

        if not answer:
            return "Ollama returned an empty response."

        return answer

    except error.URLError:
        return (
            "Local AI Error: Ollama is not running.\n\n"
            "Start Ollama and make sure the selected model is available."
        )

    except Exception as e:
        return f"Local AI Error: {e}"