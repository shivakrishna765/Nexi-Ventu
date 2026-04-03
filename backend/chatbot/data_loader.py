"""
data_loader.py
--------------
Loads startup and user datasets from CSV files into pandas DataFrames.
Also provides a utility to load live startup/user data from the PostgreSQL
database (via SQLAlchemy session) so the chatbot can work with real data.

FUTURE EXTENSION:
- Replace CSV loading with a vector database (FAISS / Pinecone) for
  scalable similarity search over millions of records.
"""

import os
import pandas as pd
from typing import Optional
from typing import Any

try:
    from sqlalchemy.orm import Session  # type: ignore
except Exception:  # pragma: no cover
    # Keep CSV loaders usable even if SQLAlchemy isn't installed.
    Session = Any  # type: ignore

# ── Paths ──────────────────────────────────────────────────────────────────────
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STARTUPS_CSV = os.path.join(_DATA_DIR, "startups.csv")
USERS_CSV    = os.path.join(_DATA_DIR, "users.csv")


# ── CSV loaders ────────────────────────────────────────────────────────────────

def load_startups_csv() -> pd.DataFrame:
    """
    Load the static startup dataset from CSV.
    Returns a DataFrame with columns:
        startup_id, name, domain, description, problem_statement,
        funding_stage, required_skills, location
    """
    df = pd.read_csv(STARTUPS_CSV)
    # Normalise text columns to lowercase strings, fill NaN with empty string
    text_cols = ["domain", "description", "problem_statement",
                 "required_skills", "funding_stage", "location"]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.lower()
    return df


def load_users_csv() -> pd.DataFrame:
    """
    Load the static user dataset from CSV.
    Returns a DataFrame with columns:
        user_id, name, role, skills, interests,
        experience_level, preferred_funding_stage, location
    """
    df = pd.read_csv(USERS_CSV)
    text_cols = ["role", "skills", "interests",
                 "experience_level", "preferred_funding_stage", "location"]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.lower()
    return df


# ── Live DB loaders ────────────────────────────────────────────────────────────

def load_startups_from_db(db: Session) -> pd.DataFrame:
    """
    Load startups from the live PostgreSQL database and return as a DataFrame.
    Falls back to CSV data if the DB is empty or unavailable.
    """
    try:
        from backend.models.startup import Startup
        rows = db.query(Startup).all()
        if not rows:
            return load_startups_csv()

        records = []
        for s in rows:
            records.append({
                "startup_id":        str(s.id),
                "name":              s.name or "",
                "domain":            (s.domain or "").lower(),
                "description":       (s.description or "").lower(),
                "problem_statement": (s.description or "").lower(),  # reuse description
                "funding_stage":     (getattr(s, "funding_stage", "") or "").lower(),
                "required_skills":   (getattr(s, "required_skills", "") or "").lower(),
                "location":          (getattr(s, "location", "") or "").lower(),
            })
        return pd.DataFrame(records)
    except Exception as e:
        print(f"[data_loader] DB load failed ({e}), falling back to CSV.")
        return load_startups_csv()


def load_users_from_db(db: Session) -> pd.DataFrame:
    """
    Load users from the live PostgreSQL database and return as a DataFrame.
    Falls back to CSV data if the DB is empty or unavailable.
    """
    try:
        from backend.models.user import User
        rows = db.query(User).all()
        if not rows:
            return load_users_csv()

        records = []
        for u in rows:
            records.append({
                "user_id":                str(u.id),
                "name":                   u.name or "",
                "role":                   (u.role or "member").lower(),
                "skills":                 (getattr(u, "skills", "") or u.bio or "").lower(),
                "interests":              (u.interests or "").lower(),
                "experience_level":       (getattr(u, "experience_level", "") or "").lower(),
                "preferred_funding_stage": (getattr(u, "preferred_funding_stage", "") or "").lower(),
                "location":               (getattr(u, "location", "") or "").lower(),
            })
        return pd.DataFrame(records)
    except Exception as e:
        print(f"[data_loader] DB user load failed ({e}), falling back to CSV.")
        return load_users_csv()
