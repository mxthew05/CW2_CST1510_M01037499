import pandas as pd
from app.data.db import connect_database

def insert_dataset(dataset_name, size_mb, format, description, source, created_date):
    """Insert new dataset metadata."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, size_mb, format, description, source, created_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, size_mb, format, description, source, created_date))
    conn.commit()
    dataset_id = cursor.lastrowid
    conn.close()
    return dataset_id

def get_all_datasets():
    """Get all datasets as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
    conn.close()
    return df

def update_dataset_description(dataset_id, new_description):
    """Update dataset description."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE datasets_metadata SET description = ? WHERE id = ?", (new_description, dataset_id))
    conn.commit()
    conn.close()

def delete_dataset(dataset_id):
    """Delete dataset metadata."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()
    conn.close()