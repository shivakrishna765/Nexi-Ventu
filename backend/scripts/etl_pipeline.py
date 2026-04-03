"""
etl_pipeline.py
---------------
Continuous data ingestion pipeline for Nexus Venture.

What it does every cycle:
  1. Scrapes TechCrunch RSS for fresh startup news
  2. Sends each article to Gemini AI for structured extraction
  3. Inserts into BOTH tables:
       - startup_signals  (raw AI scores / analytics)
       - startups         (the table the frontend reads via /get-startups)
  4. Skips duplicates by name
  5. Sleeps INTERVAL seconds, then repeats forever

Run:
    python -m backend.scripts.etl_pipeline

Environment variables (backend/.env):
    GEMINI_API_KEY=...
    DATABASE_URL=...
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ── Path setup ─────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Suppress OpenBLAS / numpy thread warnings
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import google.generativeai as genai
from backend.database.database import SessionLocal, engine, Base
import backend.models  # registers all ORM models
from backend.models.startup_signal import StartupSignal
from backend.models.startup import Startup
from backend.models.user import User
from backend.utils.auth import get_password_hash

# ── Config ─────────────────────────────────────────────────────────────────────
INTERVAL_SECONDS  = 60        # how often the pipeline runs
MAX_PER_CYCLE     = 5         # max new startups inserted per cycle
RSS_URL           = "https://techcrunch.com/category/startups/feed/"
PIPELINE_USER_EMAIL = "pipeline@nexus.dev"   # system user that "owns" pipeline startups

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PIPELINE] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline")

# ── Gemini setup ───────────────────────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    log.error("GEMINI_API_KEY not set — AI enrichment will be skipped.")
    gemini_model = None
else:
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")
    log.info("Gemini AI ready.")

# ── Ensure tables exist ────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_or_create_pipeline_user() -> str:
    """
    Returns the UUID of the system user that owns pipeline-inserted startups.
    Creates the user if it doesn't exist.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == PIPELINE_USER_EMAIL).first()
        if not user:
            user = User(
                name="Pipeline Bot",
                email=PIPELINE_USER_EMAIL,
                password_hash=get_password_hash("pipeline_secret_do_not_use"),
                role="founder",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            log.info(f"Created pipeline user: {user.id}")
        return str(user.id)
    finally:
        db.close()


def startup_exists(db, name: str) -> bool:
    """Returns True if a startup with this name already exists in either table."""
    return (
        db.query(Startup).filter(Startup.name == name).first() is not None
        or db.query(StartupSignal).filter(StartupSignal.name == name).first() is not None
    )


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — SCRAPE
# ══════════════════════════════════════════════════════════════════════════════

def scrape_rss() -> list[dict]:
    """
    Fetches TechCrunch RSS and returns a list of
    { name, title, description } dicts.
    """
    log.info("Fetching data from TechCrunch RSS...")
    try:
        resp = requests.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log.error(f"RSS fetch failed: {e}")
        return []

    soup = BeautifulSoup(resp.text, "xml")
    items = soup.find_all("item")
    results = []

    for item in items[:25]:
        title = (item.title.text if item.title else "").strip()
        raw_desc = item.description.text if item.description else ""
        clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text(separator=" ").strip()

        if not title or len(clean_desc) < 20:
            continue

        # Extract a company name from the headline
        name = title
        for splitter in [" raises", " secures", " launches", " acquires", " closes", " lands"]:
            if splitter in name.lower():
                name = name[: name.lower().index(splitter)].strip()
                break
        name = name[:120]

        results.append({"name": name, "title": title, "description": clean_desc})

    log.info(f"Scraped {len(results)} articles.")
    return results


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — AI ENRICHMENT
# ══════════════════════════════════════════════════════════════════════════════

_PROMPT_TEMPLATE = """
You are an expert startup analyst.

Extract structured startup intelligence from the text below.

Rules:
- Focus ONLY on real startups or companies.
- If no real startup is present, return {{"company_name": null}}.
- Return ONLY valid JSON, no explanation.

TEXT:
{text}

JSON format:
{{
  "company_name": "",
  "domain": "",
  "description": "",
  "funding_stage": "",
  "location": "",
  "required_skills": "",
  "traction_score": 0,
  "innovation_score": 0,
  "market_trend_score": 0,
  "team_strength_score": 0,
  "risk_score": 0
}}

Scoring (0-10):
- traction_score: growth, users, revenue signals
- innovation_score: uniqueness, deep tech
- market_trend_score: industry demand
- team_strength_score: founder background
- risk_score: 10 = very risky, 0 = very safe

funding_stage: one of Pre-Seed, Seed, Series A, Series B, Series C, Growth
location: city or country if mentioned, else empty string
required_skills: comma-separated tech skills relevant to the startup
"""


def enrich_with_ai(article: dict) -> dict | None:
    """
    Sends article text to Gemini and returns structured data dict, or None.
    Falls back to a rule-based extraction if Gemini is unavailable.
    """
    text = f"Title: {article['title']}\nDescription: {article['description']}"

    if gemini_model:
        try:
            resp = gemini_model.generate_content(_PROMPT_TEMPLATE.format(text=text))
            raw = resp.text.strip()
            # Strip markdown code fences if present
            for fence in ("```json", "```"):
                if raw.startswith(fence):
                    raw = raw[len(fence):]
            if raw.endswith("```"):
                raw = raw[:-3]
            data = json.loads(raw.strip())
            if not data.get("company_name"):
                return None
            log.info(f"  AI enriched: {data['company_name']}")
            return data
        except Exception as e:
            log.warning(f"  Gemini error ({e}), using rule-based fallback.")

    # ── Rule-based fallback (no API key or Gemini error) ──────────────────────
    return {
        "company_name":      article["name"],
        "domain":            _guess_domain(article["description"]),
        "description":       article["description"][:400],
        "funding_stage":     _guess_stage(article["title"]),
        "location":          "",
        "required_skills":   "",
        "traction_score":    5,
        "innovation_score":  5,
        "market_trend_score": 5,
        "team_strength_score": 5,
        "risk_score":        5,
    }


def _guess_domain(text: str) -> str:
    text = text.lower()
    for kw, domain in [
        ("health", "Healthcare"), ("medical", "Healthcare"), ("clinic", "Healthcare"),
        ("fintech", "Fintech"), ("payment", "Fintech"), ("bank", "Fintech"),
        ("ai", "AI"), ("machine learning", "AI"), ("llm", "AI"),
        ("edu", "EdTech"), ("learn", "EdTech"),
        ("agri", "AgriTech"), ("farm", "AgriTech"),
        ("climate", "CleanTech"), ("energy", "CleanTech"), ("green", "CleanTech"),
        ("cyber", "Cybersecurity"), ("security", "Cybersecurity"),
        ("logistics", "Logistics"), ("supply chain", "Logistics"),
        ("retail", "Retail"), ("ecommerce", "Retail"),
    ]:
        if kw in text:
            return domain
    return "Technology"


def _guess_stage(title: str) -> str:
    title = title.lower()
    for kw, stage in [
        ("series c", "Series C"), ("series b", "Series B"),
        ("series a", "Series A"), ("seed", "Seed"), ("pre-seed", "Pre-Seed"),
    ]:
        if kw in title:
            return stage
    return "Seed"


def _calculate_final_score(data: dict) -> float:
    t = float(data.get("traction_score", 5))
    m = float(data.get("market_trend_score", 5))
    i = float(data.get("innovation_score", 5))
    team = float(data.get("team_strength_score", 5))
    r = float(data.get("risk_score", 5))
    return round(0.30 * t + 0.25 * m + 0.20 * i + 0.15 * team + 0.10 * (10 - r), 2)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — INSERT
# ══════════════════════════════════════════════════════════════════════════════

def insert_startup(data: dict, founder_id: str) -> bool:
    """
    Inserts into BOTH startup_signals and startups tables.
    Returns True if inserted, False if skipped (duplicate).
    """
    name = (data.get("company_name") or "").strip()
    if not name:
        return False

    db = SessionLocal()
    try:
        if startup_exists(db, name):
            log.info(f"  [skip] '{name}' already exists.")
            return False

        final_score = _calculate_final_score(data)

        # ── Insert into startup_signals (analytics / raw scores) ──────────────
        signal = StartupSignal(
            name=name,
            domain=data.get("domain", "Technology"),
            description=data.get("description", "")[:1000],
            traction_score=int(data.get("traction_score", 5)),
            innovation_score=int(data.get("innovation_score", 5)),
            market_trend_score=int(data.get("market_trend_score", 5)),
            team_strength_score=int(data.get("team_strength_score", 5)),
            risk_score=int(data.get("risk_score", 5)),
            final_score=final_score,
        )
        db.add(signal)

        # ── Insert into startups (what /get-startups returns to frontend) ──────
        startup = Startup(
            name=name,
            domain=data.get("domain", "Technology"),
            description=data.get("description", "")[:1000],
            funding_stage=data.get("funding_stage", "Seed") or "Seed",
            risk_level=_score_to_risk(float(data.get("risk_score", 5))),
            traction_score=float(data.get("traction_score", 5)),
            market_score=float(data.get("market_trend_score", 5)),
            team_score=float(data.get("team_strength_score", 5)),
            innovation_score=float(data.get("innovation_score", 5)),
            location=data.get("location", "") or "",
            required_skills=data.get("required_skills", "") or "",
            founder_id=founder_id,
        )
        db.add(startup)

        db.commit()
        log.info(f"  [inserted] '{name}' → startups + startup_signals")
        return True

    except Exception as e:
        db.rollback()
        log.error(f"  DB error inserting '{name}': {e}")
        return False
    finally:
        db.close()


def _score_to_risk(risk_score: float) -> str:
    if risk_score <= 3:
        return "low"
    if risk_score <= 6:
        return "medium"
    return "high"


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE CYCLE
# ══════════════════════════════════════════════════════════════════════════════

def run_cycle(founder_id: str) -> int:
    """Runs one full scrape → enrich → insert cycle. Returns count inserted."""
    log.info("=" * 50)
    log.info("Pipeline running...")
    log.info("=" * 50)

    articles = scrape_rss()
    if not articles:
        log.warning("No articles scraped this cycle.")
        return 0

    inserted = 0
    for article in articles:
        if inserted >= MAX_PER_CYCLE:
            break
        try:
            enriched = enrich_with_ai(article)
            if not enriched:
                continue
            if insert_startup(enriched, founder_id):
                inserted += 1
            time.sleep(2)  # be polite to Gemini rate limits
        except Exception as e:
            log.error(f"Cycle error on '{article.get('name', '?')}': {e}")
            continue

    log.info(f"Cycle complete — {inserted} new startups inserted.")
    return inserted


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — CONTINUOUS LOOP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    log.info("=" * 55)
    log.info("  Nexus Venture — ETL Pipeline STARTED")
    log.info(f"  Interval : {INTERVAL_SECONDS}s")
    log.info(f"  Max/cycle: {MAX_PER_CYCLE}")
    log.info(f"  Gemini   : {'enabled' if gemini_model else 'disabled (fallback mode)'}")
    log.info("=" * 55)

    founder_id = get_or_create_pipeline_user()
    log.info(f"Pipeline founder_id: {founder_id}")

    cycle = 0
    while True:
        cycle += 1
        log.info(f"\n─── Cycle #{cycle} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ───")
        try:
            run_cycle(founder_id)
        except Exception as e:
            log.error(f"Unhandled cycle error: {e}")

        log.info(f"Sleeping {INTERVAL_SECONDS}s until next cycle...")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
