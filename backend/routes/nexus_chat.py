"""
nexus_chat.py  (route)
----------------------
FastAPI router for the Nexus Venture multi-role AI recommendation chatbot.

Endpoints:
  POST /nexus-chat          → authenticated, uses DB user profile
  POST /nexus-chat/demo     → unauthenticated, uses inline profile (for demos)

FUTURE EXTENSION:
- Add WebSocket endpoint for real-time streaming responses.
- Add /nexus-chat/feedback endpoint to collect accept/reject signals.
"""

import json
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.user import User
from backend.utils.dependencies import get_current_user
from backend.schemas.nexus_chat import NexusChatRequest, NexusChatResponse, MatchResult
from backend.chatbot.chatbot import run_chatbot, process_nexus_chat
from backend.chatbot.matcher import (
    match_investor_to_startups,
    match_founder_to_team,
    match_seeker_to_startups,
    match_collaborator_to_founders,
)
from backend.chatbot.data_loader import load_startups_from_db, load_users_from_db

router = APIRouter(prefix="/nexus-chat", tags=["Nexus AI Chatbot"])

_ROLE_MAP = {
    "investor":     "investor",
    "founder":      "founder",
    "mentor":       "founder",
    "seeker":       "seeker",
    "member":       "seeker",
    "collaborator": "collaborator",
    "co-founder":   "collaborator",
}


def _run_matcher(role: str, user_row: dict, db: Session):
    """Dispatch to the correct matcher based on normalised role."""
    startups_df = load_startups_from_db(db)
    users_df    = load_users_from_db(db)

    if role == "investor":
        return match_investor_to_startups(user_row, startups_df, top_n=user_row.get("top_n", 5))
    elif role == "founder":
        return match_founder_to_team(user_row, users_df, top_n=user_row.get("top_n", 5))
    elif role == "seeker":
        return match_seeker_to_startups(user_row, startups_df, top_n=user_row.get("top_n", 5))
    elif role == "collaborator":
        return match_collaborator_to_founders(user_row, users_df, startups_df, top_n=user_row.get("top_n", 5))
    return []


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _stream_text_chunks(text: str, step: int = 30):
    for i in range(0, len(text), step):
        yield text[i:i + step]
        time.sleep(0.03)


def _recent_history_for_user(db: Session, user_id, limit: int = 4):
    from backend.models.chat import ChatLog
    rows = (
        db.query(ChatLog)
        .filter(ChatLog.user_id == user_id)
        .order_by(ChatLog.timestamp.desc())
        .limit(max(0, limit))
        .all()
    )
    rows = list(reversed(rows))
    history = []
    for r in rows:
        q = (r.query or "").strip()
        a = (r.response or "").strip()
        if q:
            history.append(f"User: {q}")
        if a:
            history.append(f"Assistant: {a[:250]}")
    return history


# ── Authenticated endpoint ─────────────────────────────────────────────────────

