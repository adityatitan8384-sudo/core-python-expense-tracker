from datetime import datetime


def get_non_empty_input(prompt):
    """Keep asking until the user enters something."""
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be empty.")


def get_positive_amount(prompt):
    """Take a valid positive number from the user."""
    while True:
        try:
            amount = float(input(prompt).strip())

            if amount <= 0:
                print("Amount must be greater than 0.")
                continue

            return amount

        except ValueError:
            print("Please enter a valid number, e.g. 250 or 250.50.")


def get_date(prompt):
    """
    Validate a date entered by the user.

    Pressing Enter uses today's date because entering dates
    manually every time would be annoying for normal usage.
    """
    while True:
        value = input(prompt).strip()

        if not value:
            return datetime.now().strftime("%Y-%m-%d")

        try:
            date_object = datetime.strptime(value, "%Y-%m-%d")
            return date_object.strftime("%Y-%m-%d")

        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD.")
