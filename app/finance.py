import re
from typing import Dict, Any

import pandas as pd


# ---------------------------------------------------------------------------
# Financial vocabulary
# ---------------------------------------------------------------------------

KEYWORDS = {
    "cash": [
        "cash",
        "cash equivalents",
        "cash and cash equivalents",
        "cash, cash equivalents",
        "restricted cash",
        "cash balance",
    ],
    "marketable_securities": [
        "marketable securities",
        "short term investments",
        "short-term investments",
        "short term investment",
        "short-term investment",
    ],
    "receivables": [
        "accounts receivable",
        "account receivable",
        "trade receivables",
        "trade receivable",
        "receivables",
        "vendor non-trade receivables",
        "other receivables",
    ],
    "inventory": [
        "inventory",
        "inventories",
        "stock inventory",
    ],
    "current_assets": [
        "total current assets",
        "current assets",
    ],
    "total_assets": [
        "total assets",
    ],
    "ppe": [
        "property, plant and equipment",
        "property plant and equipment",
        "property and equipment",
        "plant and equipment",
        "ppe",
        "fixed assets",
    ],
    "goodwill": [
        "goodwill",
    ],
    "intangible_assets": [
        "intangible assets",
        "intangible asset",
    ],
    "non_current_assets": [
        "total non-current assets",
        "total non current assets",
        "non-current assets",
        "non current assets",
    ],
    "accounts_payable": [
        "accounts payable",
        "account payable",
        "trade payables",
        "trade payable",
    ],
    "current_liabilities": [
        "total current liabilities",
        "current liabilities",
    ],
    "short_term_debt": [
        "short-term debt",
        "short term debt",
        "current debt",
        "commercial paper",
        "current portion of long-term debt",
        "current portion of long term debt",
    ],
    "long_term_debt": [
        "long-term debt",
        "long term debt",
        "term debt",
        "long-term borrowings",
        "long term borrowings",
    ],
    "total_liabilities": [
        "total liabilities",
    ],
    "non_current_liabilities": [
        "total non-current liabilities",
        "total non current liabilities",
        "non-current liabilities",
        "non current liabilities",
    ],
    "equity": [
        "total shareholders equity",
        "total shareholders' equity",
        "total stockholders equity",
        "total stockholders' equity",
        "shareholders equity",
        "shareholders' equity",
        "stockholders equity",
        "stockholders' equity",
        "common stock and paid-in capital",
        "common stock and paid in capital",
        "share capital",
        "paid-in capital",
        "paid in capital",
    ],
    "retained_earnings": [
        "retained earnings",
        "retained earning",
    ],
    "accumulated_deficit": [
        "accumulated deficit",
    ],
}


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _normalize_text(value: Any) -> str:
    """Normalize financial line-item text for matching."""
    text = str(value or "").lower()

    text = (
        text.replace("&", " and ")
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", "-")
        .replace("\xa0", " ")
    )

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9$%.,'&/\- ]", " ", text)

    return text.strip()


