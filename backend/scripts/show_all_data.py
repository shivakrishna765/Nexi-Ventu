import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import SessionLocal
# Assuming __init__.py exports all models properly
from backend.models import User, Startup, Team, TeamMember, Investment, Application, Idea, ChatLog

def show_all_data():
    db = SessionLocal()
    
    models = {
        "Users": User,
        "Startups": Startup,
        "Teams": Team,
        "Team Members": TeamMember,
        "Investments": Investment,
        "Applications": Application,
        "Ideas": Idea,
        "ChatLogs": ChatLog
    }
    
    for name, model in models.items():
        print(f"\n=== {name} ===")
        records = db.query(model).all()
        if not records:
            print("  (Empty)")
        else:
            for r in records:
                # Clean up the output to only show relevant columns
                d = {k: str(v) for k, v in r.__dict__.items() if not k.startswith('_')}
                print(f"  {d}")
                
    db.close()

if __name__ == "__main__":
    show_all_data()
