from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine, Base
from backend.models import user, startup, investment, chat # Ensure models are loaded
from backend.routes import auth, startups, investments, chat as chat_routes
from backend.routes import nexus_chat as nexus_chat_routes
from backend.config.settings import settings

# Create all tables in the database (development only, for production use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the Nexus Venture Startup Platform",
    version="1.0.0"
)

# Configure CORS for frontend deployment or local development
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://startup-nexus-platform.lovable.app",
    "*" # Allowing all for initial setup, restrict in production!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(startups.router)
app.include_router(investments.router)
app.include_router(chat_routes.router)
app.include_router(nexus_chat_routes.router)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for API documentation."}