def _contains_any(text: str, keywords: list[str]) -> bool:
    """Return True when any keyword is present in text."""
    normalized = _normalize_text(text)

    return any(
        re.search(rf"\b{re.escape(_normalize_text(keyword))}\b", normalized)
        for keyword in keywords
    )


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the dataframe expected by the finance engine."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    required = {"item", "amount"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Finance engine requires columns: {sorted(required)}. "
            f"Missing: {sorted(missing)}"
        )

    result = df[["item", "amount"]].copy()

    result["item"] = result["item"].astype(str).str.strip()
    result["amount"] = pd.to_numeric(result["amount"], errors="coerce")

    result = result.dropna(subset=["amount"])
    result = result[result["item"].str.len() > 0]
    result = result.reset_index(drop=True)

    return result


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def categorize_item(item: str) -> str:
    """Classify a financial line item into a broad category."""

    text = _normalize_text(item)

    # Most specific / high-priority categories first.
    if _contains_any(text, KEYWORDS["total_assets"]):
        return "total_assets"

    if _contains_any(text, KEYWORDS["total_liabilities"]):
        return "total_liabilities"

    if _contains_any(text, KEYWORDS["equity"]):
        return "equity"

    if _contains_any(text, KEYWORDS["current_assets"]):
        return "current_assets"

    if _contains_any(text, KEYWORDS["current_liabilities"]):
        return "current_liabilities"

    if _contains_any(text, KEYWORDS["non_current_assets"]):
        return "non_current_assets"

    if _contains_any(text, KEYWORDS["non_current_liabilities"]):
        return "non_current_liabilities"

    if _contains_any(text, KEYWORDS["short_term_debt"]):
        return "short_term_debt"

    if _contains_any(text, KEYWORDS["long_term_debt"]):
        return "long_term_debt"

    if _contains_any(text, KEYWORDS["cash"]):
        return "cash"

    if _contains_any(text, KEYWORDS["marketable_securities"]):
        return "marketable_securities"

    if _contains_any(text, KEYWORDS["receivables"]):
        return "receivables"

    if _contains_any(text, KEYWORDS["inventory"]):
        return "inventory"

    if _contains_any(text, KEYWORDS["accounts_payable"]):
        return "accounts_payable"

    if _contains_any(text, KEYWORDS["retained_earnings"]):
        return "retained_earnings"

    if _contains_any(text, KEYWORDS["accumulated_deficit"]):
        return "accumulated_deficit"

    if _contains_any(text, KEYWORDS["ppe"]):
        return "ppe"

    if _contains_any(text, KEYWORDS["goodwill"]):
        return "goodwill"

    if _contains_any(text, KEYWORDS["intangible_assets"]):
        return "intangible_assets"

    return "other"


def categorize_items(df: pd.DataFrame) -> pd.DataFrame:
    """Add a category column to the financial statement."""
    result = _clean_dataframe(df)

    result["category"] = result["item"].apply(categorize_item)

    return result


# ---------------------------------------------------------------------------
# Value extraction
# ---------------------------------------------------------------------------

def _find_value(df: pd.DataFrame, categories: list[str]) -> float:
    """Find the first matching value from the requested categories."""

    for category in categories:
        matches = df[df["category"] == category]

        if not matches.empty:
            return float(matches.iloc[0]["amount"])

    return 0.0


def _find_value_by_text(
    df: pd.DataFrame,
    keywords: list[str],
    exclude_keywords: list[str] | None = None,
) -> float:
    """Find the first matching row by text."""

    exclude_keywords = exclude_keywords or []

    for _, row in df.iterrows():
        item = _normalize_text(row["item"])

        if _contains_any(item, keywords):
            if any(_contains_any(item, [x]) for x in exclude_keywords):
                continue

            return float(row["amount"])

    return 0.0


# ---------------------------------------------------------------------------
# Totals
# ---------------------------------------------------------------------------

