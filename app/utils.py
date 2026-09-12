import json
import streamlit as st


def format_money(value, currency="USD"):
    """Format financial values into readable units."""

    if value is None:
        return "N/A"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "N/A"

    symbols = {
        "USD": "$",
        "INR": "₹",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = symbols.get(str(currency).upper(), "")
    absolute = abs(value)

    if absolute >= 1_000_000_000_000:
        return f"{symbol}{value / 1_000_000_000_000:.2f}T"

    if absolute >= 1_000_000_000:
        return f"{symbol}{value / 1_000_000_000:.2f}B"

    if absolute >= 1_000_000:
        return f"{symbol}{value / 1_000_000:.2f}M"

    if absolute >= 1_000:
        return f"{symbol}{value / 1_000:.2f}K"

    return f"{symbol}{value:,.2f}"


def format_ratio(value):
    """Format ratio values."""

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "N/A"


def safe_metric(value, formatter=str):
    """Return a formatted metric or N/A."""

    if value is None:
        return "N/A"

    try:
        return formatter(value)
    except (TypeError, ValueError):
        return "N/A"


def reset_chat():
    """Clear stored chat messages."""

    st.session_state.chat_history = []


def get_latest_statement_row(df):
    """Return the latest available row from a financial statement."""

    if df is None or df.empty:
        return None

    return df.iloc[0]


def find_value(row, *column_names):
    """Find the first available value from a statement row."""

    if row is None:
        return None

    for column in column_names:
        if column in row.index:
            value = row[column]

            if value is not None:
                try:
                    if value != value:
                        continue
                except Exception:
                    pass

                return value

    return None