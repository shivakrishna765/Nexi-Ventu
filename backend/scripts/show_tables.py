import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import engine
from sqlalchemy import inspect

def show_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("------ DATABASE STRUCTURE ------")
    for table in tables:
        print(f"\nTable: {table}")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")

if __name__ == "__main__":
    show_tables()
