"""
seed_db.py
----------
Seeds the startups table with real-looking startup data.
Safe to run multiple times — skips if data already exists.

Run:
    python -m backend.scripts.seed_db
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import SessionLocal, engine, Base
import backend.models  # registers all ORM models
from backend.models.startup import Startup
from backend.models.user import User
from backend.utils.auth import get_password_hash

SEED_STARTUPS = [
    dict(name="MediAI",           domain="Healthcare",  funding_stage="Seed",     risk_level="medium", location="Bangalore",  required_skills="Python ML TensorFlow NLP Computer Vision",  traction_score=8.5, market_score=9.0, team_score=8.0, innovation_score=9.5, description="AI-powered diagnostic assistant for rural clinics using image recognition and NLP to detect diseases early."),
    dict(name="FinFlow",          domain="Fintech",     funding_stage="Series A", risk_level="low",    location="Mumbai",     required_skills="Python Data Science React Node.js",          traction_score=9.2, market_score=8.5, team_score=9.0, innovation_score=8.0, description="Automated personal finance manager with ML-based spending predictions and investment advice for millennials."),
    dict(name="EduBot",           domain="EdTech",      funding_stage="Pre-Seed", risk_level="low",    location="Delhi",      required_skills="NLP Python React Machine Learning",          traction_score=7.0, market_score=8.0, team_score=7.5, innovation_score=8.5, description="Adaptive learning platform using NLP to personalise curriculum for K-12 students based on learning pace."),
    dict(name="GreenGrid",        domain="CleanTech",   funding_stage="Series B", risk_level="low",    location="Hyderabad",  required_skills="IoT Embedded Systems Python Data Analytics", traction_score=8.8, market_score=9.2, team_score=8.5, innovation_score=8.0, description="IoT-based smart energy management system for commercial buildings reducing energy waste by 40%."),
    dict(name="AgriSense",        domain="AgriTech",    funding_stage="Seed",     risk_level="medium", location="Pune",       required_skills="Computer Vision Python Data Science Drone Tech", traction_score=7.5, market_score=8.5, team_score=7.0, innovation_score=9.0, description="Drone and satellite data analytics for precision farming and crop yield prediction for smallholder farmers."),
    dict(name="LegalEase",        domain="LegalTech",   funding_stage="Pre-Seed", risk_level="medium", location="Chennai",    required_skills="NLP Python React Legal Knowledge",           traction_score=6.5, market_score=7.5, team_score=7.0, innovation_score=8.0, description="NLP-powered contract analysis and legal document automation making legal services affordable for SMEs."),
    dict(name="CyberShield",      domain="Cybersecurity", funding_stage="Series A", risk_level="low",  location="Bangalore",  required_skills="Cybersecurity Python ML Network Security",   traction_score=9.0, market_score=9.5, team_score=9.0, innovation_score=8.5, description="AI-driven threat detection and automated incident response platform protecting SMEs from cyberattacks."),
    dict(name="SupplySync",       domain="Logistics",   funding_stage="Seed",     risk_level="medium", location="Mumbai",     required_skills="Blockchain Python React Node.js",            traction_score=7.8, market_score=8.0, team_score=7.5, innovation_score=8.5, description="Blockchain-based supply chain transparency and real-time tracking platform eliminating fraud."),
    dict(name="TalentMatch",      domain="HRTech",      funding_stage="Pre-Seed", risk_level="low",    location="Delhi",      required_skills="NLP Python Machine Learning HR Knowledge",   traction_score=7.0, market_score=8.0, team_score=7.5, innovation_score=8.0, description="AI recruitment platform matching candidates to roles using semantic skill analysis and culture fit scoring."),
    dict(name="RetailAI",         domain="Retail",      funding_stage="Series A", risk_level="low",    location="Hyderabad",  required_skills="Computer Vision Python IoT Retail Analytics", traction_score=8.5, market_score=8.5, team_score=8.0, innovation_score=8.5, description="Computer vision system for automated inventory management and shelf analytics for retail chains."),
    dict(name="HealthChain",      domain="Healthcare",  funding_stage="Seed",     risk_level="medium", location="Bangalore",  required_skills="Blockchain Python Healthcare IT",            traction_score=7.5, market_score=8.5, team_score=8.0, innovation_score=9.0, description="Blockchain-secured patient health records with interoperability across hospitals preventing medical errors."),
    dict(name="ClimateTrack",     domain="CleanTech",   funding_stage="Series B", risk_level="low",    location="Mumbai",     required_skills="Data Analytics Python React Sustainability",  traction_score=8.0, market_score=9.0, team_score=8.5, innovation_score=8.0, description="Carbon footprint tracking and offset marketplace helping enterprises achieve net-zero targets."),
    dict(name="RoboFarm",         domain="AgriTech",    funding_stage="Series A", risk_level="medium", location="Pune",       required_skills="Robotics Python Computer Vision Embedded Systems", traction_score=8.2, market_score=8.8, team_score=8.5, innovation_score=9.5, description="Autonomous robotic systems for harvesting and planting solving the agricultural labour shortage crisis."),
    dict(name="PayEasy",          domain="Fintech",     funding_stage="Seed",     risk_level="medium", location="Chennai",    required_skills="Blockchain Python Node.js Fintech",          traction_score=8.0, market_score=8.5, team_score=7.5, innovation_score=8.5, description="Cross-border payment solution with real-time FX rates for freelancers and SMEs cutting fees by 80%."),
    dict(name="MindSpace",        domain="Mental Health", funding_stage="Pre-Seed", risk_level="medium", location="Delhi",    required_skills="NLP Python React Psychology",                traction_score=7.0, market_score=9.0, team_score=7.5, innovation_score=8.5, description="AI-powered mental wellness app with CBT-based chatbot and therapist matching making therapy accessible."),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Startup).count()
        if existing >= len(SEED_STARTUPS):
            print(f"Already seeded ({existing} startups). Skipping.")
            return

        # Get or create a seed founder user
        founder = db.query(User).filter(User.email == "seed@nexus.dev").first()
        if not founder:
            founder = User(
                name="Nexus Seed",
                email="seed@nexus.dev",
                password_hash=get_password_hash("seed_password_123"),
                role="founder",
            )
            db.add(founder)
            db.commit()
            db.refresh(founder)
            print(f"Created seed founder: {founder.id}")

        # Insert startups
        inserted = 0
        for data in SEED_STARTUPS:
            exists = db.query(Startup).filter(Startup.name == data["name"]).first()
            if exists:
                continue
            s = Startup(founder_id=founder.id, **data)
            db.add(s)
            inserted += 1

        db.commit()
        print(f"Seeded {inserted} startups successfully.")

        # Verify
        total = db.query(Startup).count()
        print(f"Total startups in DB: {total}")

    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
