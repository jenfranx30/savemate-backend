"""
SaveMate API - Main Application
FastAPI backend for local deals platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 Starting SaveMate API...")
    await init_db()
    yield
    # Shutdown
    print("👋 Shutting down SaveMate API...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for SaveMate - Local Deals Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to SaveMate API",
        "status": "active",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": "development" if settings.DEBUG else "production"
    }


# API info endpoint
@app.get("/api/v1")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "description": "RESTful API for SaveMate - Find local deals near you",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }


# We'll add API routes here later
# from app.api.routes import auth, users, deals, categories
# app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
# app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["Users"])
# app.include_router(deals.router, prefix=settings.API_V1_PREFIX, tags=["Deals"])
# app.include_router(categories.router, prefix=settings.API_V1_PREFIX, tags=["Categories"])
