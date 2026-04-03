"""
cli_demo.py
-----------
Interactive command-line demo for the Nexus Venture AI Recommendation Chatbot.
Run this directly to test all four roles without needing the FastAPI server.

Usage:
    python -m backend.chatbot.cli_demo

FUTURE EXTENSION:
- Replace this CLI with a React/Next.js chat UI consuming the /nexus-chat API.
"""

from backend.chatbot.chatbot import run_chatbot

# ── Sample profiles for each role ─────────────────────────────────────────────
DEMO_PROFILES = {
    "investor": {
        "skills":                  "finance investment portfolio management due diligence",
        "interests":               "AI Healthcare Fintech",
        "experience_level":        "senior",
        "preferred_funding_stage": "seed series a",
        "location":                "Mumbai",
    },
    "founder": {
        "skills":                  "python machine learning nlp product management",
        "interests":               "AI EdTech Healthcare",
        "experience_level":        "mid",
        "preferred_funding_stage": "pre-seed seed",
        "location":                "Delhi",
    },
    "seeker": {
        "skills":                  "python data science tensorflow machine learning",
        "interests":               "AI Healthcare AgriTech",
        "experience_level":        "junior",
        "preferred_funding_stage": "seed",
        "location":                "Bangalore",
    },
    "collaborator": {
        "skills":                  "react node.js python full stack",
        "interests":               "Fintech EdTech HRTech",
        "experience_level":        "mid",
        "preferred_funding_stage": "pre-seed seed",
        "location":                "Mumbai",
    },
}


def run_demo():
    print("\n" + "=" * 60)
    print("   NEXUS VENTURE — AI Recommendation Chatbot Demo")
    print("=" * 60)
    print("\nAvailable roles: investor | founder | seeker | collaborator")
    print("Type 'all' to run all four demo profiles.\n")

    choice = input("Enter role (or 'all'): ").strip().lower()

    roles_to_run = list(DEMO_PROFILES.keys()) if choice == "all" else [choice]

    for role in roles_to_run:
        if role not in DEMO_PROFILES:
            print(f"\n[!] Unknown role '{role}'. Skipping.")
            continue

        profile = DEMO_PROFILES[role]
        print(f"\n{'='*60}")
        print(f"  Running demo for role: {role.upper()}")
        print(f"  Skills   : {profile['skills']}")
        print(f"  Interests: {profile['interests']}")
        print(f"  Location : {profile['location']}")
        print(f"{'='*60}")

        output = run_chatbot(role=role, **profile, top_n=5)
        print(output)

    print("\n[Demo complete. Run the FastAPI server for the full API experience.]\n")


if __name__ == "__main__":
    run_demo()
