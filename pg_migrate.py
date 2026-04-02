from backend.database.database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE users ADD COLUMN bio VARCHAR;'))
            print("Added bio column")
        except Exception as e:
            print("Error adding bio:", e)
        
        try:
            conn.execute(text('ALTER TABLE users ADD COLUMN interests VARCHAR;'))
            print("Added interests column")
        except Exception as e:
            print("Error adding interests:", e)
            
        conn.commit()
    print("Migration complete")

if __name__ == "__main__":
    run_migration()
