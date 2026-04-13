import bcrypt
import time
from src.db import users

# -------------------------
# RATE LIMIT
# -------------------------
login_attempts = {}

def is_blocked(email):
    attempts = login_attempts.get(email, [])
    now = time.time()
    attempts = [t for t in attempts if now - t < 60]
    login_attempts[email] = attempts
    return len(attempts) >= 5

def record_attempt(email):
    login_attempts.setdefault(email, []).append(time.time())

# -------------------------
# HELPERS
# -------------------------
def sanitize_user(user):
    user.pop("password", None)
    user.pop("password_hash", None)
    return user

def has_permission(user, perm):
    return user.get("permissions", {}).get(perm, False)

# -------------------------
# AUTH
# -------------------------
def verify_user(email, password):
    if is_blocked(email):
        return None

    user = users.find_one({"email": email})

    if not user:
        record_attempt(email)
        return None

    db_password = user.get("password_hash") or user.get("password")

    if not db_password:
        record_attempt(email)
        return None

    # hashed
    if db_password.startswith("$2"):
        try:
            if bcrypt.checkpw(password.encode(), db_password.encode()):
                return sanitize_user(user)
        except:
            record_attempt(email)
            return None

    # migrate plaintext
    else:
        if password == db_password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            users.update_one(
                {"_id": user["_id"]},
                {"$set": {"password_hash": hashed, "password": None}}
            )

            user["password_hash"] = hashed
            return sanitize_user(user)

    record_attempt(email)
    return None