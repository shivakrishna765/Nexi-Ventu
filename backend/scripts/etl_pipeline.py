"""
etl_pipeline.py
---------------
Continuous data ingestion pipeline for Nexus Venture.

Strategy per cycle:
  1. Scrape multiple RSS feeds for fresh articles
  2. Enrich with Gemini AI (or rule-based fallback)
  3. Insert new entries into startups + startup_signals tables
  4. When real sources are exhausted, generate synthetic startups
     so the frontend always gets fresh data every cycle

Run:
    python -m backend.scripts.etl_pipeline
"""

import os, sys, time, json, random, hashlib, logging, requests
from datetime import datetime
from bs4 import BeautifulSoup

# ── Path & env setup ───────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import google.generativeai as genai
from backend.database.database import SessionLocal, engine, Base
import backend.models
from backend.models.startup_signal import StartupSignal
from backend.models.startup import Startup
from backend.models.user import User
from backend.utils.auth import get_password_hash

# ── Config ─────────────────────────────────────────────────────────────────────
INTERVAL_SECONDS    = 60      # seconds between cycles
MAX_REAL_PER_CYCLE  = 5       # max inserts from real RSS per cycle
SYNTHETIC_PER_CYCLE = 3       # synthetic entries to generate if real sources dry up
PIPELINE_EMAIL      = "pipeline@nexus.dev"

# Multiple RSS sources — more variety, slower depletion
RSS_FEEDS = [
    "https://techcrunch.com/category/startups/feed/",
    "https://feeds.feedburner.com/venturebeat/SZYF",
    "https://www.entrepreneur.com/latest.rss",
    "https://feeds.feedburner.com/TechCrunch",
]

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PIPELINE] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline")

# ── Gemini ─────────────────────────────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
gemini_model = None
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")
        log.info("Gemini AI ready.")
    except Exception as e:
        log.warning(f"Gemini init failed: {e}")
else:
    log.warning("GEMINI_API_KEY not set — using rule-based enrichment.")

Base.metadata.create_all(bind=engine)

# ══════════════════════════════════════════════════════════════════════════════
# SYNTHETIC DATA BANK
# Realistic startup templates — combined with random variation each cycle
# so every generated entry has a unique name and is never a duplicate.
# ══════════════════════════════════════════════════════════════════════════════

_DOMAINS = ["AI", "Healthcare", "Fintech", "EdTech", "CleanTech", "AgriTech",
            "Cybersecurity", "Logistics", "HRTech", "Retail", "Mental Health",
            "LegalTech", "PropTech", "FoodTech", "SpaceTech", "BioTech"]

_PREFIXES = ["Nova", "Apex", "Flux", "Nexo", "Velo", "Kira", "Zeta", "Orbi",
             "Plex", "Aura", "Sync", "Lumi", "Helix", "Qubit", "Prism", "Echo",
             "Forge", "Drift", "Spark", "Pulse", "Nimbus", "Cipher", "Axiom"]

_SUFFIXES = ["AI", "Labs", "Tech", "IO", "Hub", "Base", "Core", "Works",
             "Mind", "Flow", "Sense", "Link", "Nest", "Forge", "Shift", "Wave"]

_STAGES = ["Pre-Seed", "Seed", "Series A", "Series B"]

_LOCATIONS = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai",
              "San Francisco", "New York", "London", "Berlin", "Singapore", "Dubai"]

_SKILLS_MAP = {
    "AI":           "Python Machine Learning TensorFlow NLP Computer Vision",
    "Healthcare":   "Python ML Healthcare IT FHIR Data Analytics",
    "Fintech":      "Python Node.js Blockchain React Data Science",
    "EdTech":       "React Node.js Python NLP Gamification",
    "CleanTech":    "IoT Python Data Analytics Embedded Systems",
    "AgriTech":     "Computer Vision Python Drone Tech Data Science",
    "Cybersecurity":"Python Network Security Ethical Hacking SIEM",
    "Logistics":    "Python Blockchain React Node.js Supply Chain",
    "HRTech":       "NLP Python React Machine Learning HR Analytics",
    "Retail":       "Computer Vision Python IoT React Analytics",
    "Mental Health":"NLP Python React Psychology CBT",
    "LegalTech":    "NLP Python React Legal Knowledge Automation",
    "PropTech":     "React Python Data Analytics GIS Mapping",
    "FoodTech":     "IoT Python React Supply Chain Analytics",
    "SpaceTech":    "Python C++ Embedded Systems Signal Processing",
    "BioTech":      "Python Bioinformatics ML Data Science R",
}

