"""
M-Pesa Data Loading and Preprocessing Module

This module handles the loading, cleaning, and preprocessing of M-Pesa transaction data
from PDF statements. It includes functions for data extraction, transformation, and
standardization.

Functions:

    split_details: Helper function to parse transaction details
    split_type: Helper function to parse transaction types
    
    load_pdf_data: Extracts transaction data from PDF statements
    clean_data: Cleans and standardizes the extracted data

Dependencies:
    - pandas: For data manipulation
    - tabula: For PDF data extraction
"""

import pandas as pd
import numpy as np
import re
import warnings
import streamlit as st
import sys
from tabula.io import read_pdf

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Configuration constants
EXPECTED_COLUMNS = [
    "Receipt No.",
    "Receipt No",
    "Completion Time",
    "Details",
    "Paid In",
    "Withdrawn",
]


# @st.cache_data(show_spinner="Extracting and cleaning your statement...")
# Step 1: Load and examine raw data
def load_pdf_data(pdf_path: str, password: str) -> pd.DataFrame:
    """
    Load M-Pesa transaction data from PDF statement.

    Args:
        pdf_path (str): Path to the PDF statement file
        password (str): Password for protected PDF files

    Returns:
        pd.DataFrame: Combined DataFrame containing extracted transaction data
            or None if extraction fails
    """
    try:
        print(f"📄 Loading PDF: {pdf_path}")
        df_list = read_pdf(
            pdf_path, pages="all", guess=True, lattice=True, password=password)
        print(f"📊 Found {len(df_list)} tables in PDF")

        # Filter for transaction tables
        selected_dfs = [
            df
            for df in df_list
            if isinstance(df, pd.DataFrame) and df.columns.isin(EXPECTED_COLUMNS).any()]
        print(f"\n✅ Found {len(selected_dfs)} transaction tables")

        if selected_dfs:
            combined_df = pd.concat(selected_dfs, ignore_index=True)
            combined_df.columns = (
                combined_df.columns.str.strip()
                .str.lower()
                .str.replace(r"\s+", "", regex=True)
            )
            print(f"📈 Combined dataset shape: {combined_df.shape}")
            return combined_df
        else:
            print("❌ No valid transaction tables found!")
            return pd.DataFrame()

    except Exception as e:
        print(f"❌ Error loading PDF: {str(e)}")
        return pd.DataFrame()


def split_details(details_text):
    """
    Parse transaction details into type and entity components.

    Args:
        details_text (str): Raw transaction details text

    Returns:
        tuple: Contains (transaction_type, entity_name)
    """
    pattern = r"(.*?)(?<!\S)(?: *)-(?: *)\s(?=\S)(.*)"
    match = re.search(pattern, str(details_text), re.IGNORECASE)

    if match:
        return match.group(1).strip(), match.group(2).strip()
    else:
        return details_text, details_text


def split_type(transaction_type):
    """
    Parse transaction type into class and description components.

    Args:
        transaction_type (str): Raw transaction type text

    Returns:
        pd.Series: Contains [type_class, type_description]
    """
    if pd.isna(transaction_type):
        return pd.Series(["", ""])
    else:
        split_list = str(transaction_type).split(" ")
        right = " ".join(split_list[0:4])
        left = " ".join(split_list[4:])
        return pd.Series([right, left])


# @st.cache_data(show_spinner="Cleaning your M-Pesa data...")
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize M-Pesa transaction data.

    Args:
        df (pd.DataFrame): Raw transaction data DataFrame

    Returns:
        pd.DataFrame: Cleaned and standardized DataFrame with added columns:
            - month: e.g., "July_25"
            - week: e.g., "29_25"
            - type_class: General transaction category
            - type_desc: More specific transaction description
    """
    import streamlit as st
    import pandas as pd

    print("\n🧹 Cleaning data...")

    if df is None or df.empty:
        print("❌ The DataFrame is empty after loading.")
        st.error(
            "The DataFrame is empty after loading. Please check the PDF file or password, then try again."
        )
        return pd.DataFrame()

    print(f"Original shape: {df.shape}")

    df_clean = df.copy()

    # Step 1: Drop columns not in expected list
    expected = ('receiptno.', "receiptno", 'completiontime', 'details', 'transactionstatus', 'paidin', 'withdrawn', 'withdraw')
    cols_to_drop = [col for col in df_clean.columns if col not in expected]
    
    if cols_to_drop:
        print(f"🗑️ Dropping unexpected columns: {cols_to_drop}")
        df_clean = df_clean.drop(columns=cols_to_drop)

    # Step 2: Rename columns to standardized names
    mapping = {}
    for col in df_clean.columns:
        lc = col.lower()
        if "receipt" in lc or "ref" in lc:
            mapping[col] = "receipt_no"
        elif "completion" in lc or "time" in lc:
            mapping[col] = "date_time"
        elif "detail" in lc or "details" in lc:
            mapping[col] = "details"
        elif "paid" in lc and "in" in lc:
            mapping[col] = "paid_in"
        elif "withdrawn" in lc or 'withdr' in lc:
            mapping[col] = "withdrawn"

    print(f"📝 Renaming columns using mapping: {mapping}")
    df_clean = df_clean.rename(columns=mapping)

    # Step 3: Keep only necessary renamed columns
    keep_cols = ["receipt_no", "date_time", "details", "paid_in", "withdrawn"]
    df_clean = df_clean[[col for col in keep_cols if col in df_clean.columns]]

    # Step 4: Standardize and clean column values
    df_clean["receipt_no"] = df_clean["receipt_no"].astype("string")
    df_clean["date_time"] = pd.to_datetime(df_clean["date_time"], errors="coerce")

    df_clean["withdrawn"] = (
        pd.to_numeric(
            df_clean["withdrawn"]
            .astype(str)
            .str.replace(",", "")
            .replace(["", "-", "N/A", "nan"], "0"),
            errors="coerce",
        )
        .abs()
        .fillna(0)
    )

    df_clean["paid_in"] = pd.to_numeric(
        df_clean["paid_in"]
        .astype(str)
        .str.replace(",", "")
        .replace(["", "-", "N/A", "nan"], "0"),
        errors="coerce",
    ).fillna(0)

    df_clean["details"] = df_clean["details"].str.replace(r"\s+", " ", regex=True)

    # Step 5: Extract type/entity and classify transactions
    df_clean[["type", "entity"]] = df_clean["details"].apply(
        lambda x: pd.Series(split_details(x))
    )

    df_clean[["type_class", "type_desc"]] = df_clean["type"].apply(
        lambda x: pd.Series(split_type(x))
    )

    # Step 6: Add formatted time columns
    df_clean["month"] = df_clean["date_time"].dt.strftime("%B_%y")
    df_clean["week"] = df_clean["date_time"].dt.strftime("%V_%y")

    print(f"✅ Cleaned shape: {df_clean.shape}")
    print(f"🧾 Final columns: {list(df_clean.columns)}")
    if not df_clean["date_time"].isnull().all():
        print(
            f"🗓️ Date range: {df_clean['date_time'].min().strftime('%b %d, %Y')} → {df_clean['date_time'].max().strftime('%b %d, %Y')}"
        )

    return df_clean



if __name__ == "__main__":
    pass
