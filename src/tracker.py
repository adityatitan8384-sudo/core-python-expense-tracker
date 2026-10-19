import csv
import json
from datetime import datetime
from pathlib import Path

from reports import (
    calculate_monthly_summary,
    calculate_category_spending,
    find_highest_expense,
    build_text_report
)


class ExpenseTracker:
    """
    Main class of the project.

    I kept the actual data operations inside one class so main.py
    mainly handles the menu and user input.
    """

    def __init__(self):
        # Path is used instead of hard-coding OS-specific slashes.
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.transactions_file = self.data_dir / "transactions.json"
        self.users_file = self.data_dir / "users.json"
        self.export_dir = self.base_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)

        self.user_name = self.load_user()
        self.transactions = self.load_transactions()

    def load_user(self):
        """Load the saved user or create a simple default user."""
        try:
            if self.users_file.exists():
                with open(self.users_file, "r", encoding="utf-8") as file:
                    users = json.load(file)

                if users:
                    return users[0]["name"]

            # This project does not need login/authentication,
            # so one local user is enough for now.
            user_name = input("Enter your name: ").strip() or "User"

            users = [{"id": 1, "name": user_name}]

            with open(self.users_file, "w", encoding="utf-8") as file:
                json.dump(users, file, indent=4)

            return user_name

        except (json.JSONDecodeError, OSError):
            # If the user file is damaged, the tracker can still run.
            return "User"

    def load_transactions(self):
        """Read transactions from JSON."""
        if not self.transactions_file.exists():
            return []

        try:
            with open(self.transactions_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except (json.JSONDecodeError, OSError):
            print("Warning: transactions file could not be read. Starting empty.")
            return []

    def save_transactions(self):
        """Write current transactions back to JSON."""
        with open(self.transactions_file, "w", encoding="utf-8") as file:
            json.dump(self.transactions, file, indent=4)

    def generate_id(self):
        """Generate the next transaction ID."""
        if not self.transactions:
            return "T001"

        numbers = []

        for transaction in self.transactions:
            try:
                numbers.append(int(transaction["id"][1:]))
            except (KeyError, ValueError):
                pass

        next_number = max(numbers, default=0) + 1
        return f"T{next_number:03d}"

    def add_transaction(
        self,
        transaction_type,
        amount,
        category,
        description="",
        date=None
    ):
        """Create and save a new income/expense transaction."""
        if transaction_type not in ("income", "expense"):
            raise ValueError("Transaction type must be income or expense.")

        transaction = {
            "id": self.generate_id(),
            "user": self.user_name,
            "type": transaction_type,
            "amount": float(amount),
            "category": category.title(),
            "description": description,
            "date": date or datetime.now().strftime("%Y-%m-%d")
        }

        self.transactions.append(transaction)
        self.save_transactions()

        return transaction

    def get_transactions(self):
        """Return transactions sorted by date, newest first."""
        # sorted() gives us a new list, so the stored order is not changed.
        return sorted(
            self.transactions,
            key=lambda transaction: transaction["date"],
            reverse=True
        )

    def get_transaction_by_id(self, transaction_id):
        """Find one transaction using its ID."""
        transaction_id = transaction_id.upper()

        matches = list(
            filter(
                lambda transaction: transaction["id"].upper() == transaction_id,
                self.transactions
            )
        )

        return matches[0] if matches else None

    def search_transactions(self, keyword="", transaction_type=None):
        """
        Search category, description and date.

        map() is used here to normalize the search text.
        filter() is then used to keep matching transactions.
        """
        keyword = keyword.strip().lower()

        def matches(transaction):
            searchable = " ".join(
                map(
                    str,
                    [
                        transaction.get("category", ""),
                        transaction.get("description", ""),
                        transaction.get("date", "")
                    ]
                )
            ).lower()

            keyword_match = not keyword or keyword in searchable
            type_match = (
                not transaction_type
                or transaction["type"] == transaction_type
            )

            return keyword_match and type_match

        return list(filter(matches, self.transactions))

    def get_monthly_summary(self, month):
        """Return summary information for a YYYY-MM month."""
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise ValueError("Month must be in YYYY-MM format.")

        monthly_transactions = [
            transaction
            for transaction in self.transactions
            if transaction["date"].startswith(month)
        ]

        return calculate_monthly_summary(monthly_transactions)

    def get_category_spending(self):
        """Return expense totals grouped by category."""
        return calculate_category_spending(self.transactions)

    def get_highest_expense(self):
        """Return the transaction with the largest expense amount."""
        return find_highest_expense(self.transactions)

    def delete_transaction(self, transaction_id):
        """Delete a transaction and save the changed list."""
        transaction_id = transaction_id.upper()

        old_count = len(self.transactions)

        self.transactions = [
            transaction
            for transaction in self.transactions
            if transaction["id"].upper() != transaction_id
        ]

        if len(self.transactions) == old_count:
            return False

        self.save_transactions()
        return True

    def export_report(self):
        """
        Export both CSV and TXT reports.

        CSV is useful if I later want to open the data in Excel,
        while TXT keeps a readable summary without needing any
        external Python library.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_path = self.export_dir / f"transactions_{timestamp}.csv"
        txt_path = self.export_dir / f"report_{timestamp}.txt"

        fieldnames = [
            "id",
            "user",
            "type",
            "amount",
            "category",
            "description",
            "date"
        ]

        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.get_transactions())

        report_text = build_text_report(
            self.user_name,
            self.transactions
        )

        with open(txt_path, "w", encoding="utf-8") as file:
            file.write(report_text)

        return [csv_path, txt_path]
