from pathlib import Path
import pandas as pd


def load_csv_to_table(conn, csv_path: Path, table_name: str):
    """Load a CSV into a table using pandas. Returns number of rows loaded."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    return len(df)
