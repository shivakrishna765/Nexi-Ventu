from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.user import User
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.utils.dependencies import get_current_user
from backend.services.chatbot import process_chat, generate_ideas

router = APIRouter(tags=["Chatbot"])

@router.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response_text = process_chat(
        db=db,
        user_id=current_user.id,
        query=request.query,
        budget=request.budget,
        risk=request.risk,
        domains=request.domains
    )
    return ChatResponse(response=response_text)

@router.get("/ideas")
def get_startup_ideas(domain: str = Query(..., description="Domain for startup ideas (e.g., agriculture, fintech)"), current_user: User = Depends(get_current_user)):
    response_text = generate_ideas(domain)
    return {"ideas": response_text}
