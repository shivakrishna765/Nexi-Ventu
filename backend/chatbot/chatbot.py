"""
chatbot.py
----------
Main entry point for the Nexus Venture AI Recommendation Chatbot.

Chatbot Flow:
  1. Receive user role + query context (skills, interests, location, etc.)
  2. Load startup / user data (DB-first, CSV fallback)
  3. Preprocess features
  4. Run role-based matcher
  5. Return structured recommendations with match scores and reasons

Supported roles:
  - investor    → find suitable startups
  - founder     → find team members / mentors
  - seeker      → find startups to join
  - collaborator → find co-founders / partners

FUTURE EXTENSION:
- Deploy as a Flask / FastAPI streaming endpoint.
- Add BERT embeddings for semantic understanding beyond keyword overlap.
- Integrate real-time feedback loop to personalise recommendations.
"""

from typing import Optional, List, Dict, Any
from typing import TYPE_CHECKING
from backend.config.settings import settings

try:
    from sqlalchemy.orm import Session  # type: ignore
except Exception:  # pragma: no cover
    # Allows importing/running the CLI demo in environments where SQLAlchemy
    # isn't installed. DB-backed endpoints will still require SQLAlchemy.
    Session = Any  # type: ignore

from backend.chatbot.data_loader import (
    load_startups_from_db,
    load_users_from_db,
    load_startups_csv,
    load_users_csv,
)
from backend.chatbot.matcher import (
    match_investor_to_startups,
    match_founder_to_team,
    match_seeker_to_startups,
    match_collaborator_to_founders,
)


# ── Role aliases ───────────────────────────────────────────────────────────────
_ROLE_MAP = {
    "investor":     "investor",
    "founder":      "founder",
    "mentor":       "founder",   # mentors use founder logic
    "seeker":       "seeker",
    "member":       "seeker",    # existing "member" role → seeker logic
    "collaborator": "collaborator",
    "co-founder":   "collaborator",
}


# ── Output formatter ───────────────────────────────────────────────────────────

def _small_talk_reply(query: str) -> Optional[str]:
    """
    Lightweight friendly fallback for non-recommendation chat turns.
    Keeps the assistant conversational instead of always returning rankings.
    """
    q = (query or "").strip().lower()
    if not q:
        return None

    greetings = ("hi", "hello", "hey", "good morning", "good evening")
    if any(g in q for g in greetings):
        return (
            "Hi! Great to meet you. I can help you discover startups, teammates, "
            "or co-founders based on your goals. Tell me your role and what you "
            "want to achieve."
        )

    if "thank" in q:
        return (
            "You're welcome! If you'd like, I can refine the matches by domain, "
            "location, or funding stage."
        )

    if any(k in q for k in ("who are you", "what can you do", "help")):
        return (
            "I'm your Nexus assistant. I can chat with you and also recommend "
            "startups, teammates, or founders from live platform data."
        )

    return None


def _format_results(
    results: List[Dict[str, Any]],
    role: str,
    query: str = "",
    conversation_context: Optional[List[str]] = None,
) -> str:
    """
    Convert a list of match dicts into a human-readable chatbot response string.

    Example output:
    ─────────────────────────────────────
    1. Startup: MediAI
       Match Score: 89%
       Reason:
         • Domain match: Healthcare
         • Skills overlap: Python, Ml
         • Preferred funding stage: Seed
    ─────────────────────────────────────
    """
    small_talk = _small_talk_reply(query)
    if small_talk:
        return small_talk

    if not results:
        return (
            "I could not find strong matches yet, but we can improve this quickly. "
            "Try sharing more about your skills, domain interests, and preferred location."
        )

    lines = []
    if conversation_context:
        lines.append("Nice follow-up. I used your recent chat context to refine the response.")
    else:
        lines.append(f"Great question. I found {len(results)} strong options for your {role} profile.")
    lines.extend(["Here are the best matches right now:", ""])

    for rank, item in enumerate(results, start=1):
        entity_type  = item.get("type", "result").title()
        name         = item.get("name", "Unknown")
        score        = item.get("match_score", 0)
        reasons      = item.get("reasons", [])

        lines.append(f"{rank}) {entity_type}: {name} (match: {score}%)")

        # Extra metadata by type
        if item.get("domain"):
            lines.append(f"   - Domain: {item['domain']}")
        if item.get("funding_stage"):
            lines.append(f"   - Funding Stage: {item['funding_stage']}")
        if item.get("skills"):
            lines.append(f"   - Skills: {item['skills']}")
        if item.get("location"):
            lines.append(f"   - Location: {item['location']}")

        lines.append("   Why this match:")
        for r in reasons:
            lines.append(f"   - {r}")
        lines.append("")

    lines.append(
        "If you want, I can now narrow this list by city, funding stage, or specific skills."
    )
    return "\n".join(lines)


