import streamlit as st
from parser import load_financial_statement

st.set_page_config(page_title="MoneyMap AI: ReImagined", layout="wide")

st.title("🌩️ MoneyMap AI: ReImagined")
st.caption("Parser Test — Sprint 1")

uploaded_file = st.file_uploader(
    "Upload a Financial Statement",
    type=["csv", "xlsx", "xls", "pdf"]
)

if uploaded_file:
    try:
        df = load_financial_statement(uploaded_file)

        st.success("Financial statement parsed successfully!")
        st.write(f"Rows: {len(df)}")

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Parser Error: {e}")