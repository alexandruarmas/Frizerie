"""
Automate recreating a SQLite table with new constraints, preserving data.
Usage: python recreate_table_with_constraints.py <table_name>
"""
import sys
from sqlalchemy import create_engine, MetaData, Table
from config.database import SQLALCHEMY_DATABASE_URL

if len(sys.argv) != 2:
    print("Usage: python recreate_table_with_constraints.py <table_name>")
    sys.exit(1)

table_name = sys.argv[1]
engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

if table_name not in metadata.tables:
    print(f"Table '{table_name}' does not exist in the database.")
    sys.exit(1)

# 1. Rename the old table
temp_table = f"{table_name}_old"
with engine.connect() as conn:
    print(f"Renaming {table_name} to {temp_table}...")
    conn.execute(f"ALTER TABLE {table_name} RENAME TO {temp_table}")
    conn.commit()

# 2. Create the new table (with constraints) using SQLAlchemy model
table = metadata.tables[table_name]
print(f"Creating new {table_name} table with constraints...")
table.create(bind=engine)

# 3. Copy data from old table to new table
with engine.connect() as conn:
    # Get columns that exist in both tables
    pragma = conn.execute(f"PRAGMA table_info({temp_table})").fetchall()
    old_columns = [row[1] for row in pragma]
    pragma_new = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    new_columns = [row[1] for row in pragma_new]
    common_columns = [col for col in old_columns if col in new_columns]
    columns_csv = ', '.join(common_columns)
    print(f"Copying data for columns: {columns_csv}")
    conn.execute(f"INSERT INTO {table_name} ({columns_csv}) SELECT {columns_csv} FROM {temp_table}")
    conn.commit()

# 4. Drop the old table
with engine.connect() as conn:
    print(f"Dropping old table {temp_table}...")
    conn.execute(f"DROP TABLE {temp_table}")
    conn.commit()

print(f"Table {table_name} recreated with new constraints and data preserved.") 