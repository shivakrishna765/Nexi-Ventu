"""
chatbot.py — Nexus Venture AI Recommendation Chatbot
-----------------------------------------------------
Every response is unique because:
  1. The user's free-text query is parsed for intent keywords that shift
     the matcher's skill/interest/location/stage context each turn.
  2. Gemini rewrites the structured output in a conversational tone,
     using the last N chat turns as memory so it never repeats itself.
  3. Small-talk replies are randomised from a pool.
  4. When Gemini is unavailable the structured formatter still varies
     its opening line based on query content.
"""

import random
from typing import Optional, List, Dict, Any

from backend.config.settings import settings

try:
    from sqlalchemy.orm import Session
except Exception:
    from typing import Any as Session  # type: ignore

from backend.chatbot.data_loader import (
    load_startups_from_db, load_users_from_db,
    load_startups_csv,    load_users_csv,
)
from backend.chatbot.matcher import (
    match_investor_to_startups,
    match_founder_to_team,
    match_seeker_to_startups,
    match_collaborator_to_founders,
)

# ── Role map ───────────────────────────────────────────────────────────────────
_ROLE_MAP = {
    "investor": "investor", "founder": "founder", "mentor": "founder",
    "seeker": "seeker", "member": "seeker",
    "collaborator": "collaborator", "co-founder": "collaborator",
}

# ── Domain / stage / location keyword extractors ──────────────────────────────
_DOMAIN_KEYWORDS = {
    "ai": "AI", "ml": "AI", "machine learning": "AI", "healthcare": "Healthcare",
    "health": "Healthcare", "medical": "Healthcare", "fintech": "Fintech",
    "finance": "Fintech", "payment": "Fintech", "edtech": "EdTech",
    "education": "EdTech", "agritech": "AgriTech", "agriculture": "AgriTech",
    "cleantech": "CleanTech", "climate": "CleanTech", "energy": "CleanTech",
    "cyber": "Cybersecurity", "security": "Cybersecurity",
    "logistics": "Logistics", "supply chain": "Logistics",
    "hrtech": "HRTech", "hiring": "HRTech", "recruitment": "HRTech",
    "retail": "Retail", "ecommerce": "Retail",
    "mental health": "Mental Health", "wellness": "Mental Health",
    "legaltech": "LegalTech", "legal": "LegalTech",
    "blockchain": "Blockchain", "crypto": "Blockchain",
    "robotics": "Robotics", "iot": "IoT",
}

_STAGE_KEYWORDS = {
    "pre-seed": "Pre-Seed", "pre seed": "Pre-Seed",
    "seed": "Seed", "series a": "Series A",
    "series b": "Series B", "series c": "Series C",
    "early": "Pre-Seed", "growth": "Series B",
}

_SKILL_KEYWORDS = [
    "python", "react", "node", "ml", "nlp", "tensorflow", "pytorch",
    "blockchain", "solidity", "java", "kotlin", "swift", "flutter",
    "data science", "devops", "kubernetes", "docker", "aws", "gcp",
    "product management", "ux", "ui", "design", "marketing", "sales",
    "finance", "legal", "hr", "operations",
]


def _extract_context_from_query(query: str, base_row: dict) -> dict:
    """
    Parse the user's free-text query and enrich the user_row with any
    domain / stage / skill / location signals found in the message.
    This makes every query produce a different matching context.
    """
    q = query.lower()
    row = dict(base_row)

    # Extract domain interests
    found_domains = [v for k, v in _DOMAIN_KEYWORDS.items() if k in q]
    if found_domains:
        existing = row.get("interests", "")
        row["interests"] = (existing + " " + " ".join(found_domains)).strip()

    # Extract funding stage preference
    for kw, stage in _STAGE_KEYWORDS.items():
        if kw in q:
            row["preferred_funding_stage"] = stage
            break

    # Extract skill signals
    found_skills = [sk for sk in _SKILL_KEYWORDS if sk in q]
    if found_skills:
        existing = row.get("skills", "")
        row["skills"] = (existing + " " + " ".join(found_skills)).strip()

    # Extract location (simple: look for "in <city>")
    import re
    loc_match = re.search(r"\bin\s+([a-z][a-z\s]{2,20})", q)
    if loc_match and not row.get("location"):
        row["location"] = loc_match.group(1).strip()

    return row


# ── Small-talk pool ────────────────────────────────────────────────────────────
_GREET_REPLIES = [
    "Hey! Great to connect. Tell me what you're looking for — startups, teammates, investors, or co-founders?",
    "Hi there! I'm Nexus AI. Share your goals and I'll find the best matches from our live ecosystem.",
    "Hello! Ready to explore the startup ecosystem? Tell me your role and what you need.",
    "Hey! I can surface startups, investors, or talent based on your profile. What are you after?",
]

_THANKS_REPLIES = [
    "Happy to help! Want me to refine by domain, location, or funding stage?",
    "Glad that was useful! I can narrow it down further — just say the word.",
    "You're welcome! Ask me anything else about the ecosystem.",
    "Anytime! Want to explore a different domain or funding stage?",
]

_HELP_REPLIES = [
    "I'm Nexus AI — I match investors to startups, founders to team members, and seekers to opportunities. What's your role?",
    "I can recommend startups, co-founders, or team members based on your skills and interests. What do you need?",
    "Think of me as your startup ecosystem navigator. Tell me your goal and I'll find the right matches.",
]

_OPENING_LINES = [
    "Here's what I found based on your query:",
    "Great question — here are the top matches:",
    "Based on what you shared, these look like strong fits:",
    "I ran the analysis — here are your best options right now:",
    "Scanning the ecosystem… here's what came up:",
    "These are the strongest matches for your profile:",
    "Fresh results from the platform:",
    "Here's what the recommendation engine surfaced:",
]

