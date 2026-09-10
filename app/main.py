import streamlit as st

from parser import load_financial_statement
from finance import generate_summary, get_health_label


# ---------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="MoneyMap AI: ReImagined",
    page_icon="🌩️",
    layout="wide",
)

st.title("🌩️ MoneyMap AI: ReImagined")
st.caption("AI-Powered Financial Statement Analyzer")


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------

def format_money(value):
    """
    Display financial values correctly whether they're in:
    - Dollars (yFinance Excel)
    - Millions of dollars (SEC PDFs / CSVs)
    """

    if value is None:
        return "N/A"

    value = float(value)

    # SEC statements are generally reported in millions.
    if abs(value) < 1_000_000_000:
        value *= 1_000_000

    if abs(value) >= 1_000_000_000_000:
        return f"${value/1_000_000_000_000:.2f}T"

    if abs(value) >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"

    return f"${value:,.0f}"


def format_ratio(value):
    if value is None:
        return "N/A"
    return f"{value:.2f}"


# ---------------------------------------------------------------------
# File Upload
# ---------------------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a Financial Statement",
    type=["csv", "xlsx", "xls", "pdf"],
)

# ---------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------

if uploaded_file:
    try:
        # Parse uploaded statement
        df = load_financial_statement(uploaded_file)

        st.success("Financial statement parsed successfully!")

        # Simple upload banner (safe version)
        st.info(f"📄 **File:** {uploaded_file.name}")

        # Finance analysis
        summary = generate_summary(df)

        totals = summary["totals"]
        ratios = summary["ratios"]
        health_score = summary["health_score"]

        # -------------------------------------------------------------
        # Financial Health
        # -------------------------------------------------------------

        st.subheader("Financial Health")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Health Score", f"{health_score}/100")

        with col2:
            st.metric("Assessment", get_health_label(health_score))

        st.divider()

        # -------------------------------------------------------------
        # Core Financials
        # -------------------------------------------------------------

        st.subheader("Core Financials")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "💰 Total Assets",
                format_money(totals["total_assets"]),
            )

        with c2:
            st.metric(
                "🏦 Total Liabilities",
                format_money(totals["total_liabilities"]),
            )

        with c3:
            st.metric(
                "📈 Shareholders' Equity",
                format_money(totals["shareholders_equity"]),
            )

        with c4:
            st.metric(
                "💵 Working Capital",
                format_money(totals["working_capital"]),
            )

        st.divider()

        # -------------------------------------------------------------
        # Financial Ratios
        # -------------------------------------------------------------

        st.subheader("Financial Ratios")

        r1, r2, r3, r4 = st.columns(4)

        with r1:
            st.metric(
                "Current Ratio",
                format_ratio(ratios["current_ratio"]),
            )

        with r2:
            st.metric(
                "Debt-to-Equity",
                format_ratio(ratios["debt_to_equity"]),
            )

        with r3:
            st.metric(
                "Cash Ratio",
                format_ratio(ratios["cash_ratio"]),
            )

        with r4:
            st.metric(
                "Equity Ratio",
                format_ratio(ratios["equity_ratio"]),
            )

        st.divider()

        # -------------------------------------------------------------
        # Parsed Financial Statement
        # -------------------------------------------------------------

        st.subheader("Parsed Financial Statement")

        st.dataframe(
            summary["categorized_data"],
            use_container_width=True,
            hide_index=True,
        )

    except Exception as e:
        st.error(f"Finance Engine Error: {e}")

else:
    st.info("Upload a CSV, Excel, or PDF financial statement to begin analysis.")