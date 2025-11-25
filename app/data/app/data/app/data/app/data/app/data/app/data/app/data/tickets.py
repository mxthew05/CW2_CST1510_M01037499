import pandas as pd
from app.data.db import connect_database

def insert_ticket(date, issue_type, priority, status, description, assigned_to=None):
    """Insert new IT ticket."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets 
        (date, issue_type, priority, status, description, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, issue_type, priority, status, description, assigned_to))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

def get_all_tickets():
    """Get all tickets as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", conn)
    conn.close()
    return df

def update_ticket_status(ticket_id, new_status):
    """Update ticket status."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE it_tickets SET status = ? WHERE id = ?", (new_status, ticket_id))
    conn.commit()
    conn.close()

def delete_ticket(ticket_id):
    """Delete ticket."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()