def calculate_totals(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate core balance-sheet totals."""

    data = categorize_items(df)

    total_assets = _find_value(data, ["total_assets"])
    total_liabilities = _find_value(data, ["total_liabilities"])
    shareholders_equity = _find_value(data, ["equity"])

    current_assets = _find_value(data, ["current_assets"])
    current_liabilities = _find_value(data, ["current_liabilities"])

    cash = _find_value(data, ["cash"])

    # Include marketable securities as liquid assets when calculating
    # available cash for analysis, but keep raw cash separately.
    marketable_securities = _find_value(data, ["marketable_securities"])

    total_debt = (
        data.loc[
            data["category"].isin(["short_term_debt", "long_term_debt"]),
            "amount",
        ]
        .sum()
    )

    # Prefer reported equity. Fall back to Assets - Liabilities.
    if shareholders_equity == 0 and total_assets and total_liabilities:
        shareholders_equity = total_assets - total_liabilities

    # Prefer liquid cash + marketable securities for cash position.
    liquid_assets = cash + marketable_securities

    working_capital = current_assets - current_liabilities

    return {
        "total_assets": float(total_assets),
        "total_liabilities": float(total_liabilities),
        "shareholders_equity": float(shareholders_equity),
        "current_assets": float(current_assets),
        "current_liabilities": float(current_liabilities),
        "cash": float(cash),
        "marketable_securities": float(marketable_securities),
        "liquid_assets": float(liquid_assets),
        "total_debt": float(total_debt),
        "working_capital": float(working_capital),
    }


# ---------------------------------------------------------------------------
# Financial ratios
# ---------------------------------------------------------------------------

def calculate_ratios(
    totals: Dict[str, float],
) -> Dict[str, float | None]:
    """Calculate core financial ratios."""

    current_assets = totals["current_assets"]
    current_liabilities = totals["current_liabilities"]
    equity = totals["shareholders_equity"]
    debt = totals["total_debt"]
    liquid_assets = totals["liquid_assets"]

    current_ratio = (
        current_assets / current_liabilities
        if current_liabilities
        else None
    )

    debt_to_equity = (
        debt / equity
        if equity
        else None
    )

    cash_ratio = (
        liquid_assets / current_liabilities
        if current_liabilities
        else None
    )

    equity_ratio = (
        equity / totals["total_assets"]
        if totals["total_assets"]
        else None
    )

    return {
        "current_ratio": current_ratio,
        "debt_to_equity": debt_to_equity,
        "cash_ratio": cash_ratio,
        "equity_ratio": equity_ratio,
    }


# ---------------------------------------------------------------------------
# Financial health score
# ---------------------------------------------------------------------------

def calculate_health_score(
    totals: Dict[str, float],
    ratios: Dict[str, float | None],
) -> int:
    """
    Calculate a simple, explainable 0-100 financial health score.
    """

    score = 0

    current_ratio = ratios.get("current_ratio")
    cash_ratio = ratios.get("cash_ratio")
    debt_to_equity = ratios.get("debt_to_equity")

    if current_ratio is not None:
        if current_ratio >= 2.0:
            score += 30
        elif current_ratio >= 1.0:
            score += 20
        elif current_ratio >= 0.75:
            score += 10

    if cash_ratio is not None:
        if cash_ratio >= 0.5:
            score += 25
        elif cash_ratio >= 0.25:
            score += 15
        elif cash_ratio >= 0.10:
            score += 8

    if debt_to_equity is not None:
        if debt_to_equity <= 0.5:
            score += 30
        elif debt_to_equity <= 1.0:
            score += 22
        elif debt_to_equity <= 2.0:
            score += 12
        elif debt_to_equity <= 3.0:
            score += 5

    if totals["shareholders_equity"] > 0:
        score += 15

    return max(0, min(100, int(score)))


# ---------------------------------------------------------------------------
# Full analysis
# ---------------------------------------------------------------------------

def generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate the complete deterministic financial analysis.

    This dictionary becomes the internal contract shared by:
    dashboard -> charts -> LLM -> chat.
    """

    categorized = categorize_items(df)

    totals = calculate_totals(categorized)
    ratios = calculate_ratios(totals)
    health_score = calculate_health_score(totals, ratios)

    return {
        "totals": totals,
        "ratios": ratios,
        "health_score": health_score,
        "categorized_data": categorized,
        "row_count": len(categorized),
    }


# ---------------------------------------------------------------------------
# Human-readable health label
# ---------------------------------------------------------------------------

def get_health_label(score: int) -> str:
    """Convert a numeric health score into a readable label."""

    if score >= 80:
        return "Strong"

    if score >= 60:
        return "Healthy"

    if score >= 40:
        return "Moderate"

    if score >= 20:
        return "Weak"

    return "Critical"


# ---------------------------------------------------------------------------
# Quick local test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "item": [
                "Cash and cash equivalents",
                "Accounts receivable",
                "Inventories",
                "Total current assets",
                "Total assets",
                "Accounts payable",
                "Current portion of long-term debt",
                "Total current liabilities",
                "Long-term debt",
                "Total liabilities",
                "Total shareholders' equity",
            ],
            "amount": [
                35000,
                42000,
                18000,
                120000,
                250000,
                30000,
                5000,
                70000,
                45000,
                115000,
                135000,
            ],
        }
    )

    summary = generate_summary(sample)

    print("Financial Health:", summary["health_score"])
    print("Health Label:", get_health_label(summary["health_score"]))
    print("Totals:", summary["totals"])
    print("Ratios:", summary["ratios"])