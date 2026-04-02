import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import engine, Base
# Import the initialized models registry
import backend.models

def rebuild_database():
    print("Dropping all existing tables to make way for the new UUID models...")
    # This specifically drops all tables in the connected database known to SQLAlchemy metadata
    Base.metadata.drop_all(bind=engine)
    
    print("Creating perfectly normalized UUID schema (User, Startup, Team, Investment, Application)...")
    Base.metadata.create_all(bind=engine)
    print("Schema rebuilt successfully!")

if __name__ == "__main__":
    rebuild_database()
