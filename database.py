"""SQLite database setup and schema management for AskEstate."""
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "real_estate.db"
CSV_PATH = "data/real_estate.csv"

SCHEMA_DESCRIPTION = """
Table: listings
Columns:
  - listing_id (INTEGER): Unique ID for each property listing
  - city (TEXT): City name. Values: Austin, Denver, Seattle, Portland, Nashville
  - neighborhood (TEXT): Neighborhood name. Values: Downtown, Westside, Northpark,
    Eastbrook, Southgate, Midtown, Riverside, Hillcrest, Oakwood, Lakeside
  - property_type (TEXT): Type of property. Values: House, Condo, Townhouse, Apartment
  - bedrooms (INTEGER): Number of bedrooms (1-5)
  - bathrooms (INTEGER): Number of bathrooms
  - square_feet (INTEGER): Total square footage
  - year_built (INTEGER): Year the property was built (1950-2024)
  - price (INTEGER): Listing price in USD
  - listing_date (TEXT): Date listed, format YYYY-MM-DD
  - status (TEXT): Listing status. Values: Active, Sold, Pending
  - days_on_market (INTEGER): Days the listing has been active
"""


def init_db(force: bool = False) -> None:
    """Create the SQLite database from the CSV if it doesn't exist."""
    if Path(DB_PATH).exists() and not force:
        return
    df = pd.read_csv(CSV_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("listings", conn, if_exists="replace", index=False)
    conn.close()


def run_query(sql: str) -> pd.DataFrame:
    """Execute a SELECT query and return results as a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def get_schema() -> str:
    """Return schema description for LLM prompting."""
    return SCHEMA_DESCRIPTION.strip()
