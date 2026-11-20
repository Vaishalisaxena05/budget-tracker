import csv
import os
from datetime import date
import hashlib

USERS_FILE = "users.txt"
DATA_FILE = "transactions.csv"


class User:
    def __init__(self, username, password):
        self.username = username
        self.__password = password

    def check_password(self, password):
        return self.__password == password


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def register(username, password):
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            for line in f:
                if line.split(",")[0] == username:
                    return False
    with open(USERS_FILE, "a") as f:
        f.write(f"{username},{hash_pw(password)}\n")
    return True


def login(username, password):
    if not os.path.exists(USERS_FILE):
        return None
    with open(USERS_FILE) as f:
        for line in f:
            if not line.strip():
                continue
            name, stored = line.strip().split(",")
            if name == username and stored == hash_pw(password):
                return User(username, password)
    return None


FIELDS = ["username", "date", "type", "category", "amount", "note"]


def add_transaction(username, kind, category, amount, note=""):
    if kind not in ("income", "expense"):
        raise ValueError("kind income ya expense hona chahiye")
    if amount <= 0:
        raise ValueError("amount 0 se bada hona chahiye")
    new_file = not os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(FIELDS)
        writer.writerow([username, date.today(), kind, category.title(), amount, note])


def get_transactions(username):
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline="") as f:
        return [r for r in csv.DictReader(f) if r["username"] == username]


def summary(username):
    rows = get_transactions(username)
    income = sum(float(r["amount"]) for r in rows if r["type"] == "income")
    expense = sum(float(r["amount"]) for r in rows if r["type"] == "expense")
    by_cat = {}
    for r in rows:
        if r["type"] == "expense":
            by_cat[r["category"]] = by_cat.get(r["category"], 0) + float(r["amount"])
    print(f"Income : {income:.2f}")
    print(f"Expense: {expense:.2f}")
    print(f"Savings: {income - expense:.2f}")
    print("Category-wise kharcha:")
    for cat, amt in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {amt:.2f}")


def analytics(username):
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
    except ImportError:
        print("Pehle chalao: pip install pandas matplotlib")
        return

    rows = get_transactions(username)
    if not rows:
        print("Abhi koi data nahi hai")
        return

    df = pd.DataFrame(rows)
    df["amount"] = df["amount"].astype(float)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = df.pivot_table(index="month", columns="type",
                             values="amount", aggfunc="sum", fill_value=0)
    print(monthly)
    monthly.plot(kind="bar")
    plt.title("Monthly income vs expense")
    plt.ylabel("Rs.")
    plt.tight_layout()
    plt.show()

    exp = df[df["type"] == "expense"].groupby("category")["amount"].sum().sort_values()
    if not exp.empty:
        exp.plot(kind="barh")
        plt.title("Category-wise expense")
        plt.tight_layout()
        plt.show()
    total_income = df[df["type"] == "income"]["amount"].sum()
    total_expense = df[df["type"] == "expense"]["amount"].sum()
    savings = total_income - total_expense
    rate = (savings / total_income * 100) if total_income else 0
    total_days = (df["date"].max() - df["date"].min()).days + 1

    print("\n--- INSIGHTS ---")
    print(f"Total income  : Rs.{total_income:.0f}")
    print(f"Total expense : Rs.{total_expense:.0f}")
    print(f"Savings       : Rs.{savings:.0f} ({rate:.1f}%)")
    print(f"Avg daily spend: Rs.{total_expense / total_days:.0f}")
    if not exp.empty:
        print(f"Top category  : {exp.idxmax()} (Rs.{exp.max():.0f})")

analytics("vaishali")