from app.llm_client import (
    get_gemini_client,
    get_model_name,
    get_advanced_model,
)

# ---------------------------------------------------------------------
# Prompt Builders
# ---------------------------------------------------------------------

def build_company_context(company: dict) -> str:
    """
    Compress ticker/company context into a lightweight prompt.
    Only essential company and market information is sent to Gemini.
    """

    profile = company.get("profile", {})
    market = company.get("market", {})

    return f"""
Company Name: {profile.get("name", "Unknown")}
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
52 Week High: {market.get("high_52_week", "N/A")}
52 Week Low: {market.get("low_52_week", "N/A")}
Beta: {market.get("beta", "N/A")}
""".strip()


def build_finance_context(summary: dict) -> str:
    """
    Compress Finance Engine output into a lightweight prompt.
    """

    totals = summary.get("totals", {})
    ratios = summary.get("ratios", {})

    return f"""
Financial Health
----------------
Health Score: {summary.get("health_score", "N/A")}/100

Core Financials
---------------
Total Assets: {totals.get("total_assets", "N/A")}
Total Liabilities: {totals.get("total_liabilities", "N/A")}
Shareholders' Equity: {totals.get("shareholders_equity", "N/A")}
Working Capital: {totals.get("working_capital", "N/A")}

Key Ratios
----------
Current Ratio: {ratios.get("current_ratio", "N/A")}
Debt-to-Equity: {ratios.get("debt_to_equity", "N/A")}
Cash Ratio: {ratios.get("cash_ratio", "N/A")}
Equity Ratio: {ratios.get("equity_ratio", "N/A")}
""".strip()


# ---------------------------------------------------------------------
# Main Chat Function
# ---------------------------------------------------------------------

def answer_company_question(
    company_context: dict,
    user_question: str,
    finance_summary: dict | None = None,
    advanced: bool = False,
) -> str:
    """
    MoneyMap AI Financial Chatbot.

    Parameters
    ----------
    company_context : dict
        Output from fetch_company_context().

    user_question : str
        User's question.

    finance_summary : dict | None
        Output from generate_summary(). Optional for ticker-only mode.

    advanced : bool
        True → Gemini 3.5 Flash
        False → Gemini 3.5 Flash Lite
    """

    client = get_gemini_client()
    model = get_advanced_model() if advanced else get_model_name()

    prompt = f"""
You are MoneyMap AI, an AI Financial Analyst.

Rules:
- You are MoneyMap AI.
- Do NOT introduce yourself.
- Answer ONLY the user's question.
- Use ONLY the provided financial information.
- Never invent metrics or events.
- If information is missing, say "Not available in the provided company data."
- Use concise markdown with bullet points when helpful.

========================
COMPANY CONTEXT
========================

{build_company_context(company_context)}
"""

    if finance_summary is not None:
        prompt += f"""

========================
LOCAL FINANCE ENGINE OUTPUT
========================

{build_finance_context(finance_summary)}
"""

    prompt += f"""

========================
USER QUESTION
========================

{user_question}
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text.strip()

    except Exception as e:
        return f"MoneyMap AI Error: {e}"