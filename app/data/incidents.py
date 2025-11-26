import pandas as pd
from app.data.db import connect_database


def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """Insert a new incident and return its id."""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (date, incident_type, severity, status, description, reported_by)
    )
    conn.commit()
    return cursor.lastrowid


def get_all_incidents(conn):
    """Return all incidents as a pandas DataFrame."""
    df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY id DESC", conn)
    return df


def update_incident_status(conn, incident_id, new_status):
    """Update status for an incident id and return number of affected rows."""
    cursor = conn.cursor()
    cursor.execute("UPDATE cyber_incidents SET status = ? WHERE id = ?", (new_status, incident_id))
    conn.commit()
    return cursor.rowcount


def delete_incident(conn, incident_id):
    """Delete an incident and return number of affected rows."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
    conn.commit()
    return cursor.rowcount
