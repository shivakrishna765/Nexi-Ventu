import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import SessionLocal
from backend.models import user, startup, investment, chat
from backend.models.startup import Startup

def show_data():
    db = SessionLocal()
    startups = db.query(Startup).all()
    
    print("| Name | Domain | Stage | Risk Level |")
    print("|---|---|---|---|")
    for s in startups:
        print(f"| {s.name} | {s.domain} | {s.funding_stage} | {s.risk_level} |")
    
    db.close()

if __name__ == "__main__":
    show_data()