_CLOSING_LINES = [
    "Want me to filter by location, stage, or specific skills?",
    "I can refine this further — just tell me what to prioritise.",
    "Ask me to narrow by domain, city, or funding stage anytime.",
    "Need more options or a different angle? Just ask.",
    "Want to explore a specific domain in more depth?",
]


def _small_talk_reply(query: str) -> Optional[str]:
    q = (query or "").strip().lower()
    if not q:
        return None
    if any(g in q for g in ("hi", "hello", "hey", "good morning", "good evening", "howdy")):
        return random.choice(_GREET_REPLIES)
    if "thank" in q:
        return random.choice(_THANKS_REPLIES)
    if any(k in q for k in ("who are you", "what can you do", "help", "what do you do")):
        return random.choice(_HELP_REPLIES)
    return None


# ── Structured formatter ───────────────────────────────────────────────────────

def _format_results(
    results: List[Dict[str, Any]],
    role: str,
    query: str = "",
    conversation_context: Optional[List[str]] = None,
) -> str:
    small_talk = _small_talk_reply(query)
    if small_talk:
        return small_talk

    if not results:
        no_match_options = [
            "No strong matches right now — try adding more skills or broadening your domain interests.",
            "I couldn't find a close fit yet. Share more about your background and I'll try again.",
            "The current dataset doesn't have a perfect match. Try a different domain or funding stage.",
        ]
        return random.choice(no_match_options)

    lines = [random.choice(_OPENING_LINES), ""]

    for rank, item in enumerate(results, start=1):
        entity_type = item.get("type", "result").title()
        name        = item.get("name", "Unknown")
        score       = item.get("match_score", 0)
        reasons     = item.get("reasons", [])

        lines.append(f"{rank}. {entity_type}: {name}  ({score}% match)")
        if item.get("domain"):
            lines.append(f"   Domain: {item['domain']}")
        if item.get("funding_stage"):
            lines.append(f"   Stage: {item['funding_stage']}")
        if item.get("location"):
            lines.append(f"   Location: {item['location']}")
        if item.get("skills"):
            lines.append(f"   Skills: {item['skills']}")
        if reasons:
            lines.append(f"   Why: {reasons[0]}")
        lines.append("")

    lines.append(random.choice(_CLOSING_LINES))
    return "\n".join(lines)


# ── Gemini natural-language pass ───────────────────────────────────────────────

def _render_with_gemini(
    role: str,
    query: str,
    base_answer: str,
    conversation_context: Optional[List[str]] = None,
) -> Optional[str]:
    if not settings.GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Try newer model names first, fall back gracefully
        for model_name in ("gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"):
            try:
                model = genai.GenerativeModel(model_name)
                ctx   = "\n".join(conversation_context or [])
                prompt = f"""You are Nexus, a sharp and friendly startup ecosystem AI.

Role context: {role}
User just said: "{query}"

Recent conversation (for context — do NOT repeat what was already said):
{ctx if ctx else "(this is the first message)"}

Recommendation engine output:
{base_answer}

Your task:
- Rewrite the answer in a natural, conversational tone
- Reference the user's query specifically so it feels personalised
- Do NOT repeat any phrasing from the recent conversation
- Keep all factual data (names, scores, domains) intact
- Max 200 words
- End with a single follow-up question that is DIFFERENT from any previous question
"""
                resp = model.generate_content(prompt)
                text = (getattr(resp, "text", "") or "").strip()
                if text:
                    return text
            except Exception:
                continue
        return None
    except Exception:
        return None


# ── Main entry point ───────────────────────────────────────────────────────────

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
    normalised_role = _ROLE_MAP.get(role.lower().strip(), "seeker")

    # Base profile from stored user data
    base_row = {
        "skills":                  skills.lower(),
        "interests":               interests.lower(),
        "experience_level":        experience_level.lower(),
        "preferred_funding_stage": preferred_funding_stage.lower(),
        "location":                location.lower(),
    }

    # Enrich with signals extracted from the current query
    user_row = _extract_context_from_query(query, base_row)

    # Load data
    if db:
        startups_df = load_startups_from_db(db)
        users_df    = load_users_from_db(db)
    else:
        startups_df = load_startups_csv()
        users_df    = load_users_csv()

    # Match
    if normalised_role == "investor":
        results = match_investor_to_startups(user_row, startups_df, top_n=top_n)
    elif normalised_role == "founder":
        results = match_founder_to_team(user_row, users_df, top_n=top_n)
    elif normalised_role == "seeker":
        results = match_seeker_to_startups(user_row, startups_df, top_n=top_n)
    elif normalised_role == "collaborator":
        results = match_collaborator_to_founders(user_row, users_df, startups_df, top_n=top_n)
    else:
        return "Unknown role. Please specify: investor, founder, seeker, or collaborator."

    base_answer = _format_results(
        results, normalised_role, query=query,
        conversation_context=conversation_context,
    )

    if not use_ai_style:
        return base_answer

    ai_answer = _render_with_gemini(
        role=normalised_role, query=query,
        base_answer=base_answer,
        conversation_context=conversation_context,
    )
    return ai_answer or base_answer


# ── DB-aware wrapper ───────────────────────────────────────────────────────────

def process_nexus_chat(db: Session, user_id, query: str, role_override: Optional[str] = None) -> str:
    from backend.models.user import User
    from backend.models.chat import ChatLog

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return "Error: User not found."

    role      = role_override or (user.role or "member")
    skills    = (getattr(user, "skills", "") or user.bio or "") + " " + query
    interests = user.interests or ""

    response = run_chatbot(role=role, query=query, skills=skills, interests=interests, db=db)

    log = ChatLog(user_id=user_id, query=query, response=response)
    db.add(log)
    db.commit()
    return response
