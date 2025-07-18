"""
UI Components Module for M-Top Application

This module contains reusable UI components and standardized patterns
to eliminate code duplication and ensure consistency across the application.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Union


def create_metrics_display(
    spend: float, charges: Optional[float], transactions: int, frame: pd.DataFrame
) -> None:
    """
    Create standardized metrics display with 4 columns.

    Args:
        spend: Total amount spent
        charges: Total charges incurred
        transactions: Number of transactions
        frame: DataFrame containing transaction data
    """
    with st.container():
        col1, col2 = st.columns(
            [
                1,
                1,
            ]
        )
        with col1:
            st.metric("Transacted", f"{spend:,.0f}/=", border=True)
        with col2:
            (
                st.metric("Charges incurred", f"{charges:,.0f}/=", border=True)
                if charges
                else st.metric("Total Charges", "-", border=True)
            )
    with st.container():
        col3, col4 = st.columns([1, 1])
        with col3:
            (
                st.metric("Transactions:", f"{transactions:,}", border=True)
                if transactions
                else st.metric("Transactions", "-", border=True)
            )
        with col4:
            st.metric(
                "Unique users", f"{frame['processed_entity'].nunique():,}", border=True
            )


def create_styled_dataframe(
    data: pd.DataFrame,
    color_map: str = "Reds",
    gradient_subset: Optional[List[str]] = None,
    format_dict: Optional[Dict[str, Any]] = None,
    column_config: Optional[Dict[str, Any]] = None,
    merchant_type: str = "Merchant",
) -> Any:
    """
    Create a standardized styled dataframe with consistent configuration.

    Args:
        data: DataFrame to display
        color_map: Color map for gradient styling
        gradient_subset: Columns to apply gradient to
        format_dict: Formatting dictionary for columns
        column_config: Column configuration for Streamlit
        merchant_type: Type of merchant for column naming

    Returns:
        Streamlit dataframe event object
    """
    if gradient_subset is None:
        gradient_subset = ["count"]

    if format_dict is None:
        format_dict = {"amount": lambda x: f"{x:,.0f}/="}

    if column_config is None:
        column_config = {
            "amount": st.column_config.NumberColumn("Amount"),
            "count": st.column_config.NumberColumn(
                "Number of Transactions", width="small"
            ),
            "processed_entity": st.column_config.Column(
                f"{merchant_type}", pinned=True
            ),
        }

    return st.dataframe(
        data.style.background_gradient(cmap=color_map, subset=gradient_subset).format(
            format_dict
        ),
        column_config=column_config,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )


def transaction_lookup(
    frame: pd.DataFrame,
    df: pd.DataFrame,
    selection: Optional[Dict[str, Any]],
    display_columns: List[str],
) -> pd.DataFrame:
    """
    Standard transaction lookup function for drill-down functionality.
    Supports multiple row selection for comparing entities.

    Args:
        frame: Aggregated frame with processed_entity
        df: Raw transaction DataFrame
        selection: Streamlit selection object
        display_columns: Columns to display in result

    Returns:
        Filtered DataFrame with selected merchants' transactions (sorted by date)
    """
    if not selection or not selection.get("rows"):
        return pd.DataFrame()

    # Get all selected row indices
    selected_indices = selection["rows"]

    # Extract processed_entity values for all selected rows
    entity_values = [frame.iloc[idx]["processed_entity"] for idx in selected_indices]

    # Filter for all selected entities
    result = df[df["processed_entity"].isin(entity_values)].copy()

    # Sort by date_time for better readability (most recent first)
    if "date_time" in result.columns:
        result = result.sort_values("date_time", ascending=False)

    return result[display_columns]


def create_transaction_detail_section(
    result: pd.DataFrame,
    merchant_type: str,
    column_config: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Create a standardized transaction detail section with expander.

    Args:
        result: DataFrame with transaction details
        merchant_type: Type of merchant for labeling
        column_config: Optional column configuration
    """
    if not result.empty:
        with st.expander(f"Details for selected {merchant_type}"):
            # Create default column configuration if none provided
            if column_config is None:
                column_config = {
                    "receipt_no": st.column_config.Column("Receipt No.", width="small"),
                    "date_time": st.column_config.DatetimeColumn(
                        "Date/Time", format="ddd, DD MMM, YY | hh:mma"
                    ),
                    "details": st.column_config.Column("Transaction Details"),
                    "withdrawn": st.column_config.NumberColumn(
                        "Withdrawn", format="%.0f/="
                    ),
                    "paid_in": st.column_config.NumberColumn(
                        "Paid-in", format="%.0f/="
                    ),
                    "transaction_type": st.column_config.Column("Type", width="small"),
                }

            # Apply styling for currency formatting
            styled_df = result.style.format(
                {"amount": lambda x: f"{x:,.0f}/=" if x is not None and x != 0 else ""}
            )

            st.dataframe(styled_df, hide_index=True, column_config=column_config)
    else:
        st.markdown(
            f"Select row(s) from the table to see details for specific {merchant_type}."
        )


