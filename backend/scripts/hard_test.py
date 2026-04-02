from backend.database.database import SessionLocal
from backend.models.startup_signal import StartupSignal

print("STARTING TEST")

db = SessionLocal()

try:
    obj = StartupSignal(
        name="Hard Test Startup",
        domain="AI",
        description="Direct insert test",
        traction_score=7,
        innovation_score=8,
        market_trend_score=9,
        team_strength_score=6,
        risk_score=3,
        final_score=8.5
    )

    print("ADDING TO DB...")
    db.add(obj)

    print("COMMITTING...")
    db.commit()

    print("SUCCESS ✅")

except Exception as e:
    print("ERROR ❌:", e)

finally:
    db.close()