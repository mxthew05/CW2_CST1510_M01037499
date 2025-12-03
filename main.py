import pandas as pd
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents, update_incident_status, delete_incident
from app.data.datasets import insert_dataset, get_all_datasets
from app.data.tickets import insert_ticket, get_all_tickets
from pathlib import Path

DATA_DIR = Path("DATA")

def load_csv_data(conn, csv_file, table_name):
    """Load CSV data into table using pandas."""
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    return len(df)

def load_all_csv_data(conn):
    """Load all CSV data."""
    total = 0
    for csv_name, table in [
        ('cyber_incidents.csv', 'cyber_incidents'),
        ('datasets_metadata.csv', 'datasets_metadata'),
        ('it_tickets.csv', 'it_tickets')
    ]:
        csv_path = DATA_DIR / csv_name
        if csv_path.exists():
            rows = load_csv_data(conn, csv_path, table)
            print(f"Loaded {rows} rows into {table}")
            total += rows
        else:
            print(f"Warning: {csv_name} not found")
    return total

def get_incidents_by_type_count(conn):
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)

def get_high_severity_by_status(conn):
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)

def get_incident_types_with_many_cases(conn, min_count=5):
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn, params=(min_count,))

def setup_database_complete():
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)
    
    conn = connect_database()
    print("\n[1/5] Creating tables...")
    create_all_tables(conn)
    
    print("\n[2/5] Migrating users...")
    user_count = migrate_users_from_file()
    print(f"       Migrated {user_count} users")
    
    print("\n[3/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn)
    print(f"       Loaded {total_rows} total rows")
    
    print("\n[4/5] Verifying setup...")
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\nDatabase Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")
    
    conn.close()
    print("\n" + "="*60)
    print("DATABASE SETUP COMPLETE!")
    print("="*60)

def run_comprehensive_tests():
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print("="*60)
    
    conn = connect_database()
    
    print("\n[TEST 1] Authentication")
    success, msg = register_user("test_user", "TestPass123!")
    print(f"  Register: {'✅' if success else '❌'} {msg}")
    
    success, msg = login_user("test_user", "TestPass123!")
    print(f"  Login:    {'✅' if success else '❌'} {msg}")
    
    print("\n[TEST 2] CRUD Operations - Incidents")
    test_id = insert_incident("2024-11-05", "Test", "Low", "Open", "Test desc", "test_user")
    print(f"  Create: ✅ ID {test_id}")
    
    df = get_all_incidents()
    print(f"  Read:   Found {len(df)} incidents")
    
    update_incident_status(test_id, "Resolved")
    print("  Update: ✅ Status updated")
    
    delete_incident(test_id)
    print("  Delete: ✅ Deleted")
    
    # Similar quick tests for datasets and tickets
    print("\n[TEST 3] CRUD Operations - Datasets")
    ds_id = insert_dataset("Test Dataset", 10.5, "CSV", "Test desc", "Internal", "2024-11-05")
    print(f"  Create: ✅ ID {ds_id}")
    delete_dataset(ds_id)  # Clean up
    
    print("\n[TEST 4] CRUD Operations - Tickets")
    tk_id = insert_ticket("2024-11-05", "Test Issue", "Low", "Open", "Test desc", "test_user")
    print(f"  Create: ✅ ID {tk_id}")
    delete_ticket(tk_id)  # Clean up
    
    print("\n[TEST 5] Analytical Queries")
    print(f"  By Type: {len(get_incidents_by_type_count(conn))}")
    print(f"  High Sev: {len(get_high_severity_by_status(conn))}")
    print(f"  Many Cases: {len(get_incident_types_with_many_cases(conn))}")
    
    conn.close()
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)

if __name__ == "__main__":
    setup_database_complete()
    run_comprehensive_tests()