def create_full_transaction_expander(
    df: pd.DataFrame,
    transaction_type: str,
    display_columns: List[str],
    column_config: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Create standardized full transaction list expander.

    Args:
        df: Full transaction DataFrame
        transaction_type: Type of transactions for labeling
        display_columns: Columns to display
        column_config: Optional column configuration
    """
    with st.expander(f"All {transaction_type} Transactions", expanded=False):
        if not df.empty:
            st.dataframe(
                df[display_columns], column_config=column_config, hide_index=True
            )
        else:
            st.dataframe(df[display_columns], hide_index=True)


def create_transaction_tab(
    frame: pd.DataFrame,
    raw_df: pd.DataFrame,
    fig: Any,
    spend: float,
    charges: Optional[float],
    transactions: int,
    merchant_type: str,
    transaction_type: str,
    display_columns: List[str],
    color_map: str = "Reds",
    additional_columns: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Create a complete standardized transaction tab with all components.

    Args:
        frame: Aggregated transaction DataFrame
        raw_df: Raw transaction DataFrame
        fig: Plotly figure for visualization
        spend: Total amount spent
        charges: Total charges
        transactions: Number of transactions
        merchant_type: Type of merchant (e.g., "BuyGoods Merchant")
        transaction_type: Type of transaction (e.g., "Buy Goods")
        display_columns: Columns to display in detail view
        color_map: Color map for styling
        additional_columns: Additional column configurations
    """
    if not raw_df.empty:
        # Display metrics
        create_metrics_display(spend, charges, transactions, frame)

        with st.container():
            col1, col2 = st.columns([1, 1])

            with col2:
                st.markdown("\n")

                # Create column config
                column_config = {
                    "amount": st.column_config.NumberColumn("Amount"),
                    "count": st.column_config.NumberColumn(
                        "Number of Transactions", width="small"
                    ),
                    "processed_entity": st.column_config.Column(
                        merchant_type, pinned=True
                    ),
                }

                # Add additional columns if provided
                if additional_columns:
                    column_config.update(additional_columns)

                # Create styled dataframe
                event = create_styled_dataframe(
                    data=frame,
                    color_map=color_map,
                    column_config=column_config,
                    merchant_type=merchant_type,
                )

            # Handle selection and show details
            selection = event.get("selection") if event else None
            result = transaction_lookup(frame, raw_df, selection, display_columns)

            # Determine appropriate title based on selection count
            if selection and selection.get("rows"):
                num_selected = len(selection["rows"])
                if num_selected == 1:
                    detail_title = merchant_type
                else:
                    detail_title = f"{num_selected} selected {merchant_type}s"
            else:
                detail_title = merchant_type

            create_transaction_detail_section(result, detail_title)

            with col1:
                st.plotly_chart(
                    fig, use_container_width=True, key=f"{transaction_type}_fig"
                )

            # Show all transactions
            create_full_transaction_expander(
                raw_df,
                transaction_type,
                display_columns,
                column_config={
                    "receipt_no": st.column_config.Column("Receipt No.", width="small"),
                    "date_time": st.column_config.DatetimeColumn(
                        "Date/Time", format="ddd, DD MMM, YY | hh:mma"
                    ),
                    "paid_in": st.column_config.NumberColumn(
                        "Paid-in", format="%.0f/=", width="small"
                    ),
                    "withdrawn": st.column_config.NumberColumn(
                        "Withdrawn", format="%.0f/=", width="small"
                    ),
                    "details": st.column_config.Column("Transaction Details"),
                },
            )
    else:
        st.warning(
            f"No {transaction_type} transactions found in the provided statement.",
            icon="⚠️",
        )
