import os

import plotly.express as px
import streamlit as st

from app.ticker import fetch_company_context
from app.parser import load_financial_statement
from app.finance import generate_summary, get_health_label
from app.chat import answer_company_question
from app.ollama_client import answer_with_ollama
from app.components import (
    company_header,
    market_overview,
    additional_metrics,
    company_summary,
    price_history_chart,
    financial_statement_tables,
    financial_health,
    parsed_statement,
)


# ---------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="MoneyMap AI: ReImagined",
    page_icon="🌩️",
    layout="wide",
)


# ---------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------

if "ticker_context" not in st.session_state:
    st.session_state.ticker_context = None

if "ticker_symbol" not in st.session_state:
    st.session_state.ticker_symbol = None

if "finance_summary" not in st.session_state:
    st.session_state.finance_summary = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Gemini Flash Lite"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def reset_chat():
    st.session_state.chat_history = []


def current_financial_context():
    return {
        "company_context": st.session_state.ticker_context,
        "finance_summary": st.session_state.finance_summary,
    }


def ask_ai(
    question: str,
    selected_model: str,
    ollama_model: str,
):
    context = current_financial_context()

    if selected_model == "Gemini Flash Lite":
        return answer_company_question(
            company_context=context["company_context"] or {},
            finance_summary=context["finance_summary"],
            user_question=question,
            advanced=False,
        )

    if selected_model == "Gemini Flash":
        return answer_company_question(
            company_context=context["company_context"] or {},
            finance_summary=context["finance_summary"],
            user_question=question,
            advanced=True,
        )

    return answer_with_ollama(
        user_question=question,
        company_context=context["company_context"],
        finance_summary=context["finance_summary"],
        model_name=ollama_model,
    )


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("🌩️ MoneyMap AI: ReImagined")
st.caption("AI-Powered Financial Copilot")


# ---------------------------------------------------------------------
# Main Layout
# ---------------------------------------------------------------------

left, right = st.columns(
    [3.3, 1.7],
    gap="large",
)


# =====================================================================
# LEFT SIDE — FINANCIAL WORKSPACE
# =====================================================================

with left:

    mode = st.radio(
        "Choose analysis mode",
        [
            "📈 Analyze by Ticker",
            "📄 Upload Financial Statement",
        ],
        horizontal=True,
    )

    # ================================================================
    # TICKER MODE
    # ================================================================

    if mode == "📈 Analyze by Ticker":

        st.subheader("Analyze a Stock")

        col1, col2 = st.columns([4, 1])

        with col1:
            ticker_input = st.text_input(
                "Enter a ticker symbol",
                placeholder="For Ticker info use any stock symbol like AAPL, MSFT, NVDA, etc. Indian Tickers should be followed by .NS",
            )

        with col2:
            st.write("")
            st.write("")

            analyze_clicked = st.button(
                "Analyze",
                use_container_width=True,
                type="primary",
            )

        if analyze_clicked:

            if not ticker_input.strip():
                st.warning("Please enter a ticker symbol.")

            else:
                try:
                    ticker = ticker_input.strip().upper()

                    with st.spinner(
                        f"Fetching data for {ticker}..."
                    ):
                        context = fetch_company_context(
                            ticker
                        )

                    st.session_state.ticker_context = context
                    st.session_state.ticker_symbol = ticker
                    st.session_state.finance_summary = None
                    st.session_state.uploaded_file_name = None

                    reset_chat()

                    st.success(
                        f"{ticker} loaded successfully."
                    )

                except Exception as e:
                    st.session_state.ticker_context = None
                    st.session_state.ticker_symbol = None

                    st.error(
                        f"Unable to analyze ticker: {e}"
                    )

        company = st.session_state.ticker_context

        if company:

            profile = company.get(
                "profile",
                {},
            )

            market = company.get(
                "market",
                {},
            )

            history = company.get(
                "price_history"
            )

            currency = profile.get(
                "currency",
                "USD",
            )

            st.divider()

            company_header(
                profile,
                st.session_state.ticker_symbol,
            )

            st.divider()

            market_overview(
                market,
                currency,
            )

            additional_metrics(
                market,
                currency,
            )

            company_summary(
                profile.get("summary")
            )

            price_history_chart(
                history
            )

            financial_statement_tables(
                company,
                currency,
            )

    # ================================================================
    # UPLOAD MODE
    # ================================================================

    else:

        st.subheader(
            "Analyze a Financial Statement"
        )

        uploaded_file = st.file_uploader(
            "Upload a financial statement",
            type=[
                "csv",
                "xlsx",
                "xls",
                "pdf",
            ],
        )

        if uploaded_file:

            try:
                file_changed = (
                    st.session_state.uploaded_file_name
                    != uploaded_file.name
                )

                if file_changed:

                    st.session_state.uploaded_file_name = (
                        uploaded_file.name
                    )

                    st.session_state.ticker_context = None
                    st.session_state.ticker_symbol = None
                    st.session_state.finance_summary = None

                    reset_chat()

                df = load_financial_statement(
                    uploaded_file
                )

                summary = generate_summary(df)

                display_summary = dict(summary)

                display_summary["health_label"] = (
                    get_health_label(
                        summary["health_score"]
                    )
                )

                st.session_state.finance_summary = summary

                st.success(
                    "Financial statement parsed successfully!"
                )

                st.info(
                    f"📄 **File:** {uploaded_file.name}"
                )

                financial_health(
                    display_summary
                )

                parsed_statement(
                    summary["categorized_data"]
                )

            except Exception as e:

                st.error(
                    f"Analysis Error: {e}"
                )

        else:

            st.info(
                "Upload a CSV, XLSX, XLS, or PDF "
                "financial statement to begin."
            )


