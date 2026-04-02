import json
from sqlalchemy.orm import Session
from backend.services.recommendation import get_recommendations
from backend.models.chat import ChatLog
from backend.models.user import User
from backend.models.startup import Startup
from backend.models.team import Team
from backend.models.idea import Idea
from backend.services.vector_search import compute_similarity

def process_chat(db: Session, user_id: int, query: str, budget: float = None, risk: str = None, domains: str = None) -> str:
    """
    Main chatbot entry point using TF-IDF vector matching.
    Routes logic based on the user's role (investor, member (team seeker), founder (mentor)).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return "Error: User not found."

    role = user.role.lower() if user.role else "member"
    
    # Use the query combined with user bio for richer context matching
    user_context = query
    if user.bio:
        user_context += " " + user.bio
    if user.interests:
        user_context += " " + user.interests

    # Route based on Persona
    if role == "investor":
        response_text = _handle_investor(db, user_context, budget, risk, domains)
    elif role == "member":
        # Treating 'member' as Team Seeker
        response_text = _handle_team_seeker(db, user_context)
    elif role == "founder":
        # Treating 'founder' as Mentor or looking for Ideas
        response_text = _handle_mentor(db, user_context)
    else:
        response_text = "I'm not sure how to help with that profile role."

    # Log the chat
    chat_log = ChatLog(
        user_id=user_id,
        query=query,
        response=response_text
    )
    db.add(chat_log)
    db.commit()
    
    return response_text

def _handle_investor(db: Session, query_context: str, budget: float, risk: str, domains: str) -> str:
    # 1. Fetch relevant startups using recommendation engine
    startups = get_recommendations(db, budget=budget, risk=risk, domains=domains)
    if not startups:
        return "No startups matching your criteria were found."

    # 2. Prepare texts for vector search
    documents = []
    for s in startups:
        text = f"{s.name} {s.domain} {s.description or ''}"
        documents.append(text)

    # 3. Compute similarities
    scores = compute_similarity(query_context, documents)
    
    # 4. Combine calculated_score with similarity
    for idx, s in enumerate(startups):
        base_score = getattr(s, 'calculated_score', 0)
        sim_score = scores[idx] * 100 # scale to 100
        # simple weighted average: 70% system score, 30% similarity match
        final_match = (0.7 * base_score) + (0.3 * sim_score)
        setattr(s, 'final_match', final_match)

    startups.sort(key=lambda x: getattr(x, 'final_match', 0), reverse=True)
    
    # 5. Format response
    response = "Here are the top startup recommendations tailored to your profile (using Vector Search):\n\n"
    for idx, s in enumerate(startups[:5]):
        match_score = round(getattr(s, 'final_match', 0), 1)
        response += f"{idx+1}. **{s.name}** (Match Score: {match_score})\n"
        response += f"   - Domain: {s.domain}\n"
        response += f"   - Description: {s.description}\n\n"
    
    return response

def _handle_team_seeker(db: Session, query_context: str) -> str:
    # Find startups or teams looking for members
    teams = db.query(Team).all()
    if not teams:
        return "No active teams available right now to join."
        
    documents = []
    for t in teams:
        startup_domain = t.startup.domain if t.startup else ""
        text = f"{t.team_name} {t.description or ''} {startup_domain}"
        documents.append(text)
        
    scores = compute_similarity(query_context, documents)
    
    scored_teams = list(zip(teams, scores))
    scored_teams.sort(key=lambda x: x[1], reverse=True)
    
    response = "Here are the best matching teams for your skills (using Vector Search):\n\n"
    for idx, (t, score) in enumerate(scored_teams[:5]):
        if score > 0.05: # threshold
            response += f"{idx+1}. **{t.team_name}** (Similarity: {round(score*100, 1)}%)\n"
            response += f"   - Startup Domain: {t.startup.domain if t.startup else 'N/A'}\n"
            response += f"   - Needs: {t.description}\n\n"
            
    if response == "Here are the best matching teams for your skills (using Vector Search):\n\n":
        response = "No closely matching teams found for your skills at this moment."
        
    return response

def _handle_mentor(db: Session, query_context: str) -> str:
    # Match Mentor's profile with stored Ideas
    ideas = db.query(Idea).all()
    if not ideas:
        return "No new startup ideas found in the ecosystem to mentor."
        
    documents = []
    for i in ideas:
        text = f"{i.title} {i.description or ''}"
        documents.append(text)
        
    scores = compute_similarity(query_context, documents)
    
    scored_ideas = list(zip(ideas, scores))
    scored_ideas.sort(key=lambda x: x[1], reverse=True)
    
    response = "Here are the top startup ideas matching your mentorship expertise:\n\n"
    for idx, (i, score) in enumerate(scored_ideas[:5]):
        if score > 0.05:
            response += f"{idx+1}. **{i.title}** (Similarity: {round(score*100, 1)}%)\n"
            response += f"   - Description: {i.description}\n"
            response += f"   - Author Name: {i.user.name if i.user else 'Anonymous'}\n\n"
            
    if "Similarity" not in response:
        response = "No strongly matching ideas found for your expertise."
        
    return response

def generate_ideas(domain: str) -> str:
    # Fallback to an offline response or vector retrieved DB ideas
    return f"Looking to explore {domain}? Here are 3 vector-generated mock mockups from the ecosystem:\n\n1. AI Assistant in {domain}\n2. Automated Workflow for {domain}\n3. Data Analytics Platform for {domain}"
