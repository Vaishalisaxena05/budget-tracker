# ---------------------------------------------------------------
# Budget Tracker (Python + Data Analytics)
#
# A command-line budget tracker that:
#   1. Registers / logs in users (passwords stored as SHA-256 hashes)
#   2. Saves income and expense transactions in a CSV file
#   3. Shows a text summary (income, expense, savings, category-wise)
#   4. Shows analytics with pandas + matplotlib:
#        - monthly income vs expense chart
#        - category-wise expense chart
#        - insights (savings rate, average daily spend, top category)
# ---------------------------------------------------------------

import csv
import os
from datetime import date
import hashlib

# File names used for storage (both are created in the project folder)
USERS_FILE = "users.txt"        # stores: username,hashed_password
DATA_FILE = "transactions.csv"  # stores all transactions of all users


class User:
    # Represents a logged-in user

    def __init__(self, username, password):
        self.username = username
        # Double underscore makes this attribute private to the class
        self.__password = password

    def check_password(self, password):
        # Returns True if the given password matches the stored one
        return self.__password == password


def hash_pw(pw):
    # Converts a plain password into a SHA-256 hash so the real
    # password is never written to users.txt
    return hashlib.sha256(pw.encode()).hexdigest()


def register(username, password):
    # Creates a new account. Returns False if the username already exists.
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            for line in f:
                # Each line looks like: username,hash -> compare the username part
                if line.split(",")[0] == username:
                    return False
    # Append the new user (hashed password only)
    with open(USERS_FILE,
