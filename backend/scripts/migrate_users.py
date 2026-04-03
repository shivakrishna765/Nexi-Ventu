"""
migrate_users.py
----------------
Adds all columns introduced in the User model upgrade to the existing
PostgreSQL (Supabase) users table without dropping any data.

Run once:
    python -m backend.scripts.migrate_users
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from backend.database.database import engine

MIGRATIONS = [
    # column name              SQL type        default
    ("skills",                  "TEXT",         None),
    ("experience_level",        "TEXT",         None),
    ("location",                "TEXT",         None),
    ("preferred_funding_stage", "TEXT",         None),
    ("avatar_url",              "TEXT",         None),
    ("oauth_provider",          "TEXT",         None),
    ("oauth_id",                "TEXT",         None),
    ("is_admin",                "BOOLEAN",      "FALSE"),
    ("password_hash",           "TEXT",         None),   # make nullable (already TEXT, skip if exists)
]

def column_exists(conn, table, column):
    result = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table, "c": column})
    return result.fetchone() is not None

def run():
    with engine.begin() as conn:
        for col, dtype, default in MIGRATIONS:
            if column_exists(conn, "users", col):
                print(f"  [skip]  users.{col} already exists")
                continue
            default_clause = f" DEFAULT {default}" if default is not None else ""
            sql = f"ALTER TABLE users ADD COLUMN {col} {dtype}{default_clause};"
            conn.execute(text(sql))
            print(f"  [added] users.{col} {dtype}")

        # Make password_hash nullable if it isn't already (needed for OAuth users)
        conn.execute(text(
            "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"
        ))
        print("  [ok]    password_hash is now nullable")

    print("\nMigration complete. All columns are in sync with the SQLAlchemy model.")

if __name__ == "__main__":
    run()
