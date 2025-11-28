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


# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": "development" if settings.DEBUG else "production"
    }


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


# ============================================================================
# IMPORT API ROUTES
# ============================================================================

from app.api.routes import (
    auth,
    deals,
    businesses,
    categories,  # ← NEW: Categories route
    favorites,
    reviews
)


# ============================================================================
# REGISTER ROUTERS
# ============================================================================

# Authentication routes
app.include_router(
    auth.router,
    prefix=settings.API_V1_PREFIX + "/auth",
    tags=["Authentication"]
)

# Deals routes
app.include_router(
    deals.router,
    prefix=settings.API_V1_PREFIX + "/deals",
    tags=["Deals"]
)

# Businesses routes
app.include_router(
    businesses.router,
    prefix=settings.API_V1_PREFIX + "/businesses",
    tags=["Businesses"]
)

# Categories routes (NEW!)
app.include_router(
    categories.router,
    prefix=settings.API_V1_PREFIX + "/categories",
    tags=["Categories"]
)

# Favorites routes
app.include_router(
    favorites.router,
    prefix=settings.API_V1_PREFIX + "/favorites",
    tags=["Favorites"]
)

# Reviews routes
app.include_router(
    reviews.router,
    prefix=settings.API_V1_PREFIX + "/reviews",
    tags=["Reviews"]
)


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

@app.on_event("startup")
async def startup_message():
    """Print startup message with available routes"""
    print("\n" + "="*60)
    print("🎯 SaveMate API - Successfully Started!")
    print("="*60)
    print(f"📚 Documentation: http://localhost:8000/docs")
    print(f"📖 ReDoc: http://localhost:8000/redoc")
    print(f"🏥 Health Check: http://localhost:8000/health")
    print("\n🔗 Available API Routes:")
    print(f"   • Authentication: {settings.API_V1_PREFIX}/auth")
    print(f"   • Deals: {settings.API_V1_PREFIX}/deals")
    print(f"   • Businesses: {settings.API_V1_PREFIX}/businesses")
    print(f"   • Categories: {settings.API_V1_PREFIX}/categories  ← NEW!")
    print(f"   • Favorites: {settings.API_V1_PREFIX}/favorites")
    print(f"   • Reviews: {settings.API_V1_PREFIX}/reviews")
    print("="*60 + "\n")