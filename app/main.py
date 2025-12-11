from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1.routes import auth, users, vendors, prices, surplus, analytics, inference, food_items, ngo
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from app.core.middleware import RequestLoggingMiddleware
from app.core.logging_config import setup_logging
from app.db.database import AsyncSessionLocal
from app.db.init_db import init_db, create_admin_user
from app.db.database import engine

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up application...")
    
    # Initialize database
    await init_db(engine)
    
    # Create default admin user
    async with AsyncSessionLocal() as db:
        await create_admin_user(db)
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(vendors.router, prefix=f"{settings.API_V1_STR}/vendors", tags=["vendors"])
app.include_router(prices.router, prefix=f"{settings.API_V1_STR}/vendor/prices", tags=["prices"])
app.include_router(surplus.router, prefix=f"{settings.API_V1_STR}/surplus", tags=["surplus"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(inference.router, prefix=f"{settings.API_V1_STR}/inference", tags=["inference"])
app.include_router(food_items.router, prefix=f"{settings.API_V1_STR}/food-items", tags=["food-items"])
app.include_router(ngo.router, prefix=f"{settings.API_V1_STR}/ngo", tags=["ngo"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Food Safety Platform API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

