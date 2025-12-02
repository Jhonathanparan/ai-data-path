import json


class Account:
    def __init__(self, owner, account_number, initial_balance=0):
        self.owner = owner
        self.account_number = account_number
        self.balance = initial_balance

    def __str__(self):
        return (
            f"Account {self.account_number}: Owner={self.owner}, Balance={self.balance}"
        )

    def to_dict(self):
        return {
            "owner": self.owner,
            "account_number": self.account_number,
            "balance": self.balance,
        }

    # classmethod pulling dict from json file
    @classmethod
    def from_dict(cls, data):
        owner = data["owner"]
        account_number = data["account_number"]
        balance = data["balance"]

        return cls(owner, account_number, balance)

    # makes a deposit to an account
    def deposit(self, amount):
        if amount <= 0:
            return False, "Cannot deposit negative amount"
        else:
            self.balance += amount
            return True, self.balance

    # makes a withdrawel from an account
    def withdraw(self, amount):
        if amount <= 0:
            return False, "Cannot withdraw negative amounts"
        elif amount > self.balance:
            return False, "Insufficient funds"
        else:
            self.balance -= amount
            return True, self.balance


class Bank:
    def __init__(self):
        self.accounts = {}
        self.next_account_number = 1

    # creates accounts using Account
    def create_account(self, name, initial_deposit):
        if initial_deposit < 0:
            return False, "Cannot deposit negative amount"
        else:
            account_number = self.next_account_number
            account = Account(name, account_number, initial_deposit)
            self.accounts[account_number] = account
            self.next_account_number += 1
            return True, account

    # gets account information
    def get_account(self, account_number):
        if account_number in self.accounts:
            return True, self.accounts[account_number]
        else:
            return False, "Account not found"

    # transfers from one account to another
    def transfer(self, from_acct, to_acct, amount):
        if from_acct not in self.accounts:
            return False, "Origin account doesn't exist"
        if to_acct not in self.accounts:
            return False, "Destination account doesn't exist"

        if amount <= 0:
            return False, "Transfer amount must be positive"

        success, result = self.accounts[from_acct].withdraw(amount)
        if not success:
            return False, result

        success, _ = self.accounts[to_acct].deposit(amount)
        return True, "Transfer successful"

    # saves bank data to json file
    def save_to_file(self, file_name):
        account_dicts = []
        for account in self.accounts.values():
            account_dicts.append(account.to_dict())
        bank_data = {
            "accounts": account_dicts,
            "next_account_number": self.next_account_number,
        }
        with open(file_name, "w") as f:
            json.dump(bank_data, f, indent=2)

        return True, "Bank data stored successfully"

    def load_from_file(self, file_name):
        try:
            with open(file_name, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return None
        self.accounts = {}
        for account in data["accounts"]:
            returned_account = Account.from_dict(account)
            self.accounts[returned_account.account_number] = returned_account

        self.next_account_number = data["next_account_number"]
