import json
import os

CHATS_FILE = "chat_history.json"


def load_all_chats():
    if not os.path.exists(CHATS_FILE):
        return {}

    with open(CHATS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_all_chats(data):
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_user_chats(email):
    email = email.strip().lower()
    data = load_all_chats()
    return data.get(email, {})


def save_user_chats(email, chats):
    email = email.strip().lower()
    data = load_all_chats()
    data[email] = chats
    save_all_chats(data)


# ============================================================
# DELETE ONE CHAT
# ============================================================
def delete_chat(email, chat_id):
    """
    Delete only one chat belonging to the specified user.
    Other users' chats and other chats remain untouched.
    """
    email = email.strip().lower()

    data = load_all_chats()

    if email not in data:
        return False

    user_chats = data[email]

    if chat_id not in user_chats:
        return False

    del user_chats[chat_id]

    data[email] = user_chats
    save_all_chats(data)

    return True