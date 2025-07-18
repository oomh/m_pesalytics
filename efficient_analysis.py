"""
Efficient Analysis Functions for Pre-Categorized Transaction Data

This module provides optimized analysis functions that work with pre-categorized
transaction data, eliminating the need for repeated filtering operations.

Features:
    - Works with pre-categorized DataFrames from transaction_categorizer
    - Maintains all original functionality and return values
    - Significantly faster analysis (O(1) lookup instead of O(n) filtering)
    - Compatible with existing Streamlit visualization code
    - Extensible for new transaction categories

"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Tuple, Optional
import numpy as np
from visualize import create_pie_chart, create_horizontal_bar_chart

# Configuration constants
PX_TEMPLATE = "ggplot2"
COLOR_SCALE = "Peach"  # Updated to match efficient_analysis default
N_LARGEST = 10


class Analyzer:
    """
    Efficient analyzer for pre-categorized transaction data.

    This class provides optimized analysis functions that work with
    pre-categorized DataFrames, eliminating repeated filtering operations.
    """

    def __init__(self, categorized_data: Dict[str, pd.DataFrame]):
        """
        Initialize the analyzer with pre-categorized data.

        Args:
            categorized_data: Dictionary mapping category names to DataFrames
        """
        self.data = categorized_data

    # ============================================================================
    # MONEY IN CATEGORIES
    # ============================================================================

    def ReceivedMoney(self) -> Tuple:
        """
        Analyze received money transactions.

        Returns:
            Tuple of (figure, total_received, total_transactions, receive_frame)
        """
        receive_df = self.data.get("ReceivedMoney", pd.DataFrame())

        if receive_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_received = receive_df["paid_in"].sum()
        total_transactions = receive_df.nunique()["receipt_no"]

        # Group by sender
        receive_frame = (
            receive_df.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("paid_in", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=receive_frame, x_col="amount", y_col="processed_entity", title=f""
        )

        return (
            fig,
            total_received,
            None,  # there are no charges but i wanted to standardize the return type
            total_transactions,
            receive_frame,
            receive_df,
        )

    def ReceivedMoney_business(self) -> Tuple:
        """
        Analyze business received money transactions.

        Returns:
            Tuple of (figure, total_received, total_charges, total_transactions, frame, raw_df)
        """
        # TODO: Implement business received money analysis
        # This should analyze funds received from business payments, salary payments, etc.
        business_df = self.data.get("ReceivedMoney_business", pd.DataFrame())

        if business_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_received = business_df["paid_in"].sum()
        total_transactions = business_df.nunique()["receipt_no"]

        # Group by sender (business entity)
        business_frame = (
            business_df.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("paid_in", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=business_frame, x_col="amount", y_col="processed_entity", title=f""
        )

        return (
            fig,
            total_received,
            0,  # No charges, standardize return type
            total_transactions,
            business_frame,
            business_df,
        )

    def Deposit(self) -> Tuple:
        """
        Analyze deposit transactions.

        Returns:
            Tuple of (figure, total_deposited, total_transactions, deposit_frame)
        """
        deposit_df = self.data.get("Deposit", pd.DataFrame())

        if deposit_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_deposited = deposit_df["paid_in"].sum()
        total_transactions = deposit_df.nunique()["receipt_no"]

        # Group by source
        deposit_frame = (
            deposit_df.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("paid_in", "sum"),
            )
            .sort_values(by="amount", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=deposit_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return fig, total_deposited, 0, total_transactions, deposit_frame, deposit_df

    def Pochi_in(self) -> Tuple:
        """
        Analyze Pochi In transactions.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        pochi_in_df = self.data.get("Pochi_in", pd.DataFrame())

        if pochi_in_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_amount = pochi_in_df["paid_in"].sum()
        total_transactions = pochi_in_df["receipt_no"].nunique()

        # Group by entity
        pochi_in_frame = (
            pochi_in_df.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("paid_in", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=pochi_in_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return fig, total_amount, 0, total_transactions, pochi_in_frame, pochi_in_df

    def Reversals(self) -> Tuple:
        """
        Analyze reversal transactions (both inward and outward).

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        # TODO: Implement reversal analysis
        # This should analyze both inward and outward reversals
        reversals_df = self.data.get("Reversals", pd.DataFrame())

        if reversals_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # TODO: Add implementation here
        return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

    def HustlerFund(self) -> Tuple:
        """
        Analyze Hustler Fund transactions.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        # TODO: Implement Hustler Fund analysis after real world reaserch
        # This should analyze term loan requests and repayments
        hustler_df = self.data.get("HustlerFund", pd.DataFrame())

        if hustler_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # TODO: Add implementation here
        return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

    def KCB(self) -> Tuple:
        """
        Analyze KCB M-Pesa transactions (both inward and outward).

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        # TODO: Implement KCB analysis
        # This should analyze KCB requests and repayments
        kcb_df = self.data.get("KCB", pd.DataFrame())

        if kcb_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # TODO: Add implementation here
        return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

    def MShwari(self) -> Tuple:
        """
        Analyze M-Shwari transactions (both inward and outward).

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        # TODO: Implement M-Shwari analysis
        # This should analyze M-Shwari requests and repayments
        mshwari_df = self.data.get("MShwari", pd.DataFrame())

        if mshwari_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # TODO: Add implementation here
        return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

    def businessPayment_fromOtherSME(self) -> Tuple:
        """
        Analyze business payments from other SMEs.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        # TODO: Implement business payment from other SME analysis
        # This should analyze small business transfer to other small business
        sme_df = self.data.get("businessPayment_fromOtherSME", pd.DataFrame())

        if sme_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # TODO: Add implementation here
        return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

    # ============================================================================
    # MONEY OUT CATEGORIES
    # ============================================================================

    def SendMoney(self) -> Tuple:
        """
        Analyze Send Money transactions.

        Returns:
            Tuple of (figure, total_spend, total_charges, transaction_count, transfer_frame)
        """
        transfer_df = self.data.get("SendMoney", pd.DataFrame())

        if transfer_df.empty:
            return None, 0, 0, 0, pd.DataFrame()

        # Separate transfers from charges
        transfers = transfer_df[~transfer_df["is_charge"]]
        charges = transfer_df[transfer_df["is_charge"]]

        if transfers.empty:
            return None, 0, 0, 0, pd.DataFrame()

        # Calculate totals
        total_spend = transfers["withdrawn"].sum()
        total_charges = charges["withdrawn"].sum()
        transaction_count = transfers.nunique()["receipt_no"]

        # Group by recipient
        transfer_frame = (
            transfers.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("withdrawn", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=transfer_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return (
            fig,
            total_spend,
            total_charges,
            transaction_count,
            transfer_frame,
            transfers,
        )

    def businessPayment_toCustomer(self) -> Tuple:
        """
        Analyze business payments to customers.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        business_customer_df = self.data.get(
            "businessPayment_toCustomer", pd.DataFrame()
        )

        if business_customer_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Separate transfers from charges
        transfers = business_customer_df[~business_customer_df["is_charge"]]
        charges = business_customer_df[business_customer_df["is_charge"]]

        if transfers.empty:
            return None, 0, 0, 0, pd.DataFrame()

        total_spend = transfers["withdrawn"].sum()
        total_charges = charges["withdrawn"].sum()
        transaction_count = transfers.nunique()["receipt_no"]

        # Group by recipient
        transfer_frame = (
            transfers.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("withdrawn", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=transfer_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return (
            fig,
            total_spend,
            total_charges,
            transaction_count,
            transfer_frame,
            transfers,
        )

    def Overdraft(self) -> Tuple:
        """
        Analyze overdraft transactions.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        # TODO: Implement overdraft analysis
        # This should analyze overdraft and OD loan transactions, but the statements i had were not clear
        overdraft_df = self.data.get("Overdraft", pd.DataFrame())

        if overdraft_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # TODO: Add implementation here
        return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

    def BuyGoodsPayments(self) -> Tuple:
        """
        Analyze Buy Goods transactions.

        Returns:
            Tuple of (figure, total_spend, total_charges, BuyGoodsMerchants_count, BuyGoodsMerchants_frame)
        """
        buygoods_df = self.data.get("BuyGoodsPayments", pd.DataFrame())

        if buygoods_df.empty:
            return None, 0, 0, 0, pd.DataFrame()

        # Separate payments from charges
        payments = buygoods_df[~buygoods_df["is_charge"]]
        charges = buygoods_df[buygoods_df["is_charge"]]

        if payments.empty:
            return None, 0, 0, 0, pd.DataFrame()

        # Calculate totals
        total_spend = payments["withdrawn"].sum()
        total_charges = charges["withdrawn"].sum()
        BuyGoodsMerchants_count = payments.nunique()["receipt_no"]

        # Group by BuyGoodsMerchants

        BuyGoodsMerchants_frame = (
            payments.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("withdrawn", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=BuyGoodsMerchants_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return (
            fig,
            total_spend,
            total_charges,
            BuyGoodsMerchants_count,
            BuyGoodsMerchants_frame,
            payments,
        )

    def PayBillPayments(self) -> Tuple:
        """
        Analyze paybill transactions.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        paybill_df = self.data.get("PayBillPayments", pd.DataFrame())

        if paybill_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Separate payments from charges
        payments = paybill_df[~paybill_df["is_charge"]]
        charges = paybill_df[paybill_df["is_charge"]]

        if payments.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_sent = payments["withdrawn"].sum()
        total_charges = charges["withdrawn"].sum()
        transaction_count = payments.nunique()["receipt_no"]

        # Group by business and aggregate accounts
        def agg_accounts(accounts):
            unique_accounts = accounts.dropna().unique()
            return ", ".join(unique_accounts) if len(unique_accounts) > 0 else ""

        paybill_frame = (
            payments.groupby("processed_entity")
            .agg(
                accounts=("account_no", agg_accounts),
                count=("receipt_no", "count"),
                amount=("withdrawn", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=paybill_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return (
            fig,
            total_sent,
            total_charges,
            transaction_count,
            paybill_frame,
            payments,
        )

    def Pochi(self) -> Tuple:
        """
        Analyze Pochi transactions.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        pochi_df = self.data.get("Pochi", pd.DataFrame())

        if pochi_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_amount = pochi_df["withdrawn"].sum()
        total_transactions = pochi_df["receipt_no"].nunique()

        # Group by entity
        pochi_frame = (
            pochi_df.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("withdrawn", "sum"),
            )
            .sort_values(by="count", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=pochi_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return fig, total_amount, 0, total_transactions, pochi_frame, pochi_df

    def CashWithdrawals(self) -> Tuple:
        """
        Analyze cash withdrawal transactions.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        withdrawal_df = self.data.get("CashWithdrawals", pd.DataFrame())

        if withdrawal_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Separate withdrawals from charges
        withdrawals = withdrawal_df[~withdrawal_df["is_charge"]]
        charges = withdrawal_df[withdrawal_df["is_charge"]]

        if withdrawals.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_withdrawal = withdrawals["withdrawn"].sum()
        total_charges = charges["withdrawn"].sum()
        withdrawal_count = len(withdrawals)

        # Group by location
        withdrawal_frame = (
            withdrawals.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("withdrawn", "sum"),
            )
            .sort_values(by="amount", ascending=False)
            .reset_index()
        )

        # Create visualization
        fig = create_horizontal_bar_chart(
            data=withdrawal_frame,
            y_col="processed_entity",
            x_col="amount",
            title="",
        )

        return (
            fig,
            total_withdrawal,
            total_charges,
            withdrawal_count,
            withdrawal_frame,
            withdrawals,
        )

    def airtime_bundle(self) -> Tuple:
        """
        Analyze airtime purchase transactions.

        Returns:
            Tuple of (figure, total_amount, total_charges, total_transactions, frame, raw_df)
        """
        airtime_df = self.data.get("airtime_bundle", pd.DataFrame())

        if airtime_df.empty:
            return None, 0, 0, 0, pd.DataFrame(), pd.DataFrame()

        # Calculate totals
        total_airtime = airtime_df["withdrawn"].sum()
        total_transactions = len(airtime_df)

        # Group by provider
        airtime_frame = (
            airtime_df.groupby("processed_entity")
            .agg(
                count=("receipt_no", "count"),
                amount=("withdrawn", "sum"),
            )
            .sort_values(by="amount", ascending=False)
            .reset_index()
        )

        # Create pie chart for airtime (different from other analyses)
        fig = create_pie_chart(
            data=airtime_frame,
            values_col="amount",
            names_col="processed_entity",
            title="",
        )

        return fig, total_airtime, 0, total_transactions, airtime_frame, airtime_df


if __name__ == "__main__":
    print("Efficient Analysis Module")
