from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.startup import Startup

def get_recommendations(
    db: Session, 
    budget: Optional[float] = None, 
    risk: Optional[str] = None, 
    domains: Optional[str] = None
) -> List[Startup]:
    
    query = db.query(Startup)
    
    if risk:
        query = query.filter(Startup.risk_level == risk.lower())
    
    if domains:
        domain_list = [d.strip().lower() for d in domains.split(",")]
        # Simple domain matching
        if domain_list:
            query = query.filter(Startup.domain.in_(domain_list))
    
    startups = query.all()
    
    # Calculate score
    for startup in startups:
        # score = (0.30 * traction_score) + (0.25 * market_score) + (0.20 * team_score) + (0.15 * funding_stage_score) + (0.10 * innovation_score)
        funding_stage_score = 0
        stage = startup.funding_stage.lower() if startup.funding_stage else ""
        if "seed" in stage: funding_stage_score = 30
        elif "series a" in stage: funding_stage_score = 50
        elif "series b" in stage: funding_stage_score = 70
        elif "series c" in stage: funding_stage_score = 90
        
        score = (
            (0.30 * (startup.traction_score or 0)) +
            (0.25 * (startup.market_score or 0)) +
            (0.20 * (startup.team_score or 0)) +
            (0.15 * funding_stage_score) +
            (0.10 * (startup.innovation_score or 0))
        )
        startup.calculated_score = score
    
    # Sort by calculated score descending
    startups.sort(key=lambda x: getattr(x, 'calculated_score', 0), reverse=True)
    return startups[:10]  # Return top 10
