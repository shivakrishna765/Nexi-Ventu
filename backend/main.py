import os
# Prevent OpenBLAS / numpy thread-count warnings on Windows
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine, Base
from backend.models import user, startup, investment, chat  # registers all ORM models
from backend.routes import auth, startups, investments, chat as chat_routes
from backend.routes import nexus_chat as nexus_chat_routes
from backend.config.settings import settings

# Auto-create any missing tables (safe — won't drop existing data)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the Nexus Venture Startup Platform",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://startup-nexus-platform.lovable.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(startups.router)
app.include_router(investments.router)
app.include_router(chat_routes.router)
app.include_router(nexus_chat_routes.router)

# ── Utility endpoints ──────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API docs."}

@app.get("/test")
def test():
    return {"message": "Backend working", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ── Startup log ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    print("\n" + "=" * 55, flush=True)
    print("  Nexus Venture Backend  —  RUNNING", flush=True)
    print("  URL  : http://127.0.0.1:8000", flush=True)
    print("  Docs : http://127.0.0.1:8000/docs", flush=True)
    print("  Test : http://127.0.0.1:8000/test", flush=True)
    print("=" * 55 + "\n", flush=True)
