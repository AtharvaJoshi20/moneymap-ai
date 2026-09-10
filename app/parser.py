from pathlib import Path
from openpyxl import load_workbook
import pandas as pd
import pdfplumber

def read_csv_file(file) -> pd.DataFrame:
    """
    Read Microsoft/Yahoo style balance sheet CSVs and
    convert them into item/amount format.
    """
    try:
        df = pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        file.seek(0)
        df = pd.read_csv(file, encoding="latin-1")

    # Remove non-breaking spaces
    df.columns = (
        df.columns.astype(str)
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
    )

    # Case 1: Already in item/amount format
    normalized = [c.lower() for c in df.columns]
    if "item" in normalized and "amount" in normalized:
        return df

    # Case 2: Financial export (first column = items, second column = latest year)
    if len(df.columns) >= 2:
        df = df.iloc[:, [0, 1]]
        df.columns = ["item", "amount"]
        return df

    raise ValueError("Unsupported CSV format.")

def read_excel_file(file) -> pd.DataFrame:
    """
    Read Excel financial statements from yFinance and standard layouts.
    Returns a dataframe with item and amount columns.
    """
    wb = load_workbook(file, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    latest_col = 4  # Column E = latest year (1/31/2026)

    records = []

    # yFinance stores value row, then label row.
    for i in range(2, len(rows) - 1, 2):
        value_row = rows[i]
        label_row = rows[i + 1]

        item = label_row[0]
        amount = value_row[latest_col]

        if item and amount is not None:
            records.append({"item": item, "amount": amount})

    return pd.DataFrame(records)

def read_pdf_file(file) -> pd.DataFrame:
    """
    Extract only the Balance Sheet table from a PDF.
    """
    tables = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""

            # Ignore income statement, cash flow, etc.
            if "BALANCE SHEETS" not in text.upper():
                continue

            for table in page.extract_tables():
                if not table or len(table) < 2:
                    continue

                rows = table[1:]  # Skip header

                cleaned = []
                for row in rows:
                    row = [cell.strip() if cell else "" for cell in row]

                    # First column = item, last column = latest amount
                    if len(row) >= 2 and row[0]:
                        cleaned.append([row[0], row[-1]])

                if cleaned:
                    tables.append(pd.DataFrame(cleaned, columns=["item", "amount"]))

    if not tables:
        raise ValueError("No balance sheet found in the uploaded PDF.")

    return pd.concat(tables, ignore_index=True)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names across different financial statements."""

    df.columns = (
        df.columns.astype(str)
        .str.replace("\u00a0", " ", regex=False)   # Remove non-breaking spaces
        .str.strip()
        .str.lower()
    )

    column_map = {
        "item": "item",
        "particulars": "item",
        "account": "item",
        "description": "item",
        "line item": "item",
        "name": "item",

        "amount": "amount",
        "value": "amount",
        "total": "amount",
        "balance": "amount",
        "closing balance": "amount",
    }

    return df.rename(columns=column_map)

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize financial statement data.
    """
    df = normalize_columns(df)

    if "item" not in df.columns or "amount" not in df.columns:
        raise ValueError("Required columns 'item' and 'amount' not found.")

    df = df[["item", "amount"]].copy()

    df["item"] = df["item"].astype(str).str.strip()

    df["amount"] = (
    df["amount"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("$", "", regex=False)
    .str.replace("₹", "", regex=False)
    .str.replace("(", "-", regex=False)
    .str.replace(")", "", regex=False)
    .str.strip()
    )

    def parse_amount(value):
        if pd.isna(value):
            return None

        # Already numeric? Return it.
        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).strip()

        multiplier = 1
        if value.endswith("T"):
            multiplier = 1_000_000_000_000
            value = value[:-1]
        elif value.endswith("B"):
            multiplier = 1_000_000_000
            value = value[:-1]
        elif value.endswith("M"):
            multiplier = 1_000_000
            value = value[:-1]
        elif value.endswith("K"):
            multiplier = 1_000
            value = value[:-1]

        value = value.replace(",", "").replace("$", "").replace("₹", "")

        try:
            return float(value) * multiplier
        except ValueError:
            return None

    df["amount"] = df["amount"].apply(parse_amount)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df = df.dropna(subset=["amount"])
    df = df.reset_index(drop=True)

    return df

def load_financial_statement(file) -> pd.DataFrame:
    """
    Load a financial statement from CSV, XLSX or PDF
    and return a cleaned dataframe.
    """
    extension = Path(file.name).suffix.lower()

    if extension == ".csv":
        df = read_csv_file(file)

    elif extension in [".xlsx", ".xls"]:
        df = read_excel_file(file)

    elif extension == ".pdf":
        df = read_pdf_file(file)

    else:
        raise ValueError(f"Unsupported file format: {extension}")

    return clean_dataframe(df)