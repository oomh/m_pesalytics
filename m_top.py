# ============================================================================
# M-pesalytics: M-PESA STATEMENT ANALYZER
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import streamlit as st
import pandas as pd
from load_wrangle import load_pdf_data, clean_data
from efficient_analysis import Analyzer
from transaction_categorizer import categorize_transactions_efficiently
from ui_components import (
    create_transaction_tab,
    create_full_transaction_expander
)

# Display columns for transaction details (smart amount display)
display_columns = ["receipt_no", "date_time", "details", "paid_in", "withdrawn"]

# ============================================================================
# CONFIGURATION
# ============================================================================

# App configuration
st.set_page_config(
    layout="wide", page_title="M-pesalytics: M-Pesa Statement Analyzer", page_icon="💸"
)

# I dont want the app to auto scroll on reruns
st.markdown(
    """
<style>
    * {
        overflow-anchor: none !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================


def initialize_session_state():
    """Initialize all session state variables"""
    session_vars = {
        "pdf_path": None,
        "pdf_password": "",
        "process_clicked": False,
        "load_error": None,
        "disable": {"date": False, "month": False},
    }

    for key, default_value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# Initialize session state
initialize_session_state()

# ============================================================================
# USER INTERFACE - HEADER
# ============================================================================

# Hero Section
with st.container():
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem 0 0.5rem;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0.2rem;">📱 M-Peasalytics</h1>
            <p style="font-size: 1rem; color: gray;">Track, analyze, and make sense of your M-Pesa transactions</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background: transparent; padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid rgba(49, 51, 63, 0.15);">
                <div style="font-size: 2rem;">📁</div>
                <h3 style="margin-bottom: 0.5rem;">Upload</h3>
                <p style="font-size: 0.9rem;">Upload your M-Pesa PDF statement and password to get started</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="background: transparent; padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid rgba(49, 51, 63, 0.15);">
                <div style="font-size: 2rem;">📊</div>
                <h3 style="margin-bottom: 0.5rem;">Explore</h3>
                <p style="font-size: 0.9rem;">Browse Money In and Money Out sections to see your transaction patterns</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style="background: transparent; padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid rgba(49, 51, 63, 0.15);">
                <div style="font-size: 2rem;">✅</div>
                <h3 style="margin-bottom: 0.5rem;">Interact</h3>
                <p style="font-size: 0.9rem;">Use checkboxes and expandable sections for deeper insights</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Quick Tips with basic text art-style graphics
    st.markdown(
        """
        <div style="text-align: center; background: transparent; padding: 1rem; border-radius: 8px; margin: 2rem 0 1rem; border: 1px solid rgba(49, 51, 63, 0.2);">
            <h4 style="margin-bottom: 0.5rem;">💡 Quick Tips:</h4>
            <ul style="margin: auto; display: inline-block; text-align: left; font-size: 0.9rem; line-height: 1.6;">
                <li>🗓️ <b>Filter by date/month</b> using the sidebar controls</li>
                <li>☑️ <b>Check boxes in tables</b> to group by user</li>
                <li>📂 <b>Expand sections</b> for detailed transactions</li>
                <li>🧭 <b>Navigate tabs</b> for categories like Spend, Income, Charges</li>
                <li>📈 <b>Rotate screen </b> if you are using a phone</li>
                <li>📲 <b>Download CSVs with the toolbar on the top right of the tables, useful when you need details for all transactions from person
            </ul>
            <pre style="color: gray; font-size: 0.8rem; margin-top: 1rem;">
            </pre>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================================
# USER INTERFACE - FILE UPLOAD
# ============================================================================

with st.expander(
    "📁 Upload M-Pesa Statement",
    expanded=not st.session_state.get("process_clicked", False),
):
    with st.form("pdf_upload_form"):
        pdf = st.file_uploader("Upload your M-Pesa statement (PDF)", type=["pdf"])
        password = st.text_input(
            "Enter PDF password (leave blank if not protected)",
            type="password",
            key="pdf_password_input",
        )
        process = st.form_submit_button("Process")

    if process:
        st.session_state.pdf_path = pdf
        st.session_state.pdf_password = password
        st.session_state.process_clicked = True
        st.session_state.load_error = None

# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================


@st.cache_data(show_spinner="Extracting and cleaning your statement...")
def load_and_clean(pdf_file, password):
    """Load and clean PDF data with error handling"""
    try:
        df = load_pdf_data(pdf_file, password)
        df_cleaned = clean_data(df)
        return df_cleaned, None
    except FileNotFoundError:
        return None, "PDF file not found"
    except PermissionError:
        return None, "Invalid PDF password"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


@st.cache_data(show_spinner="Categorizing transactions efficiently...")
def categorize_data(df_cleaned):
    """Categorize transactions efficiently with error handling"""
    try:
        return categorize_transactions_efficiently(df_cleaned), None
    except Exception as e:
        return None, str(e)


@st.cache_data(show_spinner="Applying filters to categorized data...")
def filter_categorized_data(categorized_data, date_filter=None, month_filter=None):
    """Apply date/month filters to pre-categorized data."""
    if not date_filter and not month_filter:
        return categorized_data

    filtered_categories = {}

    for category, df in categorized_data.items():
        if df.empty:
            filtered_categories[category] = df
            continue

        filtered_df = df.copy()

        # Apply date range filter
        if date_filter and len(date_filter) == 2:
            start_date, end_date = date_filter
            mask = (filtered_df["date_time"] >= pd.to_datetime(start_date)) & (
                filtered_df["date_time"] <= pd.to_datetime(end_date)
            )
            filtered_df = filtered_df.loc[mask]

        # Apply month filter
        elif month_filter:
            month_mask = (
                filtered_df["date_time"].dt.strftime("%B_%Y").isin(month_filter)
            )
            filtered_df = filtered_df.loc[month_mask]

        filtered_categories[category] = filtered_df

    return filtered_categories


# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

# Only proceed if the user has clicked "Process" and a file is uploaded
if st.session_state.get("process_clicked") and st.session_state.pdf_path is not None:
    df_cleaned, load_error = load_and_clean(
        st.session_state.pdf_path, st.session_state.pdf_password
    )

    if load_error:
        st.error(f"Failed to load or clean PDF: {load_error}")
        st.session_state.process_clicked = False
        st.stop()

    if not df_cleaned is None:
        startDate = df_cleaned["date_time"].min().strftime("%b %d, %Y")
        endDate = df_cleaned["date_time"].max().strftime("%b %d, %Y")

    # Categorize transactions
    categorized_data, categorize_error = categorize_data(df_cleaned)

    if categorize_error:
        st.error(f"Failed to categorize transactions: {categorize_error}")
        st.session_state.process_clicked = False
        st.stop()

else:
    st.info("Please upload your PDF and click 'Process' to continue.")
    st.stop()

# ============================================================================
# USER INTERFACE - SIDEBAR CONTAINER FILTERS
# ============================================================================


def update_toggles():
    """Update toggle states to ensure mutual exclusivity"""
    st.session_state.disable["month"] = st.session_state.date_filter
    st.session_state.disable["date"] = st.session_state.month_filter


# Initialize filter variables
date_filter_value = None
month_filter_value = None

with st.sidebar:
    st.header("🔍 Filters")

    # Date toggle
    date_toggle = st.toggle(
        "📅 Date Filter",
        key="date_filter",
        on_change=update_toggles,
        disabled=st.session_state.disable["date"],
    )

    # Month toggle
    month_toggle = st.toggle(
        "📆 Month Filter",
        key="month_filter",
        on_change=update_toggles,
        disabled=st.session_state.disable["month"],
    )

    # Date range filter
    if st.session_state.get("date_filter") and not df_cleaned is None:
        date_range = st.date_input(
            "Select Date Range",
            value=[
                df_cleaned["date_time"].min().date(),
                df_cleaned["date_time"].max().date(),
            ],
            min_value=df_cleaned["date_time"].min().date(),
            max_value=df_cleaned["date_time"].max().date(),
        )
        if len(date_range) == 2:
            date_filter_value = date_range
        else:
            st.warning("Select both dates", icon="⚠️")

    # Month filter
    elif st.session_state.get("month_filter") and not df_cleaned is None:
        month_list = list(
            df_cleaned["date_time"].dt.month_name()
            + "_"
            + df_cleaned["date_time"].dt.year.astype(str)
        )
        month_list = sorted(
            set(month_list),
            key=lambda x: pd.to_datetime(x.split("_")[0] + " 1, " + x.split("_")[1]),
        )
        # Default to first three months when toggle is enabled
        default_months = month_list[:3] if len(month_list) >= 3 else month_list
        month_filter_value = st.segmented_control(
            "Select Months",
            options=month_list,
            default=default_months,
            selection_mode="multi",
        )
        if not month_filter_value:
            month_filter_value = None
    else:
        st.info(f"💡 Showing all data from {startDate} to {endDate}")  # type: ignore

# Apply filters to categorized data
filtered_categorized_data = filter_categorized_data(
    categorized_data, date_filter=date_filter_value, month_filter=month_filter_value
)
st.divider()

# Ensure filtered_categorized_data is not None before initializing Analyzer
if filtered_categorized_data is None:
    st.error("An error occurred while filtering categorized data.")
    st.stop()

# Initialize analyzer
analysisBot = Analyzer(filtered_categorized_data)

# ============================================================================
# TRANSACTION ANALYSIS - GET ALL DATA
# ============================================================================

# Get all transaction analysis with standardized returns
buygoods_fig, bg_spend, bg_charges, bg_transactions, buygoodsFrame, buygoods_df = (
    analysisBot.BuyGoodsPayments()
)
paybill_fig, pb_spend, pb_charges, pb_transactions, paybillFrame, paybill_df = (
    analysisBot.PayBillPayments()
)
transfer_fig, tr_spend, tr_charges, tr_transactions, transferFrame, transfer_df = (
    analysisBot.SendMoney()
)
receive_fig, rc_amount, rc_charges, rc_transactions, receiveFrame, receive_df = (
    analysisBot.ReceivedMoney()
)
deposits_fig, dp_amount, dp_charges, dp_transactions, depositFrame, deposit_df = (
    analysisBot.Deposit()
)
(
    withdrawal_fig,
    wd_amount,
    wd_charges,
    wd_transactions,
    withdrawalFrame,
    withdrawal_df,
) = analysisBot.CashWithdrawals()

(
    received_business_fig,
    rb_amount,
    rb_charges,
    rb_transactions,
    received_businessFrame,
    received_business_df,
) = analysisBot.ReceivedMoney_business()

pochi_fig, pochi_spend, pochi_charges, pochi_transactions, pochiFrame, pochi_df = (
    analysisBot.Pochi()
)
(
    pochi_in_fig,
    pochi_in_spend,
    pochi_in_charges,
    pochi_in_transactions,
    pochi_inFrame,
    pochi_in_df,
) = analysisBot.Pochi_in()
(
    airtime_fig,
    airtime_amount,
    airtime_charges,
    airtime_transactions,
    airtimeFrame,
    airtime_df,
) = analysisBot.airtime_bundle()

# ============================================================================
# USER INTERFACE - MONEY OUT SECTION
# ============================================================================

st.header("💸 Money Out")

with st.container():
    st.subheader("🛒 Lipa Na M-Pesa")
    buy, pay, pochi = st.tabs(["Buy Goods", "Pay Bill", "Pochi La Biashara"])

    # Buy Goods Tab
    with buy:
        create_transaction_tab(
            frame=buygoodsFrame,
            raw_df=buygoods_df,
            fig=buygoods_fig,
            spend=bg_spend,
            charges=bg_charges,
            transactions=bg_transactions,
            merchant_type="BuyGoods Merchant",
            transaction_type="Buy Goods",
            display_columns=display_columns,
            color_map="Reds",
        )

    # Pay Bill Tab
    with pay:
        create_transaction_tab(
            frame=paybillFrame,
            raw_df=paybill_df,
            fig=paybill_fig,
            spend=pb_spend,
            charges=pb_charges,
            transactions=pb_transactions,
            merchant_type="PayBill Merchant",
            transaction_type="Pay Bill",
            display_columns=display_columns,
            color_map="Reds",
            additional_columns={
                "accounts": st.column_config.ListColumn(
                    "Accounts", width="medium", pinned=True
                )
            },
        )

    # Pochi La Biashara Tab
    with pochi:
        create_transaction_tab(
            frame=pochiFrame,
            raw_df=pochi_df,
            fig=pochi_fig,
            spend=pochi_spend,
            charges=pochi_charges,
            transactions=pochi_transactions,
            merchant_type="Pochi Merchant",
            transaction_type="Pochi La Biashara",
            display_columns=display_columns,
            color_map="Reds",
        )

with st.container():
    st.subheader("😒 Cash Transfers & Withdrawals")
    transfer, withdrawals = st.tabs(
        ["Transfers", "Withdrawals"]
    )

    # Transfer Tab
    with transfer:
        create_transaction_tab(
            frame=transferFrame,
            raw_df=transfer_df,
            fig=transfer_fig,
            spend=tr_spend,
            charges=tr_charges,
            transactions=tr_transactions,
            merchant_type="Transfer Recipient",
            transaction_type="Transfers",
            display_columns=display_columns,
            color_map="Reds",
        )

    # Withdrawals Tab
    with withdrawals:
        create_transaction_tab(
            frame=withdrawalFrame,
            raw_df=withdrawal_df,
            fig=withdrawal_fig,
            spend=wd_amount,
            charges=wd_charges,
            transactions=wd_transactions,
            merchant_type="Withdrawal Agent",
            transaction_type="Cash Withdrawals",
            display_columns=display_columns,
            color_map="Reds",
        )

    # TODO: Rethink Airtime Tab
    #     )


st.divider()

# ============================================================================
# USER INTERFACE - MONEY IN SECTION
# ============================================================================

st.header("💰🧲 Money In")

with st.container():
    st.subheader("🥳 Deposits & Received Money")
    deposits, receive, bankreceive, Pochi_payments = st.tabs(
        [
            "Deposits",
            "Received Money from Individuals",
            "Received Money from Institutions",
            "Received via Pochi",
        ]
    )

    # Deposits Tab
    with deposits:
        create_transaction_tab(
            frame=depositFrame,
            raw_df=deposit_df,
            fig=deposits_fig,
            spend=dp_amount,
            charges=dp_charges,
            transactions=dp_transactions,
            merchant_type="Deposit Source",
            transaction_type="Deposits",
            display_columns=display_columns,
            color_map="Greens",
        )

    # Received Money Tab
    with receive:
        create_transaction_tab(
            frame=receiveFrame,
            raw_df=receive_df,
            fig=receive_fig,
            spend=rc_amount,
            charges=rc_charges,
            transactions=rc_transactions,
            merchant_type="Money Sender",
            transaction_type="Received Money",
            display_columns=display_columns,
            color_map="Greens",
        )

    with bankreceive:
        create_transaction_tab(
            frame=received_businessFrame,
            raw_df=received_business_df,
            fig=received_business_fig,
            spend=rb_amount,
            charges=rb_charges,
            transactions=rb_transactions,
            merchant_type="Business Account Sender",
            transaction_type="Received Money from Business",
            display_columns=display_columns,
            color_map="Greens",
        )

    with Pochi_payments:
        create_transaction_tab(
            frame=pochi_inFrame,
            raw_df=pochi_in_df,
            fig=pochi_in_fig,
            spend=pochi_in_spend,
            charges=pochi_in_charges,
            transactions=pochi_in_transactions,
            merchant_type="Pochi Customer",
            transaction_type="Pochi La Biashara_Received",
            display_columns=display_columns,
            color_map="Greens",
        )


st.divider()
st.header("Full Transaction dataframe")

create_full_transaction_expander(
            df=df_cleaned,
            transaction_type="All Transactions",
            display_columns=display_columns)
# ============================================================================
# USER ACTIONS - RESET FUNCTIONALITY
# ============================================================================

if st.button("🔄 Want to analyze a different statement?"):
    for key in ["pdf_uploaded", "pdf_path", "pdf_password", "process_clicked"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
