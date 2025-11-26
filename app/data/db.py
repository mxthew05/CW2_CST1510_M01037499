import sqlite3
from pathlib import Path

# Database location - keep DATA directory in project root
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

# Ensure DATA directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def connect_database(db_path: Path = DB_PATH):
    """Return a sqlite3 connection to the project database file."""
    return sqlite3.connect(str(db_path))
