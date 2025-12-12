# database.py
import sqlite3
import pandas as pd


class DatabaseManager:
    def __init__(self, db_name="intelligence_platform.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                           ''')

            # Cybersecurity incidents table
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS cyber_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    resolved_date TEXT,
                    resolution_time_hours REAL

            ''')

            # Data Science datasets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    source_department TEXT NOT NULL,
                    size_mb REAL NOT NULL,
                    row_count INTEGER NOT NULL,
                    quality_score REAL,
                    last_accessed TEXT NOT NULL

            ''')

            # IT Operations tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS it_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    assignee TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    resolved_date TEXT,
                    current_stage TEXT NOT NULL

            ''')

    def load_sample_data(self):
        cyber_data = [
            ("Phishing Attempt - CEO Impersonation", "High", "Phishing", "Open", "2024-01-15", None, None),
            ("Malware Detection - Server A", "Critical", "Malware", "Resolved", "2024-01-10", "2024-01-12", 48),
            ("Suspicious Login - User XYZ", "Medium", "Unauthorized Access", "Open", "2024-01-14", None, None)
        ]

        datasets_data = [
            ("Network Logs Q4", "IT", 250.5, 1000000, 0.85, "2024-01-12"),
            ("Security Events", "Cybersecurity", 150.2, 500000, 0.92, "2024-01-14"),
            ("User Activity", "IT", 450.8, 2000000, 0.78, "2024-01-10")
        ]

        tickets_data = [
            ("Password Reset - User A", "John Smith", "Low", "Resolved", "2024-01-10", "2024-01-10", "Completed"),
            ("Server Downtime - Main DB", "Sarah Johnson", "Critical", "In Progress", "2024-01-14", None,
             "Technical Review"),
            ("Software Installation", "Mike Brown", "Medium", "Open", "2024-01-13", None, "Waiting for User")
        ]

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Insert cyber incidents if table is empty
            cursor.execute('SELECT COUNT(*) FROM cyber_incidents')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('INSERT INTO cyber_incidents VALUES (NULL,?,?,?,?,?,?,?)', cyber_data)

            # Insert datasets metadata if table is empty
            cursor.execute('SELECT COUNT(*) FROM datasets_metadata')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('INSERT INTO datasets_metadata VALUES (NULL,?,?,?,?,?,?)', datasets_data)

            # Insert IT tickets if table is empty
            cursor.execute('SELECT COUNT(*) FROM it_tickets')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('INSERT INTO it_tickets VALUES (NULL,?,?,?,?,?,?,?)', tickets_data)

    # Convenience methods to fetch tables as pandas DataFrames
    def fetch_users(self):
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql('SELECT * FROM users', conn)

    def fetch_cyber_incidents(self):
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql('SELECT * FROM cyber_incidents', conn)

    def fetch_datasets(self):
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql('SELECT * FROM datasets_metadata', conn)

    def fetch_it_tickets(self):
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql('SELECT * FROM it_tickets', conn)