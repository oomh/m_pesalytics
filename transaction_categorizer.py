"""
Efficient Single-Pass Transaction Categorizer.

"""

import pandas as pd
import re
from typing import Dict, Tuple


class TransactionCategorizer:
    """
    A class to categorize M-Pesa transactions
    """

    def __init__(self):
        """Initialize the categorizer with default categories."""
        self.categories = {
            # Money in
            "ReceivedMoney": [],
            "ReceivedMoney_business": [],
            "Deposit": [],
            "Pochi_in": [],
            "Reversals": [],  # Inward and Outward
            "HustlerFund": [],
            "KCB": [],  # Inward and Outward
            "MShwari": [],  # Inward and Outward
            "businessPayment_fromOtherSME": [],
            # Money Out
            "SendMoney": [],
            "businessPayment_toCustomer": [],
            "Overdraft": [],
            "BuyGoodsPayments": [],
            "PayBillPayments": [],
            "Pochi": [],
            "CashWithdrawals": [],
            "airtime_bundle": [],
            "NoDetails": [],
            "uncategorized": [],
        }

        # Regex patterns for entity processing (compiled once for efficiency)
        self.masked_phone_pattern = re.compile(r"\*+")
        self.paybill_pattern = re.compile(r"(.*?)(?:\s+Acc\.\s+(.*)|$)")
        self.business_payment_pattern = re.compile(
            r"(.*?)(?:\s+(?:via).*?(?:is)\s+(.*)|$)", re.IGNORECASE
        )

    def add_category(self, category_name: str):
        """Add a new transaction category to the categorizer."""
        if category_name not in self.categories:
            self.categories[category_name] = []

    def process_masked_phone(self, entity: str) -> tuple:
        """
        Process masked phone numbers to extract names.

        Args:
            entity: Raw entity string (e.g., "2547******09 John Doe")

        Returns:
            Cleaned entity name (e.g., "John Doe")
        """
        if pd.isna(entity) or entity == "":
            return entity, ""

        # Check if it contains masked numbers (asterisks)
        if self.masked_phone_pattern.search(entity):
            # Extract name part after phone number
            parts = entity.split(" ", 1)
            return parts[1].title(), parts[0].title()

        return entity.title(), ""

    def process_business_and_account(self, entity: str) -> tuple:
        """_summary_

        Args:
            entity (str): _description_

        Returns:
            str: _description_
        """
        if pd.isna(entity) or entity == "":
            return entity, ""

        # Check if it contains masked numbers (asterisks)
        if self.business_payment_pattern.search(entity):
            match = self.business_payment_pattern.search(entity)
            if match:
                business_name = match.group(1).strip() if match.group(1) else ""
                extra_info = match.group(2).strip() if match.group(2) else ""

                return business_name, extra_info
            return entity, ""
        return entity, ""

    def extract_paybill_details(self, entity: str) -> Tuple[str, str]:
        """
        Extract business name and account number from paybill entity.

        Args:
            entity: Raw entity string (e.g., "Kenya Power Acc. 123456")

        Returns:
            Tuple of (business_name, account_number)
        """
        if pd.isna(entity) or entity == "":
            return entity, ""

        match = self.paybill_pattern.search(entity)

        if match:
            business_name = match.group(1).strip()
            account_no = match.group(2).strip() if match.group(2) else ""
            return business_name, account_no

        return entity, ""

    def categorize_transaction(self, row: pd.Series) -> Dict:
        """
        Categorize a single transaction and process its entity.

        Args:
            row: DataFrame row containing transaction data

        Returns:
            Dictionary with categorized and processed transaction data
        """
        type_class = str(row["type_class"]).lower()
        type_desc = str(row["type_desc"]).lower()
        entity = str(row["entity"])
        details = str(row["details"]).lower()

        # Base transaction data
        transaction_data = {
            "receipt_no": row["receipt_no"],
            "date_time": row["date_time"],
            "details": row["details"],
            "paid_in": row["paid_in"],
            "withdrawn": row["withdrawn"],
            "entity": entity,
            "type_class": row["type_class"],
            "type_desc": row["type_desc"],
            "month": row["month"],
            "week": row["week"],
            "processed_entity": entity,
            "is_charge": False,
            "category": None,
            "subcategory": None,
        }

        # Match/case categorization with entity processing
        # Match on a tuple of columns for more flexibility
        # Ordered to match self.categories sequence
        match (details, type_desc, type_class):

            # Money In Categories
            case (x, y, z) if "funds received from" == z:
                transaction_data["category"] = "ReceivedMoney"
                transaction_data["is_charge"] = False
                name, account = (
                    # expecting only individuals but just incase.
                    self.process_masked_phone(entity)
                    if entity[0:1].isnumeric()
                    else self.process_business_and_account(entity)
                )
                transaction_data["processed_entity"] = name
                transaction_data["account_no"] = account

            case (x, y, z) if (
                "merchant customer payment from" == z
                or "salary payment from" in z
                or "promotion payment from" in z
                or "business payment from" in z
                or "funds received from business" in z
            ):
                transaction_data["category"] = "ReceivedMoney_business"
                transaction_data["is_charge"] = False
                name, account = (
                    self.process_masked_phone(entity)
                    if entity[0:1].isnumeric()
                    else self.process_business_and_account(entity)
                )
                transaction_data["processed_entity"] = name
                transaction_data["account_no"] = account

            case (x, y, z) if "deposit of" in x:
                transaction_data["category"] = "Deposit"
                transaction_data["subcategory"] = "deposit"

            case (x, y, z) if z == "customer payment to small" and y == "business from":
                transaction_data["category"] = "Pochi_in"
                transaction_data["is_charge"] = False
                name, account = (
                    self.process_masked_phone(entity)
                    if entity[0:1].isnumeric()
                    else self.process_business_and_account(entity)
                )
                transaction_data["processed_entity"] = name
                transaction_data["account_no"] = account

            case (x, y, z) if "reversal" in x:
                transaction_data["category"] = "Reversals"
                transaction_data["subcategory"] = ()

            case (x, y, z) if "term loan" in x:
                transaction_data["category"] = "HustlerFund"
                transaction_data["subcategory"] = y
                transaction_data["is_charge"] = "charge" in z

            case (x, y, z) if "kcb m-pesa" in x:
                transaction_data["category"] = "KCB"
                transaction_data["subcategory"] = y

            case (x, y, z) if "m-shwari" in x:
                transaction_data["category"] = "MShwari"
                transaction_data["subcategory"] = "mshwari"

            case (x, y, z) if (
                "small business transfer to" in z and "other small business from" in y
            ):
                transaction_data["category"] = "businessPayment_fromOtherSME"
                transaction_data["is_charge"] = False
                name, account = (
                    self.process_masked_phone(entity)
                    if entity[0:1].isnumeric()
                    else self.process_business_and_account(entity)
                )
                transaction_data["processed_entity"] = name
                transaction_data["account_no"] = account

            # Money Out Categories
            case (x, y, z) if (
                "customer transfer" in x
                or "send money" in x
                or "transfer to other small business to" in x
            ):
                transaction_data["category"] = "SendMoney"
                transaction_data["is_charge"] = "charge" in y
                transaction_data["subcategory"] = (
                    "charge" if transaction_data["is_charge"] else "transfer"
                )
                transaction_data["processed_entity"] = self.process_masked_phone(
                    entity
                )[0]

            case (x, y, z) if z == "small business payment to":
                transaction_data["category"] = "businessPayment_toCustomer"
                transaction_data["is_charge"] = False
                name, account = (
                    self.process_masked_phone(entity)
                    if entity[0:1].isnumeric()
                    else self.process_business_and_account(entity)
                )
                transaction_data["processed_entity"] = name
                transaction_data["account_no"] = account

            case (x, y, z) if "overdraft" in x or "od loan" in x:
                transaction_data["category"] = "Overdraft"
                transaction_data["subcategory"] = "overdraft"

            case (x, y, z) if "merchant payment" in x or "pay merchant" in x:
                transaction_data["category"] = "BuyGoodsPayments"
                transaction_data["is_charge"] = "charge" in z
                transaction_data["subcategory"] = (
                    "charge" if transaction_data["is_charge"] else ""
                )

            case (x, y, z) if "pay bill" in x:
                transaction_data["category"] = "PayBillPayments"
                transaction_data["is_charge"] = "charge" in z
                transaction_data["subcategory"] = (
                    "charge" if transaction_data["is_charge"] else ""
                )
                business_name, account_no = self.extract_paybill_details(entity)
                transaction_data["processed_entity"] = business_name
                transaction_data["account_no"] = account_no

            case (x, y, z) if "customer payment to small business to" in x:
                transaction_data["category"] = "Pochi"
                transaction_data["subcategory"] = "pochi"
                transaction_data["processed_entity"] = self.process_masked_phone(
                    entity
                )[0]

            case (x, y, z) if "withdrawal" in x and not y[0:4] == "from":
                transaction_data["category"] = "CashWithdrawals"
                transaction_data["is_charge"] = "charge" in x
                transaction_data["subcategory"] = (
                    "charge" if transaction_data["is_charge"] == True else "withdrawal"
                )

            case (x, y, z) if "airtime" in x or "bundles" in y or "bundle" in x:
                transaction_data["category"] = "airtime_bundle"
                transaction_data["is_charge"] = False
                transaction_data["subcategory"] = "purchase"
                transaction_data["processed_entity"] = self.process_masked_phone(
                    entity
                )[0]

            # Special Cases
            case (x, y, z) if x == "nan":
                # I found in Some statements, some transactions did not have any details
                transaction_data["category"] = "NoDetails"
                transaction_data["is_charge"] = ""
                transaction_data["subcategory"] = ""

            case _:
                transaction_data["category"] = "uncategorized"
                transaction_data["subcategory"] = "unknown"
                transaction_data["processed_entity"] = (
                    self.process_masked_phone(entity)
                    if entity[0:2].isnumeric() == True
                    else "non"
                )

        return transaction_data

    def categorize_transactions(
        self, df_clean: pd.DataFrame
    ) -> Dict[str, pd.DataFrame]:
        """
        Categorize all transactions in a single pass.

        Args:
            df_clean: Cleaned DataFrame with M-Pesa transactions

        Returns:
            Dictionary mapping category names to DataFrames
        """
        print(f"🔄 Categorizing {df_clean['receipt_no'].nunique()} transactions...")

        # Single pass through all transactions
        for _, row in df_clean.iterrows():
            transaction_data = self.categorize_transaction(row)
            category = transaction_data["category"]

            # Add to appropriate category
            if category in self.categories:
                self.categories[category].append(transaction_data)

        # Convert to DataFrames for easy analysis
        categorized_dfs = {}
        for category, transactions in self.categories.items():
            if transactions:
                categorized_dfs[category] = pd.DataFrame(transactions)
                print(f"✅ {category}: {len(transactions)} transactions")
            else:
                categorized_dfs[category] = pd.DataFrame()

        print(
            f"🎯 Categorization complete! Found {len([c for c in categorized_dfs.values() if len(c) > 0])} active categories"
        )
        if len(categorized_dfs["uncategorized"]) > 0:
            print("Uncategorized type classes")
            print(categorized_dfs["uncategorized"]["type_class"].unique())
        else:
            print("All transactions categorized")

        return categorized_dfs

    def get_category_summary(
        self, categorized_data: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Get a summary of all transaction categories.

        Args:
            categorized_data: Dictionary of categorized DataFrames

        Returns:
            Summary DataFrame with category statistics
        """
        summary_data = []

        for category, df in categorized_data.items():
            if len(df) > 0:
                summary_data.append(
                    {
                        "category": category,
                        "transaction_count": df["receipt_no"].nunique(),
                        "total_withdrawn": df["withdrawn"].sum(),
                        "total_paid_in": df["paid_in"].sum(),
                        "unique_entities": df["processed_entity"].nunique(),
                        "date_range": f"{df['date_time'].min().strftime('%Y-%m-%d')} to {df['date_time'].max().strftime('%Y-%m-%d')}",
                    }
                )

        return pd.DataFrame(summary_data)


# Convenience functions for easy usage
def categorize_transactions_efficiently(
    df_clean: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to categorize transactions efficiently.

    Args:
        df_clean: Cleaned DataFrame with M-Pesa transactions

    Returns:
        Dictionary mapping category names to DataFrames
    """
    categorizer = TransactionCategorizer()
    return categorizer.categorize_transactions(df_clean)


def get_transaction_summary(categorized_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Get a summary of categorized transactions.

    Args:
        categorized_data: Dictionary of categorized DataFrames

    Returns:
        Summary DataFrame with category statistics
    """
    categorizer = TransactionCategorizer()
    return categorizer.get_category_summary(categorized_data)


if __name__ == "__main__":
    # Example usage
    print(
        "I only need the two convenience functions: from transaction_categorizer import categorize_transactions_efficiently"
    )
