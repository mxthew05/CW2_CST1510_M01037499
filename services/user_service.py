import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user

def register_user(username, password, role='user'):
    """Register new user with password hashing."""
    user = get_user_by_username(username)
    if user:
        return False, f"User '{username}' already exists."
    
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    insert_user(username, password_hash, role)
    return True, f"User '{username}' registered successfully."

def login_user(username, password):
    """Authenticate user."""
    user = get_user_by_username(username)
    if not user:
        return False, "User not found."
    
    stored_hash = user[2]  # password_hash
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, "Login successful!"
    return False, "Incorrect password."

def migrate_users_from_file(filepath='DATA/users.txt'):
    """Migrate users from text file to database."""
    path = Path(filepath)
    if not path.exists():
        print("No users.txt found. Skipping migration.")
        return 0
    
    conn = connect_database()
    count = 0
    with open(path, 'r') as file:
        for line in file:
            if line.strip():
                username, hashed_pw = line.strip().split(',')
                if not get_user_by_username(username):
                    insert_user(username, hashed_pw)
                    count += 1
    conn.close()
    return count
