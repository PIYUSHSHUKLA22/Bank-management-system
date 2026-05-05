"""
Bank Management System
Author: Piyush Shukla
Description: A CLI-based banking system with MySQL backend.
             Supports account creation, login, deposit, withdrawal, and transfer.
"""

import mysql.connector
import hashlib
import os
import random
import string
from datetime import datetime


# ─────────────────────────────────────────────
#  DATABASE CONNECTION
# ─────────────────────────────────────────────

def get_connection():
    """Create and return a MySQL database connection."""
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Change to your MySQL username
        password="",          # Change to your MySQL password
        database="bank_db"
    )


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def hash_password(password):
    """Hash a password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_account_number():
    """Generate a random 10-digit account number."""
    return ''.join(random.choices(string.digits, k=10))


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 45)
    print(f"   {title}")
    print("=" * 45)


def print_success(message):
    print(f"\n  ✅  {message}")


def print_error(message):
    print(f"\n  ❌  {message}")


def print_info(message):
    print(f"\n  ℹ️   {message}")


# ─────────────────────────────────────────────
#  DATABASE SETUP
# ─────────────────────────────────────────────

def setup_database():
    """
    Create the database and tables if they don't already exist.
    This runs once when you start the program for the first time.
    """
    # Connect without specifying a database first
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""           # Change to your MySQL password
    )
    cursor = conn.cursor()

    # Create the database
    cursor.execute("CREATE DATABASE IF NOT EXISTS bank_db")
    cursor.execute("USE bank_db")

    # Create accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            account_no    VARCHAR(10) UNIQUE NOT NULL,
            full_name     VARCHAR(100)       NOT NULL,
            email         VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(64)        NOT NULL,
            balance       DECIMAL(12, 2)     NOT NULL DEFAULT 0.00,
            created_at    DATETIME           NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create transactions table — stores every deposit, withdrawal, transfer
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            account_no     VARCHAR(10)  NOT NULL,
            type           ENUM('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT') NOT NULL,
            amount         DECIMAL(12, 2) NOT NULL,
            related_acc    VARCHAR(10)  DEFAULT NULL,
            timestamp      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_no) REFERENCES accounts(account_no)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print_success("Database ready.")


# ─────────────────────────────────────────────
#  ACCOUNT FUNCTIONS
# ─────────────────────────────────────────────

def create_account():
    """Register a new bank account."""
    print_header("CREATE NEW ACCOUNT")

    full_name = input("  Enter your full name     : ").strip()
    email     = input("  Enter your email         : ").strip()
    password  = input("  Create a password        : ").strip()

    if not full_name or not email or not password:
        print_error("All fields are required.")
        return

    account_no    = generate_account_number()
    password_hash = hash_password(password)

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Parameterized query — prevents SQL injection
        cursor.execute("""
            INSERT INTO accounts (account_no, full_name, email, password_hash, balance)
            VALUES (%s, %s, %s, %s, %s)
        """, (account_no, full_name, email, password_hash, 0.00))

        conn.commit()
        print_success(f"Account created successfully!")
        print(f"\n  Your Account Number : {account_no}")
        print(f"  Name               : {full_name}")
        print(f"  Please save your account number for login.\n")

    except mysql.connector.IntegrityError:
        print_error("An account with this email already exists.")
    finally:
        cursor.close()
        conn.close()


def login():
    """
    Log in with account number + password.
    Returns the account row dict on success, or None on failure.
    """
    print_header("LOGIN")

    account_no = input("  Account Number : ").strip()
    password   = input("  Password       : ").strip()

    password_hash = hash_password(password)

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM accounts
            WHERE account_no = %s AND password_hash = %s
        """, (account_no, password_hash))

        account = cursor.fetchone()

        if account:
            print_success(f"Welcome back, {account['full_name']}!")
            return account
        else:
            print_error("Invalid account number or password.")
            return None

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
#  BANKING OPERATIONS
# ─────────────────────────────────────────────

def view_balance(account):
    """Display the current balance of the logged-in account."""
    print_header("ACCOUNT BALANCE")
    print(f"\n  Account No  : {account['account_no']}")
    print(f"  Name        : {account['full_name']}")
    print(f"  Balance     : ₹ {account['balance']:,.2f}")


def deposit(account):
    """Deposit money into the account."""
    print_header("DEPOSIT MONEY")
    view_balance(account)

    try:
        amount = float(input("\n  Enter deposit amount : ₹ "))
        if amount <= 0:
            print_error("Amount must be greater than 0.")
            return account

        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Update balance
        cursor.execute("""
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_no = %s
        """, (amount, account['account_no']))

        # Log transaction
        cursor.execute("""
            INSERT INTO transactions (account_no, type, amount)
            VALUES (%s, 'DEPOSIT', %s)
        """, (account['account_no'], amount))

        conn.commit()

        # Fetch updated account data
        cursor.execute("SELECT * FROM accounts WHERE account_no = %s",
                       (account['account_no'],))
        updated = cursor.fetchone()

        print_success(f"₹ {amount:,.2f} deposited successfully!")
        print(f"  New Balance : ₹ {updated['balance']:,.2f}")
        return updated

    except ValueError:
        print_error("Please enter a valid number.")
        return account
    finally:
        cursor.close()
        conn.close()


