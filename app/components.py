import pandas as pd
import plotly.express as px
import streamlit as st

from app.utils import format_money, format_ratio


def company_header(profile: dict, ticker: str):
    """Render company name and metadata."""

    name = profile.get("name", ticker)

    st.header(name)

    metadata = []

    if profile.get("ticker"):
        metadata.append(profile["ticker"])

    if profile.get("sector"):
        metadata.append(profile["sector"])

    if profile.get("industry"):
        metadata.append(profile["industry"])

    if profile.get("country"):
        metadata.append(profile["country"])

    if metadata:
        st.caption(" • ".join(metadata))


def market_overview(market: dict, currency: str = "USD"):
    """Render primary market metrics."""

    st.subheader("Market Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Current Price",
            format_money(
                market.get("current_price"),
                currency,
            ),
        )

    with c2:
        st.metric(
            "Market Cap",
            format_money(
                market.get("market_cap"),
                currency,
            ),
        )

    with c3:
        st.metric(
            "Trailing P/E",
            format_ratio(
                market.get("trailing_pe")
            ),
        )

    with c4:
        st.metric(
            "EPS",
            format_money(
                market.get("eps"),
                currency,
            ),
        )


def additional_metrics(market: dict, currency: str = "USD"):
    """Render secondary market metrics."""

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "52W High",
            format_money(
                market.get("fifty_two_week_high"),
                currency,
            ),
        )

    with c2:
        st.metric(
            "52W Low",
            format_money(
                market.get("fifty_two_week_low"),
                currency,
            ),
        )

    with c3:
        dividend = market.get("dividend_yield")

        dividend_display = (
            "N/A"
            if dividend is None
            else f"{float(dividend):.2f}%"
        )

        st.metric(
            "Dividend Yield",
            dividend_display,
        )

    with c4:
        beta = market.get("beta")

        st.metric(
            "Beta",
            "N/A"
            if beta is None
            else f"{float(beta):.2f}",
        )


def company_summary(summary: str):
    """Render company description in a collapsible section."""

    if not summary:
        return

    st.subheader("About the Company")

    with st.expander(
        "Company Overview",
        expanded=False,
    ):
        st.write(summary)


def price_history_chart(history: pd.DataFrame):
    """Render one-year closing price history."""

    if history is None or history.empty:
        return

    if "close" not in history.columns:
        return

    st.subheader("Price History")

    chart_data = history.copy()

    if "date" in chart_data.columns:
        chart_data["date"] = (
            chart_data["date"].astype(str)
        )

    fig = px.line(
        chart_data,
        x="date",
        y="close",
        title="Closing Price — 1 Year",
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Price",
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


def statement_summary(
    df: pd.DataFrame,
    title: str,
    metrics: list[tuple[str, list[str]]],
    currency: str = "USD",
):
    """Render a compact latest-year financial statement summary."""

    if df is None or df.empty:
        return

    st.write(f"### {title}")

    latest = df.iloc[0]

    rows = []

    for display_name, possible_columns in metrics:
        value = None

        for column in possible_columns:
            if column in latest.index:
                value = latest[column]
                break

        rows.append(
            {
                "Metric": display_name,
                "Latest FY": format_money(
                    value,
                    currency,
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


def financial_statement_tables(
    company: dict,
    currency: str = "USD",
):
    balance_sheet = company.get("balance_sheet")
    income_statement = company.get("income_statement")
    cash_flow = company.get("cash_flow")

    balance_metrics = [
        ("Cash & Cash Equivalents", ["Cash And Cash Equivalents", "Cash Financial"]),
        ("Total Assets", ["Total Assets"]),
        ("Total Liabilities", ["Total Liabilities Net Minority Interest"]),
        ("Shareholders' Equity", ["Common Stock Equity", "Total Equity Gross Minority Interest"]),
        ("Working Capital", ["Working Capital"]),
    ]

    income_metrics = [
        ("Revenue", ["Operating Revenue", "Total Revenue"]),
        ("Operating Income", ["Operating Income"]),
        ("Net Income", ["Net Income Common Stockholders", "Net Income"]),
        ("Diluted EPS", ["Diluted EPS", "Basic EPS"]),
    ]

    cashflow_metrics = [
        ("Operating Cash Flow", ["Operating Cash Flow"]),
        ("Capital Expenditure", ["Capital Expenditure"]),
        ("Free Cash Flow", ["Free Cash Flow"]),
        ("Ending Cash", ["End Cash Position"]),
    ]

    if balance_sheet is not None and not balance_sheet.empty:
        statement_summary(
            balance_sheet,
            "Balance Sheet — Latest FY",
            balance_metrics,
            currency,
        )

        with st.expander("View Full Balance Sheet"):
            st.dataframe(
                balance_sheet,
                use_container_width=True,
                hide_index=True,
                height=260,
            )

    if income_statement is not None and not income_statement.empty:
        statement_summary(
            income_statement,
            "Income Statement — Latest FY",
            income_metrics,
            currency,
        )

        with st.expander("View Full Income Statement"):
            st.dataframe(
                income_statement,
                use_container_width=True,
                hide_index=True,
                height=260,
            )

    if cash_flow is not None and not cash_flow.empty:
        statement_summary(
            cash_flow,
            "Cash Flow — Latest FY",
            cashflow_metrics,
            currency,
        )

        with st.expander("View Full Cash Flow"):
            st.dataframe(
                cash_flow,
                use_container_width=True,
                hide_index=True,
                height=260,
            )


def financial_health(summary: dict):
    """Render financial health metrics for uploaded statements."""

    health_score = summary.get("health_score")
    ratios = summary.get("ratios", {})
    totals = summary.get("totals", {})

    st.subheader("Financial Health")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Health Score",
            (
                "N/A"
                if health_score is None
                else f"{health_score}/100"
            ),
        )

    with c2:
        st.metric(
            "Assessment",
            (
                "N/A"
                if health_score is None
                else summary.get(
                    "health_label",
                    "Unknown",
                )
            ),
        )

    st.subheader("Core Financials")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Assets",
            format_money(
                totals.get("total_assets")
            ),
        )

    with c2:
        st.metric(
            "Total Liabilities",
            format_money(
                totals.get("total_liabilities")
            ),
        )

    with c3:
        st.metric(
            "Shareholders' Equity",
            format_money(
                totals.get("shareholders_equity")
            ),
        )

    with c4:
        st.metric(
            "Working Capital",
            format_money(
                totals.get("working_capital")
            ),
        )

    st.subheader("Financial Ratios")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Current Ratio",
            format_ratio(
                ratios.get("current_ratio")
            ),
        )

    with c2:
        st.metric(
            "Debt-to-Equity",
            format_ratio(
                ratios.get("debt_to_equity")
            ),
        )

    with c3:
        st.metric(
            "Cash Ratio",
            format_ratio(
                ratios.get("cash_ratio")
            ),
        )

    with c4:
        st.metric(
            "Equity Ratio",
            format_ratio(
                ratios.get("equity_ratio")
            ),
        )


def parsed_statement(df: pd.DataFrame):
    """Render parsed financial statement data."""

    if df is None or df.empty:
        return

    with st.expander(
        "View Parsed Financial Statement",
        expanded=False,
    ):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


def chat_message(role: str, content: str):
    """Render one chat message."""

    with st.chat_message(role):
        st.markdown(content)