_DESC_TEMPLATES = [
    "{name} is building an {domain} platform that uses AI to automate {action} for {target}, reducing costs by up to {pct}%.",
    "{name} provides {domain} solutions powered by machine learning, helping {target} to {action} more efficiently.",
    "Founded in {year}, {name} is disrupting the {domain} space by enabling {target} to {action} using real-time data.",
    "{name} leverages {domain} technology to solve {problem} for {target}, with {pct}% faster outcomes.",
    "An AI-first {domain} startup, {name} helps {target} {action} through intelligent automation and predictive analytics.",
]

_ACTIONS = ["automate workflows", "reduce operational costs", "predict outcomes",
            "optimise resource allocation", "improve decision-making", "scale operations",
            "detect anomalies", "personalise experiences", "streamline processes"]

_TARGETS = ["enterprises", "SMEs", "hospitals", "farmers", "students",
            "investors", "HR teams", "logistics companies", "retail chains",
            "financial institutions", "government agencies", "startups"]

_PROBLEMS = ["inefficiency", "data silos", "manual errors", "high costs",
             "lack of visibility", "slow processes", "poor user experience"]


def _generate_synthetic_startup(cycle: int, idx: int) -> dict:
    """
    Generates a unique synthetic startup entry.
    Uses cycle + idx + timestamp to ensure the name is never repeated.
    """
    random.seed(int(time.time()) + cycle * 100 + idx)
    domain   = random.choice(_DOMAINS)
    prefix   = random.choice(_PREFIXES)
    suffix   = random.choice(_SUFFIXES)
    # Add a short hash suffix to guarantee uniqueness across runs
    uid      = hashlib.md5(f"{prefix}{suffix}{cycle}{idx}{time.time()}".encode()).hexdigest()[:4].upper()
    name     = f"{prefix}{suffix} {uid}"

    template = random.choice(_DESC_TEMPLATES)
    desc = template.format(
        name=name,
        domain=domain,
        action=random.choice(_ACTIONS),
        target=random.choice(_TARGETS),
        problem=random.choice(_PROBLEMS),
        pct=random.randint(20, 70),
        year=random.randint(2021, 2025),
    )

    return {
        "company_name":      name,
        "domain":            domain,
        "description":       desc,
        "funding_stage":     random.choice(_STAGES),
        "location":          random.choice(_LOCATIONS),
        "required_skills":   _SKILLS_MAP.get(domain, "Python React Node.js"),
        "traction_score":    random.randint(5, 10),
        "innovation_score":  random.randint(5, 10),
        "market_trend_score": random.randint(5, 10),
        "team_strength_score": random.randint(5, 10),
        "risk_score":        random.randint(2, 7),
    }


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE USER
# ══════════════════════════════════════════════════════════════════════════════

def get_or_create_pipeline_user() -> str:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == PIPELINE_EMAIL).first()
        if not user:
            user = User(
                name="Pipeline Bot",
                email=PIPELINE_EMAIL,
                password_hash=get_password_hash("pipeline_internal_only"),
                role="founder",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            log.info(f"Created pipeline user: {user.id}")
        return str(user.id)
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════════════
# DUPLICATE CHECK
# ══════════════════════════════════════════════════════════════════════════════

def name_exists(db, name: str) -> bool:
    return db.query(Startup).filter(Startup.name == name).first() is not None


# ══════════════════════════════════════════════════════════════════════════════
# SCRAPE — multiple RSS feeds
# ══════════════════════════════════════════════════════════════════════════════

def scrape_all_feeds() -> list[dict]:
    """Scrapes all RSS feeds and returns deduplicated article list."""
    seen_titles = set()
    articles = []

    for url in RSS_FEEDS:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "xml")

            for item in soup.find_all("item")[:20]:
                title = (item.title.text if item.title else "").strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)

                raw_desc = item.description.text if item.description else ""
                clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text(" ").strip()
                if len(clean_desc) < 20:
                    continue

                # Extract company name from headline
                name = title
                for splitter in [" raises", " secures", " launches", " acquires",
                                  " closes", " lands", " gets", " nabs"]:
                    if splitter in name.lower():
                        name = name[: name.lower().index(splitter)].strip()
                        break
                name = name[:120]

                articles.append({"name": name, "title": title, "description": clean_desc})

        except Exception as e:
            log.warning(f"Feed {url} failed: {e}")
            continue

    log.info(f"Scraped {len(articles)} unique articles from {len(RSS_FEEDS)} feeds.")
    return articles


