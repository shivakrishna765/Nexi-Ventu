import sys
import os
import time
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import schedule
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import SessionLocal, engine, Base
from backend.models.startup_signal import StartupSignal

Base.metadata.create_all(bind=engine)

print("🚀 PIPELINE STARTED")

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    print("Loaded API Key:", API_KEY[:10])  # debug
else:
    print("Loaded API Key: None")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

def test_gemini():
    try:
        response = model.generate_content("Say OK")
        print("Gemini working:", response.text.strip())
        return True
    except Exception as e:
        print("Gemini API ERROR:", e)
        return False

def test_insert():
    print("[DEBUG] Running test_insert()...")
    db = SessionLocal()
    try:
        dummy = StartupSignal(
            name="Test Dummy AI",
            domain="Testing",
            description="Dummy descriptions for testing DB insert.",
            traction_score=5,
            innovation_score=5,
            market_trend_score=5,
            team_strength_score=5,
            risk_score=5,
            final_score=5.0
        )
        print("INSERTING: Test Dummy AI")
        db.add(dummy)
        db.commit()
        print("Inserted successfully")
    except Exception as e:
        print("DB ERROR:", e)
        db.rollback()
    finally:
        db.close()

def scrape_news():
    print("[DEBUG] Running scrape_news()...")
    url = "https://techcrunch.com/category/startups/feed/"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        print("[DEBUG] scrape_news() -> Scraped RSS successfully.")
        return response.text
    except Exception as e:
        print("[DEBUG] scrape_news() -> Error scraping data:", e)
        return None

def extract_startup_info(html_content):
    print("[DEBUG] Running extract_startup_info()...")
    startups = []
    if not html_content:
        return startups
        
    soup = BeautifulSoup(html_content, "xml")
    items = soup.find_all("item")
    
    for item in items[:20]:
        title = item.title.text if item.title else ""
        description = item.description.text if item.description else ""
        clean_desc = BeautifulSoup(description, "html.parser").get_text(separator=" ").strip()
        name = title.split("raises")[0].split("secures")[0].split("launches")[0].strip()
        
        if not clean_desc or len(clean_desc) < 10:
            print(f"[DEBUG] Skipping {name[:15]}... due to empty description.")
            continue
            
        startups.append({
            "name": name[:100],
            "title": title,
            "description": clean_desc
        })
    print(f"[DEBUG] extract_startup_info() -> Extracted {len(startups)} valid startups.")
    return startups

def process_with_ai(text):
    try:
        prompt = f"""
You are an expert startup analyst and venture capital advisor.

Your task is to extract structured startup intelligence from the given text.

IMPORTANT:
* Focus ONLY on actual startups or companies
* Ignore events, general news, or unrelated content
* If no real startup/company is present, return "company_name": null

---
TEXT:
{text}
---

Return ONLY valid JSON (no explanation):
{{
"company_name": "",
"domain": "",
"description": "",
"traction_score": 0,
"innovation_score": 0,
"market_trend_score": 0,
"team_strength_score": 0,
"risk_score": 0
}}

---
SCORING GUIDELINES:
traction_score (0-10): Based on growth, users, funding.
innovation_score (0-10): Based on uniqueness or deep tech.
market_trend_score (0-10): Based on industry demand.
team_strength_score (0-10): Based on founder background.
risk_score (0-10): High risk = 10, Low risk = 0.

STRICT RULES:
* If no startup is found: return {{"company_name": null}}
* Keep output strictly JSON.
"""

        response = model.generate_content(prompt)
        ai_text = response.text.strip()

        if ai_text.startswith("```json"):
            ai_text = ai_text[7:]
        if ai_text.startswith("```"):
            ai_text = ai_text[3:]
        if ai_text.endswith("```"):
            ai_text = ai_text[:-3]

        import json
        ai_data = json.loads(ai_text)
        print("AI OUTPUT:", ai_data)
        
        if not ai_data.get("company_name"):
            print("No valid startup found in text. Returning None.")
            return None
            
        return ai_data
    except Exception as e:
        print("AI ERROR:", e)
        return None

def calculate_score(signals):
    t_score = float(signals.get('traction_score', 0))
    m_score = float(signals.get('market_trend_score', 0))
    i_score = float(signals.get('innovation_score', 0))
    team_score = float(signals.get('team_strength_score', 0))
    r_score = float(signals.get('risk_score', 10))
    
    final_score = (
        0.30 * t_score +
        0.25 * m_score +
        0.20 * i_score +
        0.15 * team_score +
        0.10 * (10 - r_score)
    )
    return round(final_score, 2)

def store_in_db(name, url_text, signals, final_score):
    db = SessionLocal()
    try:
        existing = db.query(StartupSignal).filter(StartupSignal.name == name).first()
        if existing:
            print("[DEBUG] store_in_db() -> Skipped, existing entry found.")
            return False

        new_signal = StartupSignal(
            name=name,
            domain=signals.get('domain', 'Unknown'),
            description=url_text,
            traction_score=int(signals.get('traction_score', 0)),
            innovation_score=int(signals.get('innovation_score', 0)),
            market_trend_score=int(signals.get('market_trend_score', 0)),
            team_strength_score=int(signals.get('team_strength_score', 0)),
            risk_score=int(signals.get('risk_score', 10)),
            final_score=final_score
        )
        print("INSERTING:", name)
        db.add(new_signal)
        db.commit()
        print("Inserted successfully")
        return True
    except Exception as e:
        print("DB ERROR:", e)
        db.rollback()
        return False
    finally:
        db.close()

def run_pipeline():
    print("====== PIPELINE START ======")
    raw_data = scrape_news()
    
    startups = extract_startup_info(raw_data)
    
    successful_inserts = 0
    for startup in startups:
        if successful_inserts >= 5: 
            break
            
        combined_text = f"Title: {startup['title']}\nDesc: {startup['description']}"
        ai_data = process_with_ai(combined_text)
        
        if not ai_data:
            print("Skipping due to AI failure")
            continue
            
        f_score = calculate_score(ai_data)
        success = store_in_db(startup['name'], combined_text, ai_data, f_score)
        if success:
            successful_inserts += 1
        time.sleep(2) 
            
    print(f"====== PIPELINE FINISHED: {successful_inserts} new rows added ======")

def main():
    if not test_gemini():
        print("Stopping pipeline due to API failure")
        return

    test_insert()
    run_pipeline()
    schedule.every(6).hours.do(run_pipeline)
    print("[DEBUG] ETL Scheduler Running...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
