from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents
from pathlib import Path
import pandas as pd


def setup_database_complete():
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)

    conn = connect_database()

    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)

    print("\n[3/5] Migrating users from users.txt...")
    migrated = migrate_users_from_file(conn=conn)
    print(f"       Migrated {migrated} users")

    # optional CSV loading (if files exist)
    data_dir = Path("DATA")
    print("\n[4/5] Loading CSV data (if available)...")
    for csv_file, table in [
        (data_dir / "cyber_incidents.csv", "cyber_incidents"),
        (data_dir / "datasets_metadata.csv", "datasets_metadata"),
        (data_dir / "it_tickets.csv", "it_tickets")
    ]:
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                df.to_sql(name=table, con=conn, if_exists='append', index=False)
                print(f"      Loaded {len(df)} rows from {csv_file.name} into {table}")
            except Exception as e:
                print(f"      Failed to load {csv_file.name}: {e}")
        else:
            print(f"      Skipping {csv_file.name} (not found)")

    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
        except Exception:
            count = 0
        print(f"{table:<25} {count:<15}")

    conn.close()

    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")
    print("="*60)


def main():
    print("Welcome — Week 8 DB demo")
    setup_database_complete()

    # quick test: register + login
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)
    success, msg = login_user("alice", "SecurePass123!")
    print(msg)

    # create a test incident (if users exist)
    conn = connect_database()
    create_all_tables(conn)
    try:
        incident_id = insert_incident(conn, "2024-11-05", "Phishing", "High", "Open", "Suspicious email detected", "alice")
        print(f"Created incident #{incident_id}")
    except Exception as e:
        print(f"Couldn't create incident: {e}")

    df = get_all_incidents(conn)
    print(f"Total incidents: {len(df)}")
    conn.close()


if __name__ == "__main__":
    main()