# ══════════════════════════════════════════════════════════════════════════════
# AI ENRICHMENT
# ══════════════════════════════════════════════════════════════════════════════

_PROMPT = """You are a startup analyst. Extract structured data from the text.
If no real startup is present return {{"company_name": null}}.
Return ONLY valid JSON, no explanation.

TEXT: {text}

JSON:
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

funding_stage: Pre-Seed | Seed | Series A | Series B | Series C
required_skills: comma-separated tech skills
Scores 0-10. risk_score: 10=very risky."""


def enrich(article: dict) -> dict | None:
    text = f"Title: {article['title']}\n{article['description'][:600]}"

    if gemini_model:
        for attempt in range(2):
            try:
                resp = gemini_model.generate_content(_PROMPT.format(text=text))
                raw = resp.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                data = json.loads(raw)
                if data.get("company_name"):
                    return data
                return None
            except Exception as e:
                log.warning(f"  Gemini attempt {attempt+1} failed: {e}")
                time.sleep(3)

    # Rule-based fallback
    return {
        "company_name":       article["name"],
        "domain":             _guess_domain(article["description"]),
        "description":        article["description"][:500],
        "funding_stage":      _guess_stage(article["title"]),
        "location":           "",
        "required_skills":    "",
        "traction_score":     5, "innovation_score": 5,
        "market_trend_score": 5, "team_strength_score": 5, "risk_score": 5,
    }


def _guess_domain(text: str) -> str:
    t = text.lower()
    checks = [
        (["health", "medical", "clinic", "pharma"], "Healthcare"),
        (["fintech", "payment", "bank", "crypto", "finance"], "Fintech"),
        (["ai", "machine learning", "llm", "gpt", "neural"], "AI"),
        (["edu", "learn", "school", "course", "tutor"], "EdTech"),
        (["agri", "farm", "crop", "harvest"], "AgriTech"),
        (["climate", "energy", "solar", "green", "carbon"], "CleanTech"),
        (["cyber", "security", "hack", "threat"], "Cybersecurity"),
        (["logistics", "supply chain", "delivery", "shipping"], "Logistics"),
        (["hr", "recruit", "talent", "hiring"], "HRTech"),
        (["retail", "ecommerce", "shop", "commerce"], "Retail"),
        (["mental", "therapy", "wellness", "mindful"], "Mental Health"),
        (["legal", "contract", "law", "compliance"], "LegalTech"),
    ]
    for keywords, domain in checks:
        if any(k in t for k in keywords):
            return domain
    return "Technology"


def _guess_stage(title: str) -> str:
    t = title.lower()
    for kw, stage in [("series c", "Series C"), ("series b", "Series B"),
                      ("series a", "Series A"), ("seed", "Seed"), ("pre-seed", "Pre-Seed")]:
        if kw in t:
            return stage
    return "Seed"


# ══════════════════════════════════════════════════════════════════════════════
# INSERT
# ══════════════════════════════════════════════════════════════════════════════

def _risk_label(score: float) -> str:
    return "low" if score <= 3 else ("medium" if score <= 6 else "high")


def _final_score(d: dict) -> float:
    return round(
        0.30 * float(d.get("traction_score", 5)) +
        0.25 * float(d.get("market_trend_score", 5)) +
        0.20 * float(d.get("innovation_score", 5)) +
        0.15 * float(d.get("team_strength_score", 5)) +
        0.10 * (10 - float(d.get("risk_score", 5))), 2
    )


