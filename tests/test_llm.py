from app.ticker import fetch_company_context
from app.llm_client import get_gemini_client, get_model_name

company = fetch_company_context("NVDA")

prompt = f"""
You are MoneyMap AI, an expert financial analyst.

Company Profile:
{company.get("profile", {})}

Market Data:
{company.get("market", {})}

Question:
Is NVIDIA financially healthy? Explain in under 150 words.
"""

client = get_gemini_client()

response = client.models.generate_content(
    model=get_model_name(),
    contents=prompt
)

print(response.text)