# =====================================================================
# RIGHT SIDE — PERMANENT AI COPILOT
# =====================================================================

with right:

    st.subheader("💬 Ask MoneyMap AI")

    model_options = [
        "Gemini Flash Lite",
        "Gemini Flash",
        "Local AI (Ollama)",
    ]

    current_model_index = model_options.index(
        st.session_state.selected_model
    )

    st.session_state.selected_model = st.selectbox(
        "AI Model",
        model_options,
        index=current_model_index,
    )

    ollama_model = os.getenv(
        "OLLAMA_MODEL",
        "llama3", #Replace with your preferred default model
    )

    if (
        st.session_state.selected_model
        == "Local AI (Ollama)"
    ):
        ollama_model = st.text_input(
            "Local model",
            value=ollama_model,
            placeholder="e.g. llama3.2, mistral, phi3",
        )

        st.caption(
            "Runs locally through Ollama."
        )


    # -----------------------------------------------------------------
    # Active Context
    # -----------------------------------------------------------------

    if st.session_state.ticker_context:

        context_label = (
            f"📈 {st.session_state.ticker_symbol}"
        )

    elif st.session_state.finance_summary:

        context_label = (
            f"📄 {st.session_state.uploaded_file_name}"
        )

    else:

        context_label = (
            "No financial data loaded"
        )

    st.caption(
        f"Context: {context_label}"
    )


    # -----------------------------------------------------------------
    # Chat Controls
    # -----------------------------------------------------------------

    if st.button(
        "Clear Chat",
        use_container_width=True,
    ):
        reset_chat()
        st.rerun()

    st.divider()


    # -----------------------------------------------------------------
    # Chat History
    # -----------------------------------------------------------------

    chat_container = st.container(
        height=500,
        border=False,
    )

    with chat_container:

        if not st.session_state.chat_history:

            st.info(
                "Load a ticker or financial statement, "
                "then ask MoneyMap AI a question."
            )

        for message in st.session_state.chat_history:

            with st.chat_message(
                message["role"]
            ):
                st.markdown(
                    message["content"]
                )


    # -----------------------------------------------------------------
    # Chat Input
    # -----------------------------------------------------------------

    question = st.chat_input(
        "Ask MoneyMap AI..."
    )

    if question:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.spinner(
            f"Thinking with "
            f"{st.session_state.selected_model}..."
        ):

            answer = ask_ai(
                question=question,
                selected_model=(
                    st.session_state.selected_model
                ),
                ollama_model=ollama_model,
            )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.rerun()