"""
Migration script: add 'customer_name' column to 'orders' table.

This uses the existing SQLAlchemy engine configured in app.config.database
and applies a dialect-aware ALTER TABLE.
"""
from sqlalchemy import text, inspect
from app.config.database import engine


def column_exists(table_name: str, column_name: str) -> bool:
    insp = inspect(engine)
    try:
        cols = [c['name'] for c in insp.get_columns(table_name)]
        return column_name in cols
    except Exception:
        return False


def main():
    dialect = engine.dialect.name
    print(f"Detected dialect: {dialect}")

    if column_exists('orders', 'customer_name'):
        print("Column 'customer_name' already exists on 'orders'. Skipping.")
        return

    ddl = None
    if dialect == 'postgresql':
        ddl = "ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_name VARCHAR(100);"
    elif dialect == 'mysql':
        # MySQL 8+ supports IF NOT EXISTS but we already checked existence above
        ddl = "ALTER TABLE orders ADD COLUMN customer_name VARCHAR(100);"
    elif dialect == 'sqlite':
        # SQLite supports simple ADD COLUMN without constraints
        ddl = "ALTER TABLE orders ADD COLUMN customer_name VARCHAR(100);"
    else:
        # Fallback for other dialects
        ddl = "ALTER TABLE orders ADD COLUMN customer_name VARCHAR(100);"

    print(f"Applying DDL: {ddl}")
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print("Column 'customer_name' added successfully.")


if __name__ == "__main__":
    main()