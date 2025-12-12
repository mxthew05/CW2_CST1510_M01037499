#!/usr/bin/env python3
"""
Secure Authentication & File Persistence
- bcrypt for hashing (includes salt + cost factor)
- atomic writes for file persistence
- simple username,hashed_password CSV: username,hashed_password
- minimal, clear functions for register / login / change password
"""

import os
import bcrypt
import tempfile
import argparse
import getpass

USERS_FILE = "users.txt"
BCRYPT_ROUNDS = 12  # cost factor; increase with time if needed


def ensure_users_file():
    """Ensure users file exists and has safe permissions (rw-------)."""
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "a", encoding="utf-8").close()
        try:
            os.chmod(USERS_FILE, 0o600)
        except PermissionError:
            # best effort; some platforms don't allow chmod
            pass




def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt and return utf-8 string."""
    pw_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def load_users() -> dict:
    """
    Load users from file.
    Returns dict: {username: hashed_password}
    """
    ensure_users_file()
    users = {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # split only on the first comma to allow hashes that may include commas
            try:
                username, hashed = line.split(",", 1)
            except ValueError:
                continue
            users[username] = hashed
    return users


def write_users_atomic(users: dict):
    """
    Atomically write the users dict to USERS_FILE.
    Uses a temporary file and os.replace for atomicity.
    """
    dirpath = os.path.dirname(os.path.abspath(USERS_FILE)) or "."
    fd, temp_path = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            for u, h in users.items():
                tmp.write(f"{u},{h}\n")
        # replace target file atomically
        os.replace(temp_path, USERS_FILE)
        try:
            os.chmod(USERS_FILE, 0o600)
        except PermissionError:
            pass
    finally:
        # cleanup if anything failed before replace
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def register_user(username: str, password: str) -> bool:
    """
    Register a new user.
    Returns True on success, False if user exists or invalid input.
    """
    if not username or "," in username or len(username) > 150:
        return False
    if len(password) < 8:
        # require at least 8 chars; you can raise this if you want stricter policy
        return False

    users = load_users()
    if username in users:
        return False

    hashed = hash_password(password)
    users[username] = hashed
    write_users_atomic(users)
    return True


def login_user(username: str, password: str) -> bool:
    """Verify a login. Returns True if credentials match."""
    users = load_users()
    hashed = users.get(username)
    if not hashed:
        return False
    return verify_password(password, hashed)


def change_password(username: str, old_password: str, new_password: str) -> bool:
    """Change a user's password after verifying old password. Returns True on success."""
    if len(new_password) < 8:
        return False
    users = load_users()
    hashed = users.get(username)
    if not hashed:
        return False
    if not verify_password(old_password, hashed):
        return False
    users[username] = hash_password(new_password)
    write_users_atomic(users)
    return True


def cli_register():
    username = input("username: ").strip()
    password = getpass.getpass("password: ")
    confirm = getpass.getpass("confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        return
    ok = register_user(username, password)
    if ok:
        print(f"User '{username}' registered.")
    else:
        print("Register failed. Username exists, invalid username, or weak password.")


def cli_login():
    username = input("username: ").strip()
    password = getpass.getpass("password: ")
    ok = login_user(username, password)
    if ok:
        print("Login successful.")
    else:
        print("Login failed.")


def cli_change_password():
    username = input("username: ").strip()
    old = getpass.getpass("old password: ")
    new = getpass.getpass("new password: ")
    confirm = getpass.getpass("confirm new password: ")
    if new != confirm:
        print("New passwords do not match.")
        return
    ok = change_password(username, old, new)
    if ok:
        print("Password changed.")
    else:
        print("Password change failed.")


def main():
    parser = argparse.ArgumentParser(description="Simple auth CLI")
    parser.add_argument("action", choices=["register", "login", "changepw"], help="action")
    args = parser.parse_args()

    if args.action == "register":
        cli_register()
    elif args.action == "login":
        cli_login()
    elif args.action == "changepw":
        cli_change_password()


if __name__ == "__main__":
    main()