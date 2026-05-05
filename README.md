# 🏦 Bank Management System

A command-line banking application built with **Python** and **MySQL**.  
Supports account creation, secure login, deposits, withdrawals, fund transfers, and transaction history.

---

## ✨ Features

- **Create Account** — Register with name, email, and password
- **Secure Login** — Passwords stored as SHA-256 hashes (never in plain text)
- **Deposit & Withdraw** — Update balance with full validation
- **Fund Transfer** — Send money to any other account in the system
- **Transaction History** — View last 10 transactions with type, amount, and timestamp
- **SQL Injection Prevention** — All queries use parameterized statements
- **Referential Integrity** — Foreign key constraints enforced across tables

---

## 🛠️ Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Language  | Python 3.x              |
| Database  | MySQL                   |
| DB Driver | mysql-connector-python  |
| Security  | SHA-256 password hashing, parameterized SQL queries |

---

## 📁 Project Structure

```
bank-management-system/
├── bank.py            # Main application — all logic lives here
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

---

## ⚙️ Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/PIYUSHSHUKLA22/bank-management-system.git
cd bank-management-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure MySQL credentials  
Open `bank.py` and update the two places with your MySQL username and password:

```python
# In get_connection():
conn = mysql.connector.connect(
    host="localhost",
    user="root",       # ← your MySQL username
    password="",       # ← your MySQL password
    database="bank_db"
)

# In setup_database():
conn = mysql.connector.connect(
    host="localhost",
    user="root",       # ← your MySQL username
    password=""        # ← your MySQL password
)
```

### 4. Run the application
```bash
python bank.py
```

> The database and tables are created **automatically** on first run. No manual SQL setup needed.

---

## 🗄️ Database Schema

### `accounts` table
| Column        | Type           | Description                        |
|---------------|----------------|------------------------------------|
| id            | INT (PK)       | Auto-increment primary key         |
| account_no    | VARCHAR(10)    | Unique 10-digit account number     |
| full_name     | VARCHAR(100)   | Account holder's name              |
| email         | VARCHAR(100)   | Unique email address               |
| password_hash | VARCHAR(64)    | SHA-256 hashed password            |
| balance       | DECIMAL(12,2)  | Current account balance            |
| created_at    | DATETIME       | Account creation timestamp         |

### `transactions` table
| Column      | Type                                               | Description                        |
|-------------|----------------------------------------------------|------------------------------------|
| id          | INT (PK)                                           | Auto-increment primary key         |
| account_no  | VARCHAR(10) (FK → accounts)                        | Account that made the transaction  |
| type        | ENUM(DEPOSIT, WITHDRAWAL, TRANSFER_IN, TRANSFER_OUT) | Transaction type                 |
| amount      | DECIMAL(12,2)                                      | Amount involved                    |
| related_acc | VARCHAR(10)                                        | Other account (for transfers)      |
| timestamp   | DATETIME                                           | When the transaction occurred      |

---

## 📸 Demo

```
=============================================
   BANK MANAGEMENT SYSTEM
=============================================
  1. Create New Account
  2. Login
  3. Exit

  Choose an option (1-3): 2

=============================================
   LOGIN
=============================================
  Account Number : 3847291056
  Password       : ********

  ✅  Welcome back, Piyush Shukla!

=============================================
   DASHBOARD — Piyush Shukla
=============================================
  1. View Balance
  2. Deposit Money
  3. Withdraw Money
  4. Transfer Money
  5. Transaction History
  6. Logout
```

---

## 🔒 Security Notes

- Passwords are **never stored in plain text** — SHA-256 hashing is applied before saving
- All SQL queries use **parameterized statements** (`%s` placeholders) to prevent SQL injection
- **Foreign key constraints** ensure transaction records always reference valid accounts

---

## 👨‍💻 Author

**Piyush Shukla**  
B.Tech CS (AI/ML) — Maharana Pratap Group of Institutions, Kanpur  
[GitHub](https://github.com/PIYUSHSHUKLA22) · [LinkedIn](https://linkedin.com/in/piyush-shukla-29152132a)
