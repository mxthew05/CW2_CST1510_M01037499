import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user


def register_user(username: str, password: str, role: str = 'user'):
    """Register a user in the database with bcrypt password hashing."""
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')

    insert_user(username, password_hash, role)
    return True, f"User '{username}' registered successfully!"


def login_user(username: str, password: str):
    """Authenticate user against DB-stored bcrypt hash."""
    user = get_user_by_username(username)
    if not user:
        return False, "Username not found."

    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hash_bytes):
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."


def migrate_users_from_file(filepath='DATA/users.txt', conn=None):
    """Migrate users from a file into the database; returns migrated count."""
    close_conn = False
    if conn is None:
        conn = connect_database()
        close_conn = True

    path = Path(filepath)
    if not path.exists():
        if close_conn:
            conn.close()
        return 0

    cursor = conn.cursor()
    migrated_count = 0

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]
                role = parts[2] if len(parts) > 2 else 'user'
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except Exception:
                    pass

    conn.commit()
    if close_conn:
        conn.close()

    return migrated_count
