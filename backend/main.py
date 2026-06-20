from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import create_tables
from core.config import settings
from api.routes import auth, profile, jobs, applications, gmail
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FirstJob API...")
    await create_tables()
    logger.info("Database tables ready ✓")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="FirstJob API",
    description="Multi-agent AI job application system for fresh graduates",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_origin_regex=r"https://first-job-.*-satvik2\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(gmail.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "app": "FirstJob API",
        "version": "1.0.0",
        "status": "running",
        "agents": {
            "profile_agent": "✓ Active",
            "job_scraper_agent": "✓ Active",
            "resume_tailor_agent": "✓ Active",
            "apply_agent": "✓ Active (via /jobs/{id}/apply)",
            "outreach_agent": "✓ Active (background)",
            "tracker_agent": "✓ Active",
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
