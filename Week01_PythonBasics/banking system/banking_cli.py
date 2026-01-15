from banking_system import Bank

DEFAULT_FILE = "bank_data.json"

bank = Bank()

while True:
    print(
        """
=== BANK MENU ===
1. Create Account
2. View Account
3. Deposit
4. Withdraw
5. Transfer
6. Save Bank to File
7. Load Bank from File
8. Exit
"""
    )

    user_input = input("Choose an option: ").strip()

    # Validate input: must be one of "1" through "8"
    if user_input not in {"1", "2", "3", "4", "5", "6", "7", "8"}:
        print("Must make a valid selection (1-8).")
        continue

    # Now branch based on string input
    if user_input == "1":
        print("Create account selected")
        user_name = input("Enter your full name: ")
        initial_deposit = float(input("Enter your initial deposit: "))
        success, message = bank.create_account(user_name, initial_deposit)
        if success:
            print(message)
        else:
            print("ERROR: " + message)

    # view account block
    elif user_input == "2":
        print("View account selected")
        account_number = input("Please enter your bank account number:")
        try:
            account_number = int(account_number)
        except ValueError:
            print("ERROR: Account number must be a valid integer")
            continue
        success, message = bank.get_account(account_number)
        if success:
            print(message)
        else:
            print("ERROR: " + message)

    # make a deposit block
    elif user_input == "3":
        print("Deposit selected")
        account_number = input("Please enter your bank account number:")
        try:
            account_number = int(account_number)
        except ValueError:
            print("ERROR: Account number must be a valid integer")
            continue
        amount = input("input amount to be deposited: ")
        try:
            amount = float(amount)
        except ValueError:
            print("ERROR: Deposit amount must be a valid number")
            continue

        success, account = bank.get_account(account_number)
        if not success:
            print("ERROR: " + account)
            continue
        success, message = account.deposit(amount)
        if success:
            print(message)
        else:
            print("ERROR: " + message)

    # make withdrawal block
    elif user_input == "4":
        print("Withdraw selected")
        account_number = input("Please enter your bank account number:")
        try:
            account_number = int(account_number)
        except ValueError:
            print("ERROR: Account number must be a valid integer")
            continue
        amount = input("input amount to withdraw: ")
        try:
            amount = float(amount)
        except ValueError:
            print("ERROR: withdrawal amount must be a valid number")
            continue

        success, account = bank.get_account(account_number)
        if not success:
            print("ERROR: " + account)
            continue
        success, message = account.withdraw(amount)
        if success:
            print(message)
        else:
            print("ERROR: " + message)

    # transfer block
    elif user_input == "5":
        print("Transfer selected")
        account_number1 = input("Please enter account for withdrawal:")
        try:
            account_number1 = int(account_number1)
        except ValueError:
            print("ERROR: Account number must be a valid integer")
            continue
        account_number2 = input("Please enter account for deposit:")
        try:
            account_number2 = int(account_number2)
        except ValueError:
            print("ERROR: Account number must be a valid integer")
            continue
        amount = input("input transfer amount: ")
        try:
            amount = float(amount)
        except ValueError:
            print("ERROR: transfer amount must be a valid number")
            continue
        if amount <= 0:
            print("ERROR: Cannot transfer amount smaller than zero")
            continue

        success, account1 = bank.get_account(account_number1)
        if not success:
            print("ERROR: " + account1)
            continue

        success, account2 = bank.get_account(account_number2)
        if not success:
            print("ERROR: " + account2)
            continue

        success, message = bank.transfer(account_number1, account_number2, amount)
        if success:
            print(message)
        else:
            print("ERROR: " + message)

    elif user_input == "6":
        print("Save bank to file selected")
        success, message = bank.save_to_file(DEFAULT_FILE)
        if success:
            print(f"Bank data saved to {DEFAULT_FILE}")
        else:
            print("ERROR: " + message)

    elif user_input == "7":
        print("Load bank from file selected")
        success, message = bank.load_from_file(DEFAULT_FILE)
        if success:
            print(message)
        else:
            print("ERROR: " + message)

    elif user_input == "8":
        print("Exit selected")
        break