def insert(data: dict, founder_id: str) -> bool:
    name = (data.get("company_name") or "").strip()
    if not name:
        return False

    db = SessionLocal()
    try:
        if name_exists(db, name):
            log.info(f"  [skip] '{name}' already in DB.")
            return False

        fs = _final_score(data)

        db.add(StartupSignal(
            name=name,
            domain=data.get("domain", "Technology"),
            description=(data.get("description", ""))[:1000],
            traction_score=int(data.get("traction_score", 5)),
            innovation_score=int(data.get("innovation_score", 5)),
            market_trend_score=int(data.get("market_trend_score", 5)),
            team_strength_score=int(data.get("team_strength_score", 5)),
            risk_score=int(data.get("risk_score", 5)),
            final_score=fs,
        ))

        db.add(Startup(
            name=name,
            domain=data.get("domain", "Technology"),
            description=(data.get("description", ""))[:1000],
            funding_stage=data.get("funding_stage") or "Seed",
            risk_level=_risk_label(float(data.get("risk_score", 5))),
            traction_score=float(data.get("traction_score", 5)),
            market_score=float(data.get("market_trend_score", 5)),
            team_score=float(data.get("team_strength_score", 5)),
            innovation_score=float(data.get("innovation_score", 5)),
            location=data.get("location") or "",
            required_skills=data.get("required_skills") or "",
            founder_id=founder_id,
        ))

        db.commit()
        log.info(f"  [inserted] '{name}' | {data.get('domain')} | {data.get('funding_stage')}")
        return True

    except Exception as e:
        db.rollback()
        log.error(f"  DB error for '{name}': {e}")
        return False
    finally:
        db.close()


def db_count() -> int:
    db = SessionLocal()
    try:
        return db.query(Startup).count()
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════════════
# CYCLE
# ══════════════════════════════════════════════════════════════════════════════

def run_cycle(founder_id: str, cycle: int) -> int:
    total_inserted = 0

    # ── Phase 1: real RSS data ─────────────────────────────────────────────────
    articles = scrape_all_feeds()
    for article in articles:
        if total_inserted >= MAX_REAL_PER_CYCLE:
            break
        try:
            enriched = enrich(article)
            if enriched and insert(enriched, founder_id):
                total_inserted += 1
            time.sleep(1)
        except Exception as e:
            log.error(f"  Article error: {e}")

    # ── Phase 2: synthetic fill-in ─────────────────────────────────────────────
    # Always generate synthetic entries so the DB grows every cycle
    log.info(f"Generating {SYNTHETIC_PER_CYCLE} synthetic startups...")
    for i in range(SYNTHETIC_PER_CYCLE):
        try:
            synthetic = _generate_synthetic_startup(cycle, i)
            if insert(synthetic, founder_id):
                total_inserted += 1
        except Exception as e:
            log.error(f"  Synthetic error: {e}")

    return total_inserted


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    log.info("=" * 55)
    log.info("  Nexus Venture — ETL Pipeline STARTED")
    log.info(f"  Interval      : {INTERVAL_SECONDS}s")
    log.info(f"  Real/cycle    : up to {MAX_REAL_PER_CYCLE}")
    log.info(f"  Synthetic/cycle: {SYNTHETIC_PER_CYCLE}")
    log.info(f"  Gemini        : {'enabled' if gemini_model else 'rule-based fallback'}")
    log.info("=" * 55)

    founder_id = get_or_create_pipeline_user()

    cycle = 0
    while True:
        cycle += 1
        log.info(f"\n{'─'*50}")
        log.info(f"Cycle #{cycle}  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log.info(f"{'─'*50}")

        try:
            inserted = run_cycle(founder_id, cycle)
            total = db_count()
            log.info(f"Cycle #{cycle} done — inserted: {inserted} | total in DB: {total}")
        except Exception as e:
            log.error(f"Unhandled cycle error: {e}")

        log.info(f"Sleeping {INTERVAL_SECONDS}s...")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
