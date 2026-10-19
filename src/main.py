from tracker import ExpenseTracker
from utils import get_non_empty_input, get_positive_amount, get_date


def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 45)
    print("              EXPENSE TRACKER")
    print("=" * 45)
    print("1. Add Income")
    print("2. Add Expense")
    print("3. View Transactions")
    print("4. Search Transactions")
    print("5. Monthly Summary")
    print("6. Category-wise Spending")
    print("7. Highest Expense")
    print("8. Export Report")
    print("9. Delete Transaction")
    print("10. Exit")
    print("=" * 45)


def add_transaction(tracker, transaction_type):
    """Take transaction details from the user and save them."""
    print(f"\n--- Add {transaction_type.title()} ---")

    amount = get_positive_amount("Enter amount: ")
    category = get_non_empty_input("Enter category: ")
    description = input("Enter description (optional): ").strip()
    date = get_date("Enter date (YYYY-MM-DD, press Enter for today): ")

    transaction = tracker.add_transaction(
        transaction_type=transaction_type,
        amount=amount,
        category=category,
        description=description,
        date=date
    )

    print(f"Transaction added successfully. ID: {transaction['id']}")


def print_transactions(transactions):
    """Print transactions in a simple table."""
    if not transactions:
        print("\nNo transactions found.")
        return

    print("\n" + "-" * 95)
    print(f"{'ID':<5}{'Date':<13}{'Type':<10}{'Category':<18}"
          f"{'Amount':>12}  Description")
    print("-" * 95)

    for transaction in transactions:
        description = transaction["description"][:28]
        print(
            f"{transaction['id']:<5}"
            f"{transaction['date']:<13}"
            f"{transaction['type'].title():<10}"
            f"{transaction['category'][:17]:<18}"
            f"₹{transaction['amount']:>10.2f}  "
            f"{description}"
        )

    print("-" * 95)


def search_transactions(tracker):
    """Search by keyword and optionally filter by type."""
    print("\n--- Search Transactions ---")
    keyword = input(
        "Enter keyword (category/description/date, blank for all): "
    ).strip()

    transaction_type = input(
        "Type filter (income/expense, blank for all): "
    ).strip().lower()

    if transaction_type not in ("", "income", "expense"):
        print("Invalid type. Use income, expense or leave it blank.")
        return

    results = tracker.search_transactions(
        keyword=keyword,
        transaction_type=transaction_type or None
    )

    print_transactions(results)


def monthly_summary(tracker):
    """Display income, expense and balance for a selected month."""
    print("\n--- Monthly Summary ---")
    month = input("Enter month (YYYY-MM, e.g. 2026-10): ").strip()

    try:
        summary = tracker.get_monthly_summary(month)
    except ValueError:
        print("Invalid month. Please use YYYY-MM format.")
        return

    print(f"\nSummary for {month}")
    print(f"Total Income : ₹{summary['income']:.2f}")
    print(f"Total Expense: ₹{summary['expense']:.2f}")
    print(f"Balance      : ₹{summary['balance']:.2f}")
    print(f"Transactions : {summary['transaction_count']}")


def category_spending(tracker):
    """Show total expense for each category."""
    print("\n--- Category-wise Spending ---")
    spending = tracker.get_category_spending()

    if not spending:
        print("No expense data available.")
        return

    print("-" * 40)
    print(f"{'Category':<25}{'Amount':>12}")
    print("-" * 40)

    for category, amount in spending.items():
        print(f"{category:<25}₹{amount:>10.2f}")

    print("-" * 40)


def highest_expense(tracker):
    """Show the single highest expense."""
    transaction = tracker.get_highest_expense()

    if transaction is None:
        print("\nNo expenses found.")
        return

    print("\n--- Highest Expense ---")
    print(f"ID         : {transaction['id']}")
    print(f"Date       : {transaction['date']}")
    print(f"Category   : {transaction['category']}")
    print(f"Amount     : ₹{transaction['amount']:.2f}")
    print(f"Description: {transaction['description']}")


def export_report(tracker):
    """Export transactions and a summary to files."""
    print("\n--- Export Report ---")
    exported_files = tracker.export_report()

    print("Report exported successfully:")
    for file_path in exported_files:
        print(f"- {file_path}")


def delete_transaction(tracker):
    """Delete a transaction after confirmation."""
    print("\n--- Delete Transaction ---")
    transaction_id = input("Enter transaction ID: ").strip()

    transaction = tracker.get_transaction_by_id(transaction_id)

    if transaction is None:
        print("Transaction not found.")
        return

    print_transactions([transaction])

    confirm = input("Delete this transaction? (y/n): ").strip().lower()

    if confirm == "y":
        if tracker.delete_transaction(transaction_id):
            print("Transaction deleted.")
        else:
            print("Could not delete transaction.")
    else:
        print("Delete cancelled.")


def main():
    tracker = ExpenseTracker()

    print("\nWelcome to Expense Tracker")
    print(f"Current user: {tracker.user_name}")

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                add_transaction(tracker, "income")

            elif choice == "2":
                add_transaction(tracker, "expense")

            elif choice == "3":
                print_transactions(tracker.get_transactions())

            elif choice == "4":
                search_transactions(tracker)

            elif choice == "5":
                monthly_summary(tracker)

            elif choice == "6":
                category_spending(tracker)

            elif choice == "7":
                highest_expense(tracker)

            elif choice == "8":
                export_report(tracker)

            elif choice == "9":
                delete_transaction(tracker)

            elif choice == "10":
                print("\nThanks for using Expense Tracker.")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 10.")

        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Exiting safely.")
            break
        except Exception as error:
            # A final safety net so one unexpected input does not kill the app.
            print(f"Something went wrong: {error}")


if __name__ == "__main__":
    main()