def withdraw(account):
    """Withdraw money from the account."""
    print_header("WITHDRAW MONEY")
    view_balance(account)

    try:
        amount = float(input("\n  Enter withdrawal amount : ₹ "))
        if amount <= 0:
            print_error("Amount must be greater than 0.")
            return account

        if amount > float(account['balance']):
            print_error("Insufficient balance.")
            return account

        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_no = %s
        """, (amount, account['account_no']))

        cursor.execute("""
            INSERT INTO transactions (account_no, type, amount)
            VALUES (%s, 'WITHDRAWAL', %s)
        """, (account['account_no'], amount))

        conn.commit()

        cursor.execute("SELECT * FROM accounts WHERE account_no = %s",
                       (account['account_no'],))
        updated = cursor.fetchone()

        print_success(f"₹ {amount:,.2f} withdrawn successfully!")
        print(f"  New Balance : ₹ {updated['balance']:,.2f}")
        return updated

    except ValueError:
        print_error("Please enter a valid number.")
        return account
    finally:
        cursor.close()
        conn.close()


def transfer(account):
    """Transfer money to another account."""
    print_header("TRANSFER MONEY")
    view_balance(account)

    target_acc = input("\n  Enter recipient's Account Number : ").strip()

    if target_acc == account['account_no']:
        print_error("Cannot transfer to your own account.")
        return account

    try:
        amount = float(input("  Enter transfer amount : ₹ "))
        if amount <= 0:
            print_error("Amount must be greater than 0.")
            return account

        if amount > float(account['balance']):
            print_error("Insufficient balance.")
            return account

        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if recipient exists
        cursor.execute("SELECT * FROM accounts WHERE account_no = %s", (target_acc,))
        recipient = cursor.fetchone()

        if not recipient:
            print_error("Recipient account not found.")
            return account

        # Deduct from sender
        cursor.execute("""
            UPDATE accounts SET balance = balance - %s WHERE account_no = %s
        """, (amount, account['account_no']))

        # Add to recipient
        cursor.execute("""
            UPDATE accounts SET balance = balance + %s WHERE account_no = %s
        """, (amount, target_acc))

        # Log both sides of the transaction
        cursor.execute("""
            INSERT INTO transactions (account_no, type, amount, related_acc)
            VALUES (%s, 'TRANSFER_OUT', %s, %s)
        """, (account['account_no'], amount, target_acc))

        cursor.execute("""
            INSERT INTO transactions (account_no, type, amount, related_acc)
            VALUES (%s, 'TRANSFER_IN', %s, %s)
        """, (target_acc, amount, account['account_no']))

        conn.commit()

        cursor.execute("SELECT * FROM accounts WHERE account_no = %s",
                       (account['account_no'],))
        updated = cursor.fetchone()

        print_success(f"₹ {amount:,.2f} transferred to {recipient['full_name']} ({target_acc})")
        print(f"  New Balance : ₹ {updated['balance']:,.2f}")
        return updated

    except ValueError:
        print_error("Please enter a valid number.")
        return account
    finally:
        cursor.close()
        conn.close()


def view_transactions(account):
    """Show the last 10 transactions for the account."""
    print_header("TRANSACTION HISTORY")
    print(f"  Account : {account['account_no']} | {account['full_name']}\n")

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT type, amount, related_acc, timestamp
            FROM transactions
            WHERE account_no = %s
            ORDER BY timestamp DESC
            LIMIT 10
        """, (account['account_no'],))

        rows = cursor.fetchall()

        if not rows:
            print_info("No transactions found.")
            return

        print(f"  {'Type':<15} {'Amount':>12}  {'Related Acc':<12}  {'Date & Time'}")
        print("  " + "-" * 60)

        for row in rows:
            t_type  = row['type']
            amount  = f"₹ {row['amount']:,.2f}"
            related = row['related_acc'] or "—"
            time_   = row['timestamp'].strftime("%d %b %Y  %H:%M")

            # Show +/- based on transaction type
            sign = "+" if t_type in ('DEPOSIT', 'TRANSFER_IN') else "-"
            print(f"  {t_type:<15} {sign}{amount:>12}  {related:<12}  {time_}")

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
#  MENUS
# ─────────────────────────────────────────────

def dashboard(account):
    """The main menu shown after login."""
    while True:
        print_header(f"DASHBOARD — {account['full_name']}")
        print("  1. View Balance")
        print("  2. Deposit Money")
        print("  3. Withdraw Money")
        print("  4. Transfer Money")
        print("  5. Transaction History")
        print("  6. Logout")
        print()

        choice = input("  Choose an option (1-6): ").strip()

        if   choice == '1': view_balance(account)
        elif choice == '2': account = deposit(account)
        elif choice == '3': account = withdraw(account)
        elif choice == '4': account = transfer(account)
        elif choice == '5': view_transactions(account)
        elif choice == '6':
            print_info("Logged out successfully.")
            break
        else:
            print_error("Invalid choice. Please enter 1–6.")

        input("\n  Press Enter to continue...")


def main_menu():
    """The starting menu of the application."""
    setup_database()

    while True:
        print_header("BANK MANAGEMENT SYSTEM")
        print("  1. Create New Account")
        print("  2. Login")
        print("  3. Exit")
        print()

        choice = input("  Choose an option (1-3): ").strip()

        if choice == '1':
            create_account()
            input("\n  Press Enter to continue...")

        elif choice == '2':
            account = login()
            if account:
                dashboard(account)

        elif choice == '3':
            print("\n  Thank you for using Bank Management System. Goodbye!\n")
            break

        else:
            print_error("Invalid choice. Please enter 1, 2, or 3.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main_menu()