@router.post("", response_model=NexusChatResponse)
def nexus_chat(
    request: NexusChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Authenticated multi-role recommendation endpoint.
    Uses the logged-in user's stored role, bio (skills), and interests.
    All fields can be overridden in the request body.
    """
    # Resolve role: request override > DB role > default seeker
    raw_role = request.role or current_user.role or "member"
    role     = _ROLE_MAP.get(raw_role.lower(), "seeker")

    user_row = {
        "skills":                  request.skills    or (current_user.bio       or "") + " " + request.query,
        "interests":               request.interests or (current_user.interests or ""),
        "experience_level":        request.experience_level        or "",
        "preferred_funding_stage": request.preferred_funding_stage or "",
        "location":                request.location                or "",
        "top_n":                   request.top_n,
    }

    results = _run_matcher(role, user_row, db)

    # Format text response
    formatted = run_chatbot(
        role=role,
        query=request.query,
        skills=user_row["skills"],
        interests=user_row["interests"],
        experience_level=user_row["experience_level"],
        preferred_funding_stage=user_row["preferred_funding_stage"],
        location=user_row["location"],
        top_n=request.top_n,
        db=db,
        conversation_context=_recent_history_for_user(db, current_user.id, request.memory_turns),
        use_ai_style=request.use_ai_style,
    )

    # Log to ChatLog
    from backend.models.chat import ChatLog
    log = ChatLog(user_id=current_user.id, query=request.query, response=formatted)
    db.add(log)
    db.commit()

    return NexusChatResponse(
        role=role,
        formatted_text=formatted,
        results=[MatchResult(**{k: v for k, v in r.items() if k in MatchResult.model_fields}) for r in results],
    )


# ── Demo endpoint (no auth required) ──────────────────────────────────────────

@router.post("/demo", response_model=NexusChatResponse)
def nexus_chat_demo(
    request: NexusChatRequest,
    db: Session = Depends(get_db),
):
    """
    Unauthenticated demo endpoint.
    Requires role, skills, and interests to be provided in the request body.
    Uses CSV data as fallback if DB is empty.
    """
    if not request.role:
        raise HTTPException(status_code=400, detail="'role' is required for the demo endpoint.")

    role = _ROLE_MAP.get(request.role.lower(), "seeker")

    user_row = {
        "skills":                  (request.skills    or request.query).lower(),
        "interests":               (request.interests or "").lower(),
        "experience_level":        (request.experience_level        or "").lower(),
        "preferred_funding_stage": (request.preferred_funding_stage or "").lower(),
        "location":                (request.location                or "").lower(),
        "top_n":                   request.top_n,
    }

    results = _run_matcher(role, user_row, db)

    formatted = run_chatbot(
        role=role,
        query=request.query,
        skills=user_row["skills"],
        interests=user_row["interests"],
        experience_level=user_row["experience_level"],
        preferred_funding_stage=user_row["preferred_funding_stage"],
        location=user_row["location"],
        top_n=request.top_n,
        db=db,
        conversation_context=[],
        use_ai_style=request.use_ai_style,
    )

    return NexusChatResponse(
        role=role,
        formatted_text=formatted,
        results=[MatchResult(**{k: v for k, v in r.items() if k in MatchResult.model_fields}) for r in results],
    )


@router.post("/stream")
def nexus_chat_stream(
    request: NexusChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Authenticated streaming chatbot endpoint using Server-Sent Events (SSE).
    Emits:
      - text_chunk events for progressive UI rendering
      - done event with full payload + structured results
    """
    raw_role = request.role or current_user.role or "member"
    role = _ROLE_MAP.get(raw_role.lower(), "seeker")

    user_row = {
        "skills":                  request.skills or (current_user.bio or "") + " " + request.query,
        "interests":               request.interests or (current_user.interests or ""),
        "experience_level":        request.experience_level or "",
        "preferred_funding_stage": request.preferred_funding_stage or "",
        "location":                request.location or "",
        "top_n":                   request.top_n,
    }

    results = _run_matcher(role, user_row, db)
    formatted = run_chatbot(
        role=role,
        query=request.query,
        skills=user_row["skills"],
        interests=user_row["interests"],
        experience_level=user_row["experience_level"],
        preferred_funding_stage=user_row["preferred_funding_stage"],
        location=user_row["location"],
        top_n=request.top_n,
        db=db,
        conversation_context=_recent_history_for_user(db, current_user.id, request.memory_turns),
        use_ai_style=request.use_ai_style,
    )

    from backend.models.chat import ChatLog
    log = ChatLog(user_id=current_user.id, query=request.query, response=formatted)
    db.add(log)
    db.commit()

    result_models = [
        MatchResult(**{k: v for k, v in r.items() if k in MatchResult.model_fields}).model_dump()
        for r in results
    ]

    def event_generator():
        yield _sse_event("meta", {"role": role})
        for chunk in _stream_text_chunks(formatted):
            yield _sse_event("text_chunk", {"content": chunk})
        yield _sse_event(
            "done",
            {
                "role": role,
                "formatted_text": formatted,
                "results": result_models,
            },
        )

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/demo/stream")
def nexus_chat_demo_stream(
    request: NexusChatRequest,
    db: Session = Depends(get_db),
):
    """
    Unauthenticated SSE endpoint for frontend/demo environments.
    """
    if not request.role:
        raise HTTPException(status_code=400, detail="'role' is required for the demo stream endpoint.")

    role = _ROLE_MAP.get(request.role.lower(), "seeker")
    user_row = {
        "skills":                  (request.skills or request.query).lower(),
        "interests":               (request.interests or "").lower(),
        "experience_level":        (request.experience_level or "").lower(),
        "preferred_funding_stage": (request.preferred_funding_stage or "").lower(),
        "location":                (request.location or "").lower(),
        "top_n":                   request.top_n,
    }

    results = _run_matcher(role, user_row, db)
    formatted = run_chatbot(
        role=role,
        query=request.query,
        skills=user_row["skills"],
        interests=user_row["interests"],
        experience_level=user_row["experience_level"],
        preferred_funding_stage=user_row["preferred_funding_stage"],
        location=user_row["location"],
        top_n=request.top_n,
        db=db,
        conversation_context=[],
        use_ai_style=request.use_ai_style,
    )

    result_models = [
        MatchResult(**{k: v for k, v in r.items() if k in MatchResult.model_fields}).model_dump()
        for r in results
    ]

    def event_generator():
        yield _sse_event("meta", {"role": role})
        for chunk in _stream_text_chunks(formatted):
            yield _sse_event("text_chunk", {"content": chunk})
        yield _sse_event(
            "done",
            {"role": role, "formatted_text": formatted, "results": result_models},
        )

    return StreamingResponse(event_generator(), media_type="text/event-stream")
