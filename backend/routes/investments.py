from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.models.investment import Investment
from backend.models.startup import Startup
from backend.models.user import User
from backend.schemas.investment import InvestmentCreate, InvestmentResponse
from backend.schemas.startup import StartupResponse
from backend.utils.dependencies import get_current_user, get_current_investor
from backend.services.recommendation import get_recommendations

router = APIRouter(tags=["Investments"])


@router.post("/invest", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def invest(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_investor),
):
    startup = db.query(Startup).filter(Startup.id == investment.startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    new_investment = Investment(
        investor_id=current_user.id,
        startup_id=investment.startup_id,
        amount=investment.amount,
    )
    db.add(new_investment)
    db.commit()
    db.refresh(new_investment)
    return new_investment


@router.get("/investments", response_model=List[InvestmentResponse])
def get_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Investment).filter(Investment.investor_id == current_user.id).all()


@router.get("/recommendations", response_model=List[StartupResponse])
def recommendations(
    budget: Optional[float] = None,
    risk: Optional[str] = None,
    domains: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recommendations(db, budget=budget, risk=risk, domains=domains)
