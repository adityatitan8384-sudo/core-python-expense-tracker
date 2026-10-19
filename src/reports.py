from collections import defaultdict


def calculate_monthly_summary(transactions):
    """Calculate total income, expense and balance."""
    income = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction["type"] == "income"
    )

    expense = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction["type"] == "expense"
    )

    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "transaction_count": len(transactions)
    }


def calculate_category_spending(transactions):
    """
    Add expenses category by category.

    defaultdict is useful here because I don't have to check
    whether a category already exists before adding to it.
    """
    spending = defaultdict(float)

    for transaction in transactions:
        if transaction["type"] == "expense":
            spending[transaction["category"]] += transaction["amount"]

    # sorted() makes the report easier to read.
    return dict(
        sorted(
            spending.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


def find_highest_expense(transactions):
    """Find the expense with the highest amount."""
    expenses = list(
        filter(
            lambda transaction: transaction["type"] == "expense",
            transactions
        )
    )

    if not expenses:
        return None

    return max(
        expenses,
        key=lambda transaction: transaction["amount"]
    )


def build_text_report(user_name, transactions):
    """Create a plain-text report for export."""
    summary = calculate_monthly_summary(transactions)
    category_spending = calculate_category_spending(transactions)
    highest = find_highest_expense(transactions)

    lines = [
        "=" * 55,
        "                 EXPENSE TRACKER REPORT",
        "=" * 55,
        f"User: {user_name}",
        "",
        "OVERALL SUMMARY",
        "-" * 55,
        f"Total Income : ₹{summary['income']:.2f}",
        f"Total Expense: ₹{summary['expense']:.2f}",
        f"Balance      : ₹{summary['balance']:.2f}",
        f"Transactions : {summary['transaction_count']}",
        "",
        "CATEGORY-WISE SPENDING",
        "-" * 55
    ]

    if category_spending:
        for category, amount in category_spending.items():
            lines.append(f"{category:<25} ₹{amount:>10.2f}")
    else:
        lines.append("No expenses recorded.")

    lines.extend([
        "",
        "HIGHEST EXPENSE",
        "-" * 55
    ])

    if highest:
        lines.extend([
            f"Date       : {highest['date']}",
            f"Category   : {highest['category']}",
            f"Amount     : ₹{highest['amount']:.2f}",
            f"Description: {highest['description']}"
        ])
    else:
        lines.append("No expenses recorded.")

    lines.extend([
        "",
        "TRANSACTIONS",
        "-" * 55
    ])

    if transactions:
        sorted_transactions = sorted(
            transactions,
            key=lambda transaction: transaction["date"],
            reverse=True
        )

        for transaction in sorted_transactions:
            lines.append(
                f"{transaction['id']} | "
                f"{transaction['date']} | "
                f"{transaction['type'].title()} | "
                f"{transaction['category']} | "
                f"₹{transaction['amount']:.2f} | "
                f"{transaction['description']}"
            )
    else:
        lines.append("No transactions recorded.")

    return "\n".join(lines) + "\n"
