"""
migrate_all.py
--------------
Idempotent migration: adds any missing columns to ALL tables so the
live Supabase schema matches the current SQLAlchemy models.

Run once:
    python -m backend.scripts.migrate_all
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from backend.database.database import engine


def col_exists(conn, table, column):
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table, "c": column})
    return r.fetchone() is not None


def add_col(conn, table, column, dtype, default=None):
    if col_exists(conn, table, column):
        print(f"  [skip]  {table}.{column} already exists")
        return
    default_clause = f" DEFAULT {default}" if default is not None else ""
    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {dtype}{default_clause};"))
    print(f"  [added] {table}.{column} {dtype}")


MIGRATIONS = {
    "users": [
        ("skills",                  "TEXT",    None),
        ("experience_level",        "TEXT",    None),
        ("location",                "TEXT",    None),
        ("preferred_funding_stage", "TEXT",    None),
        ("avatar_url",              "TEXT",    None),
        ("oauth_provider",          "TEXT",    None),
        ("oauth_id",                "TEXT",    None),
        ("is_admin",                "BOOLEAN", "FALSE"),
    ],
    "startups": [
        ("funding_stage",    "TEXT",             None),
        ("risk_level",       "TEXT",             None),
        ("traction_score",   "DOUBLE PRECISION", "0.0"),
        ("market_score",     "DOUBLE PRECISION", "0.0"),
        ("team_score",       "DOUBLE PRECISION", "0.0"),
        ("innovation_score", "DOUBLE PRECISION", "0.0"),
        ("location",         "TEXT",             None),
        ("required_skills",  "TEXT",             None),
    ],
    "investments": [
        ("status",     "TEXT",      "'pending'"),
        ("created_at", "TIMESTAMP", "NOW()"),
    ],
}

NULLABLE = [
    ("users",   "password_hash"),
]


def run():
    with engine.begin() as conn:
        for table, cols in MIGRATIONS.items():
            print(f"\n── {table} ──")
            for col, dtype, default in cols:
                add_col(conn, table, col, dtype, default)

        print("\n── nullable fixes ──")
        for table, col in NULLABLE:
            try:
                conn.execute(text(
                    f"ALTER TABLE {table} ALTER COLUMN {col} DROP NOT NULL;"
                ))
                print(f"  [ok]    {table}.{col} is now nullable")
            except Exception as e:
                print(f"  [skip]  {table}.{col}: {e}")

    print("\n✓ All migrations complete — schema is in sync with SQLAlchemy models.")


if __name__ == "__main__":
    run()
