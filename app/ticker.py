from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


# -------------------------------------------------------------------
# Core Validation
# -------------------------------------------------------------------

def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize a stock ticker.
    Returns an uppercase ticker string.
    """
    if not ticker or not ticker.strip():
        raise ValueError("Ticker symbol cannot be empty.")

    ticker = ticker.strip().upper()

    stock = yf.Ticker(ticker)

    try:
        info = stock.info
    except Exception:
        raise ValueError(f"Unable to fetch data for ticker '{ticker}'.")

    if not info or "symbol" not in info:
        raise ValueError(f"Invalid ticker symbol: {ticker}")

    return ticker


# -------------------------------------------------------------------
# Company Profile
# -------------------------------------------------------------------

def get_company_profile(ticker: str) -> dict:
    """
    Fetch general company information.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "ticker": ticker,
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "website": info.get("website"),
        "employees": info.get("fullTimeEmployees"),
        "summary": info.get("longBusinessSummary"),
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
    }


# -------------------------------------------------------------------
# Market Metrics
# -------------------------------------------------------------------

def get_market_metrics(ticker: str) -> dict:
    """
    Fetch live market metrics.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "current_price": info.get("currentPrice"),
        "previous_close": info.get("previousClose"),
        "open": info.get("open"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "market_cap": info.get("marketCap"),
        "volume": info.get("volume"),
        "average_volume": info.get("averageVolume"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "beta": info.get("beta"),
        "dividend_yield": info.get("dividendYield"),
    }


# -------------------------------------------------------------------
# Financial Statements
# -------------------------------------------------------------------

def get_balance_sheet(ticker: str) -> pd.DataFrame:
    """
    Latest balance sheet.
    """
    stock = yf.Ticker(ticker)

    df = stock.balance_sheet.T.reset_index()

    if df.empty:
        raise ValueError("Balance sheet unavailable.")

    df = df.rename(columns={"index": "date"})
    return df


def get_income_statement(ticker: str) -> pd.DataFrame:
    """
    Latest income statement.
    """
    stock = yf.Ticker(ticker)

    df = stock.financials.T.reset_index()

    if df.empty:
        raise ValueError("Income statement unavailable.")

    df = df.rename(columns={"index": "date"})
    return df


def get_cash_flow(ticker: str) -> pd.DataFrame:
    """
    Latest cash flow statement.
    """
    stock = yf.Ticker(ticker)

    df = stock.cashflow.T.reset_index()

    if df.empty:
        raise ValueError("Cash flow statement unavailable.")

    df = df.rename(columns={"index": "date"})
    return df


# -------------------------------------------------------------------
# Historical Price Data
# -------------------------------------------------------------------

def get_price_history(
    ticker: str,
    period: str = "1y",
) -> pd.DataFrame:
    """
    Fetch historical stock prices.

    Supported periods:
    1mo, 3mo, 6mo, 1y, 2y, 5y, max
    """
    stock = yf.Ticker(ticker)

    history = stock.history(period=period)

    if history.empty:
        raise ValueError("Historical price data unavailable.")

    history = history.reset_index()

    history.columns = [col.lower() for col in history.columns]

    history["date"] = history["date"].dt.tz_localize(None)

    return history


# -------------------------------------------------------------------
# Complete Company Context
# -------------------------------------------------------------------

def fetch_company_context(ticker: str) -> dict:
    """
    Fetch all financial context for MoneyMap AI.
    This dictionary becomes the context object for
    Finance Engine, Charts, and Gemini Chatbot.
    """
    ticker = validate_ticker(ticker)

    return {
        "profile": get_company_profile(ticker),
        "market": get_market_metrics(ticker),
        "balance_sheet": get_balance_sheet(ticker),
        "income_statement": get_income_statement(ticker),
        "cash_flow": get_cash_flow(ticker),
        "price_history": get_price_history(ticker),
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
    }