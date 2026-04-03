"""
matcher.py
----------
Role-based matching engine for the Nexus Venture recommendation chatbot.

Implements the weighted scoring formula:
    Final Score = 0.5 * cosine_similarity
                + 0.2 * skill_overlap
                + 0.2 * domain_match
                + 0.1 * location_match

Supports four roles:
    A. investor    → ranked startups
    B. founder     → ranked team members / users
    C. seeker      → ranked startups to join
    D. collaborator → ranked founders / startups

FUTURE EXTENSION:
- Add real-time feedback learning: store user accept/reject signals and
  re-weight the scoring formula using a lightweight bandit algorithm.
- Integrate FAISS ANN search to replace brute-force cosine computation.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any

from backend.chatbot.preprocess  import (
    build_startup_feature,
    build_user_feature,
    build_query_feature,
    clean_text,
)
from backend.chatbot.vectorizer  import get_tfidf_vectors


# ── Scoring weights ────────────────────────────────────────────────────────────
W_COSINE   = 0.5
W_SKILL    = 0.2
W_DOMAIN   = 0.2
W_LOCATION = 0.1


# ── Helper utilities ───────────────────────────────────────────────────────────

def _token_overlap(text_a: str, text_b: str) -> float:
    """
    Jaccard-style token overlap between two strings.
    Returns a float in [0, 1].
    """
    set_a = set(clean_text(text_a).split())
    set_b = set(clean_text(text_b).split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _domain_match(user_interests: str, startup_domain: str) -> float:
    """
    Returns 1.0 if any user interest token appears in the startup domain,
    else 0.0.
    """
    interests = set(clean_text(user_interests).split())
    domain    = set(clean_text(startup_domain).split())
    return 1.0 if interests & domain else 0.0


def _location_match(loc_a: str, loc_b: str) -> float:
    """Returns 1.0 if locations share at least one token, else 0.0."""
    set_a = set(clean_text(loc_a).split())
    set_b = set(clean_text(loc_b).split())
    return 1.0 if set_a & set_b else 0.0


def _weighted_score(
    cosine: float,
    skill_overlap: float,
    domain_match: float,
    location_match: float,
) -> float:
    """Apply the weighted scoring formula and return a value in [0, 1]."""
    return (
        W_COSINE   * cosine
        + W_SKILL    * skill_overlap
        + W_DOMAIN   * domain_match
        + W_LOCATION * location_match
    )


def _build_reason(
    user_row: dict,
    target_row: dict,
    role: str,
    cosine: float,
) -> List[str]:
    """
    Generate human-readable reason bullets for a match.
    """
    reasons = []

    # Domain match
    user_interests  = user_row.get("interests", "")
    target_domain   = target_row.get("domain", "")
    if _domain_match(user_interests, target_domain) > 0:
        reasons.append(f"Domain match: {target_domain.title()}")

    # Skill overlap
    user_skills     = user_row.get("skills", "")
    target_skills   = target_row.get("required_skills", target_row.get("skills", ""))
    overlap_score   = _token_overlap(user_skills, target_skills)
    if overlap_score > 0:
        u_set = set(clean_text(user_skills).split())
        t_set = set(clean_text(target_skills).split())
        shared = ", ".join(sorted(u_set & t_set)[:5]).title()
        if shared:
            reasons.append(f"Skills overlap: {shared}")

    # Funding stage (investor / seeker)
    if role in ("investor", "seeker"):
        pref_stage  = user_row.get("preferred_funding_stage", "")
        target_stage = target_row.get("funding_stage", "")
        if pref_stage and target_stage and any(
            p in target_stage for p in clean_text(pref_stage).split()
        ):
            reasons.append(f"Preferred funding stage: {target_stage.title()}")

    # Location
    user_loc   = user_row.get("location", "")
    target_loc = target_row.get("location", "")
    if _location_match(user_loc, target_loc):
        reasons.append(f"Same location: {target_loc.title()}")

    # Cosine similarity note
    if cosine > 0.3:
        reasons.append(f"Strong profile-text similarity ({round(cosine * 100, 1)}%)")

    return reasons if reasons else ["General profile alignment"]


# ── Role-based matchers ────────────────────────────────────────────────────────

def match_investor_to_startups(
    user_row: dict,
    startups_df: pd.DataFrame,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    A. INVESTOR → STARTUPS
    Match investor preferences (interests, preferred_funding_stage, location)
    against startup features.
    """
    startup_features = [build_startup_feature(r) for _, r in startups_df.iterrows()]
    query_feature    = build_query_feature({
        "skills":   user_row.get("skills", ""),
        "interests": user_row.get("interests", ""),
        "stage":    user_row.get("preferred_funding_stage", ""),
    })

    startup_matrix, query_vec, _ = get_tfidf_vectors(startup_features, query_feature)
    from sklearn.metrics.pairwise import cosine_similarity as cos_sim
    cosine_scores = cos_sim(query_vec, startup_matrix).flatten()

    results = []
    for idx, row in startups_df.iterrows():
        cosine      = float(cosine_scores[idx])
        skill_ov    = _token_overlap(user_row.get("skills", ""), row.get("required_skills", ""))
        dom_match   = _domain_match(user_row.get("interests", ""), row.get("domain", ""))
        loc_match   = _location_match(user_row.get("location", ""), row.get("location", ""))
        final       = _weighted_score(cosine, skill_ov, dom_match, loc_match)

        results.append({
            "id":           row.get("startup_id", ""),
            "name":         row.get("name", ""),
            "type":         "startup",
            "domain":       row.get("domain", "").title(),
            "funding_stage": row.get("funding_stage", "").title(),
            "location":     row.get("location", "").title(),
            "match_score":  round(final * 100, 1),
            "reasons":      _build_reason(user_row, dict(row), "investor", cosine),
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]


def match_founder_to_team(
    user_row: dict,
    users_df: pd.DataFrame,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    B. FOUNDER → TEAM MEMBERS
    Match founder's required skills / interests against seeker/collaborator profiles.
    """
    # Only consider seekers and collaborators as potential team members
    candidates = users_df[users_df["role"].isin(["seeker", "collaborator"])].copy()
    if candidates.empty:
        return []

    candidate_features = [build_user_feature(r) for _, r in candidates.iterrows()]
    query_feature      = build_query_feature({
        "skills":    user_row.get("skills", ""),
        "interests": user_row.get("interests", ""),
    })

    startup_matrix, query_vec, _ = get_tfidf_vectors(candidate_features, query_feature)
    from sklearn.metrics.pairwise import cosine_similarity as cos_sim
    cosine_scores = cos_sim(query_vec, startup_matrix).flatten()

    results = []
    for enum_idx, (_, row) in enumerate(candidates.iterrows()):
        cosine    = float(cosine_scores[enum_idx])
        skill_ov  = _token_overlap(user_row.get("skills", ""), row.get("skills", ""))
        dom_match = _domain_match(user_row.get("interests", ""), row.get("interests", ""))
        loc_match = _location_match(user_row.get("location", ""), row.get("location", ""))
        final     = _weighted_score(cosine, skill_ov, dom_match, loc_match)

        results.append({
            "id":           row.get("user_id", ""),
            "name":         row.get("name", ""),
            "type":         "user",
            "role":         row.get("role", "").title(),
            "skills":       row.get("skills", "").title(),
            "location":     row.get("location", "").title(),
            "match_score":  round(final * 100, 1),
            "reasons":      _build_reason(user_row, dict(row), "founder", cosine),
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]


def match_seeker_to_startups(
    user_row: dict,
    startups_df: pd.DataFrame,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    C. TEAM SEEKER → STARTUPS
    Match seeker's skills against startup required_skills.
    """
    startup_features = [build_startup_feature(r) for _, r in startups_df.iterrows()]
    query_feature    = build_query_feature({
        "skills":    user_row.get("skills", ""),
        "interests": user_row.get("interests", ""),
        "level":     user_row.get("experience_level", ""),
    })

    startup_matrix, query_vec, _ = get_tfidf_vectors(startup_features, query_feature)
    from sklearn.metrics.pairwise import cosine_similarity as cos_sim
    cosine_scores = cos_sim(query_vec, startup_matrix).flatten()

    results = []
    for idx, row in startups_df.iterrows():
        cosine    = float(cosine_scores[idx])
        skill_ov  = _token_overlap(user_row.get("skills", ""), row.get("required_skills", ""))
        dom_match = _domain_match(user_row.get("interests", ""), row.get("domain", ""))
        loc_match = _location_match(user_row.get("location", ""), row.get("location", ""))
        final     = _weighted_score(cosine, skill_ov, dom_match, loc_match)

        results.append({
            "id":             row.get("startup_id", ""),
            "name":           row.get("name", ""),
            "type":           "startup",
            "domain":         row.get("domain", "").title(),
            "required_skills": row.get("required_skills", "").title(),
            "funding_stage":  row.get("funding_stage", "").title(),
            "location":       row.get("location", "").title(),
            "match_score":    round(final * 100, 1),
            "reasons":        _build_reason(user_row, dict(row), "seeker", cosine),
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]


def match_collaborator_to_founders(
    user_row: dict,
    users_df: pd.DataFrame,
    startups_df: pd.DataFrame,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    D. COLLABORATOR → FOUNDERS / STARTUPS
    Match collaborator's interests + skills against founder profiles and startups.
    Returns a blended list of founders and startups.
    """
    # --- Match against founders ---
    founders = users_df[users_df["role"] == "founder"].copy()
    founder_results = []

    if not founders.empty:
        founder_features = [build_user_feature(r) for _, r in founders.iterrows()]
        query_feature    = build_query_feature({
            "skills":    user_row.get("skills", ""),
            "interests": user_row.get("interests", ""),
        })
        startup_matrix, query_vec, _ = get_tfidf_vectors(founder_features, query_feature)
        from sklearn.metrics.pairwise import cosine_similarity as cos_sim
        cosine_scores = cos_sim(query_vec, startup_matrix).flatten()

        for enum_idx, (_, row) in enumerate(founders.iterrows()):
            cosine    = float(cosine_scores[enum_idx])
            skill_ov  = _token_overlap(user_row.get("skills", ""), row.get("skills", ""))
            dom_match = _domain_match(user_row.get("interests", ""), row.get("interests", ""))
            loc_match = _location_match(user_row.get("location", ""), row.get("location", ""))
            final     = _weighted_score(cosine, skill_ov, dom_match, loc_match)

            founder_results.append({
                "id":          row.get("user_id", ""),
                "name":        row.get("name", ""),
                "type":        "founder",
                "skills":      row.get("skills", "").title(),
                "interests":   row.get("interests", "").title(),
                "location":    row.get("location", "").title(),
                "match_score": round(final * 100, 1),
                "reasons":     _build_reason(user_row, dict(row), "collaborator", cosine),
            })

    # --- Match against startups ---
    startup_results = match_seeker_to_startups(user_row, startups_df, top_n=top_n)
    for r in startup_results:
        r["type"] = "startup"

    # Merge, sort, return top N
    combined = founder_results + startup_results
    combined.sort(key=lambda x: x["match_score"], reverse=True)
    return combined[:top_n]
