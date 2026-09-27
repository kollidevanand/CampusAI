import json
import os
import hashlib
import re

USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def is_valid_gmail(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@gmail\.com$"
    return re.match(pattern, email.strip().lower()) is not None


def signup_user(name, email, password):
    email = email.strip().lower()
    users = load_users()

    if not name.strip():
        return False, "Please enter your name."

    if not is_valid_gmail(email):
        return False, "Please enter a valid Gmail address (must end with @gmail.com)."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if email in users:
        return False, "An account with this Gmail already exists. Please log in."

    users[email] = {
        "name": name.strip(),
        "password": hash_password(password)
    }
    save_users(users)
    return True, "Account created successfully! Please log in."


def login_user(email, password):
    email = email.strip().lower()
    users = load_users()

    if not is_valid_gmail(email):
        return False, "Please enter a valid Gmail address (must end with @gmail.com).", None

    if email not in users:
        return False, "No account found with this Gmail. Please sign up first.", None

    if users[email]["password"] != hash_password(password):
        return False, "Incorrect password. Please try again.", None

    return True, "Login successful!", users[email]["name"]


# ============================================================
# CHANGE PASSWORD
# ============================================================
def change_password_user(email, current_password, new_password):
    """
    Verify current_password matches stored hash for email,
    then update to new_password (hashed).
    Return: (success: bool, message: str)
    """
    email = email.strip().lower()
    users = load_users()

    if email not in users:
        return False, "No account found with this email."

    if users[email]["password"] != hash_password(current_password):
        return False, "Current password is incorrect."

    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    if hash_password(new_password) == users[email]["password"]:
        return False, "New password must be different from current password."

    users[email]["password"] = hash_password(new_password)
    save_users(users)
    return True, "Password updated successfully!"


# ============================================================
# DELETE ACCOUNT
# ============================================================
def delete_user_account(email):
    """
    Permanently delete the user account from users.json.
    Return: (success: bool, message: str)
    """
    email = email.strip().lower()
    users = load_users()

    if email not in users:
        return False, "No account found with this email."

    del users[email]
    save_users(users)

    # Also clear their saved chat history file, if it exists
    try:
        from chat_storage import save_user_chats
        save_user_chats(email, {})
    except Exception:
        pass  # If chat_storage isn't available or fails, account deletion still succeeds

    return True, "Account deleted successfully."