import sys
import os

# Add root folder to sys.path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import SessionLocal, engine, Base
from backend.models import user, startup, investment, chat
from backend.models.startup import Startup
from backend.models.user import User

def seed_data():
    # Make sure tables are created in Supabase
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Let's ensure a mock user exists first to satisfy foreign keys
    admin_user = db.query(User).filter(User.email=="admin@nexus.com").first()
    if not admin_user:
        admin_user = User(
            name="Admin User",
            email="admin@nexus.com",
            password_hash="mock_hash",
            role="founder"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    # Check if startups already exist
    existing = db.query(Startup).first()
    if existing:
        print("Data already seeded! Skipping...")
        db.close()
        return

    print("Seeding new startups data...")
    mock_startups = [
        Startup(
            name="AgriTech Solutions",
            created_by=admin_user.id,
            domain="agriculture",
            description="AI-driven agriculture platform optimizing water usage and predicting crop yields.",
            funding_stage="Pre-Seed",
            risk_level="medium",
            traction_score=8.5,
            market_score=9.0,
            team_score=8.0,
            innovation_score=9.5
        ),
        Startup(
            name="FinGuard AI",
            created_by=admin_user.id,
            domain="fintech",
            description="Fraud detection security system using neural networks for regional banks.",
            funding_stage="Series A",
            risk_level="low",
            traction_score=9.5,
            market_score=8.5,
            team_score=9.0,
            innovation_score=8.0
        ),
        Startup(
            name="NeuroHealth Tech",
            created_by=admin_user.id,
            domain="healthtech",
            description="Wearable devices that monitor brainwaves to predict seizures.",
            funding_stage="Seed",
            risk_level="high",
            traction_score=6.5,
            market_score=9.5,
            team_score=8.5,
            innovation_score=9.8
        ),
        Startup(
            name="EcoPack",
            created_by=admin_user.id,
            domain="cleantech",
            description="Biodegradable packaging solutions derived from mushroom roots.",
            funding_stage="Seed",
            risk_level="medium",
            traction_score=7.0,
            market_score=8.0,
            team_score=8.0,
            innovation_score=8.5
        ),
    ]

    for startup in mock_startups:
        db.add(startup)

    try:
        db.commit()
        print("Successfully seeded database with startup information!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