def _render_with_gemini(
    role: str,
    query: str,
    base_answer: str,
    conversation_context: Optional[List[str]] = None,
) -> Optional[str]:
    """
    Optional natural-language pass for friendlier chat tone.
    Returns None on any failure so callers can safely fall back.
    """
    if not settings.GEMINI_API_KEY:
        return None

    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        context_text = "\n".join(conversation_context or [])

        prompt = f"""
You are Nexus, a friendly startup ecosystem assistant.
Role: {role}
User message: {query}

Recent conversation context:
{context_text}

Recommendation engine output:
{base_answer}

Rewrite the final answer to sound conversational and human, while keeping the factual recommendations intact.
Rules:
- Keep it concise (max 180 words)
- Keep recommendation ordering and key facts
- End with one clarifying follow-up question
"""
        resp = model.generate_content(prompt)
        text = (getattr(resp, "text", "") or "").strip()
        return text or None
    except Exception:
        return None


# ── Main chatbot function ──────────────────────────────────────────────────────

def run_chatbot(
    role: str,
    query: str = "",
    skills: str = "",
    interests: str = "",
    experience_level: str = "",
    preferred_funding_stage: str = "",
    location: str = "",
    top_n: int = 5,
    db: Optional[Session] = None,
    conversation_context: Optional[List[str]] = None,
    use_ai_style: bool = True,
) -> str:
    """
    Core chatbot function. Accepts user profile inputs and returns
    a formatted recommendation string.

    Parameters
    ----------
    role                    : user role (investor / founder / seeker / collaborator)
    skills                  : comma-separated skills string
    interests               : comma-separated domain interests
    experience_level        : junior / mid / senior
    preferred_funding_stage : e.g. "Seed Series A"
    location                : city name
    top_n                   : number of recommendations to return
    db                      : optional SQLAlchemy session (uses CSV if None)

    Returns
    -------
    Formatted recommendation string for display in chat UI.
    """
    # Normalise role
    normalised_role = _ROLE_MAP.get(role.lower().strip(), "seeker")

    # Build user profile dict
    user_row = {
        "skills":                  skills.lower(),
        "interests":               interests.lower(),
        "experience_level":        experience_level.lower(),
        "preferred_funding_stage": preferred_funding_stage.lower(),
        "location":                location.lower(),
    }

    # Load data (DB preferred, CSV fallback)
    if db:
        startups_df = load_startups_from_db(db)
        users_df    = load_users_from_db(db)
    else:
        startups_df = load_startups_csv()
        users_df    = load_users_csv()

    # Route to role-specific matcher
    if normalised_role == "investor":
        results = match_investor_to_startups(user_row, startups_df, top_n=top_n)

    elif normalised_role == "founder":
        results = match_founder_to_team(user_row, users_df, top_n=top_n)

    elif normalised_role == "seeker":
        results = match_seeker_to_startups(user_row, startups_df, top_n=top_n)

    elif normalised_role == "collaborator":
        results = match_collaborator_to_founders(
            user_row, users_df, startups_df, top_n=top_n
        )
    else:
        return "Unknown role. Please specify: investor, founder, seeker, or collaborator."

    base_answer = _format_results(
        results,
        normalised_role,
        query=query,
        conversation_context=conversation_context,
    )
    if not use_ai_style:
        return base_answer

    ai_answer = _render_with_gemini(
        role=normalised_role,
        query=query,
        base_answer=base_answer,
        conversation_context=conversation_context,
    )
    return ai_answer or base_answer


# ── DB-aware wrapper (used by FastAPI route) ───────────────────────────────────

def process_nexus_chat(
    db: Session,
    user_id,
    query: str,
    role_override: Optional[str] = None,
) -> str:
    """
    FastAPI-friendly wrapper that:
      1. Loads the user from DB to get their role/skills/interests.
      2. Merges the free-text query into the user profile.
      3. Calls run_chatbot() and returns the formatted response.
      4. Logs the chat to the ChatLog table.

    Parameters
    ----------
    db            : SQLAlchemy session
    user_id       : UUID of the authenticated user
    query         : free-text message from the chat UI
    role_override : optionally force a role (useful for testing)
    """
    from backend.models.user import User
    from backend.models.chat import ChatLog

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return "Error: User not found."

    role     = role_override or (user.role or "member")
    skills   = (user.bio or "") + " " + query          # bio acts as skills proxy
    interests = user.interests or ""

    response = run_chatbot(
        role=role,
        query=query,
        skills=skills,
        interests=interests,
        db=db,
    )

    # Persist chat log
    log = ChatLog(user_id=user_id, query=query, response=response)
    db.add(log)
    db.commit()

    return response
