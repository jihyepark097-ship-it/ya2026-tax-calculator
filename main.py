import functions as fn


def get_valid_input(prompt, validator, error_msg):
    while True:
        value = input(prompt)
        if validator(value):
            return value.strip()
        print(error_msg)


def handle_registration():
    print("\n--- New User Registration ---")
    user_id = get_valid_input(
        "Create User ID: ",
        fn.is_valid_user_id,
        "Invalid User ID. Cannot be empty."
    )
    ic_number = get_valid_input(
        "Enter 12-digit IC Number (no dashes): ",
        fn.is_valid_ic,
        "Invalid IC. Must be exactly 12 digits."
    )
    success, message = fn.register_user(user_id, ic_number)
    print(message)


def handle_login():
    print("\n--- User Login ---")
    user_id = get_valid_input(
        "Enter User ID: ",
        fn.is_valid_user_id,
        "Invalid User ID. Cannot be empty."
    )
    password = input("Enter Password (last 4 digits of IC): ").strip()
    authenticated, ic_number = fn.authenticate_user(user_id, password)
    if authenticated:
        print(f"Login successful! Welcome, {user_id}.")
        return user_id, ic_number
    print("Authentication failed. Invalid User ID or password.")
    return None, None


def run_tax_calculation(user_id, ic_number):
    print("\n--- YA 2026 Malaysian Personal Income Tax Calculator ---")
    test_case_input = input("Enter Test Case ID (e.g. T01-T05, or press Enter for N/A): ").strip()
    test_case_id = test_case_input if test_case_input else "N/A"

    annual_income = float(get_valid_input(
        "Enter Annual Income (RM): ",
        fn.is_valid_amount,
        "Invalid amount. Enter a non-negative number."
    ))
    total_relief = float(get_valid_input(
        "Enter Total Eligible Tax Relief (RM): ",
        fn.is_valid_amount,
        "Invalid amount. Enter a non-negative number."
    ))

    record = fn.build_tax_record(
        user_id,
        ic_number,
        annual_income,
        total_relief,
        test_case_id=test_case_id,
    )
    fn.save_tax_record(record)

    print("\n--- YA 2026 Tax Calculation Result ---")
    print(f"User ID:           {record['user_id']}")
    print(f"IC Number:         {record['ic_number']}")
    print(f"Test Case ID:      {record['test_case_id']}")
    print(f"Year of Assessment:{record['year_of_assessment']}")
    print(f"Annual Income:     RM {record['annual_income']:,.2f}")
    print(f"Total Tax Relief:  RM {record['total_relief']:,.2f}")
    print(f"Chargeable Income: RM {record['chargeable_income']:,.2f}")
    print(f"Gross Tax:         RM {record['gross_tax']:,.2f}")
    print(f"Tax Rebate:        RM {record['rebate']:,.2f}")
    print(f"Tax Payable:       RM {record['tax_payable']:,.2f}")
    print("Record saved to tax_records.csv!")

def view_saved_records(user_id=None):
    print("\n--- Stored Tax Records ---")
    df = fn.load_tax_records()
    if df.empty:
        print("No tax records found yet.")
        return
    if user_id:
        user_df = df[df["user_id"].astype(str) == str(user_id)]
        if user_df.empty:
            print(f"No tax records found for {user_id}.")
            return
        print(user_df.to_string(index=False))
    else:
        print(df.to_string(index=False))


def main():
    current_user = None
    current_ic = None

    while True:
        print("\n==============================================")
        print("   YA 2026 Malaysian Income Tax System")
        print("==============================================")
        if current_user:
            print(f"Logged in as: {current_user}")
            print("1. Calculate YA 2026 Income Tax")
            print("2. View My Tax Records")
            print("3. View All Tax Records")
            print("4. Logout")
            print("5. Exit")
            choice = input("Select an option (1-5): ").strip()

            if choice == "1":
                run_tax_calculation(current_user, current_ic)
            elif choice == "2":
                view_saved_records(current_user)
            elif choice == "3":
                view_saved_records()
            elif choice == "4":
                print(f"Logged out {current_user}.")
                current_user = None
                current_ic = None
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1 to 5.")
        else:
            print("1. Register New User")
            print("2. Login")
            print("3. Exit")
            choice = input("Select an option (1-3): ").strip()

            if choice == "1":
                handle_registration()
            elif choice == "2":
                current_user, current_ic = handle_login()
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1 to 3.")


if __name__ == "__main__":
    main()