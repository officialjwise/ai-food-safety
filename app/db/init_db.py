from sqlalchemy.ext.asyncio import AsyncEngine
from app.db.database import engine, Base
from app.db import models
from app.core import security
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def init_db(engine: AsyncEngine):
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")

async def create_admin_user(db):
    """Create default admin user if not exists"""
    # Check if admin exists
    result = await db.execute(
        select(models.User).filter(models.User.role == models.UserRole.ADMIN)
    )
    admin = result.scalars().first()
    
    if not admin:
        # Create admin user
        admin = models.User(
            email="admin@foodsafety.com",
            hashed_password=security.get_password_hash("admin123"),
            full_name="System Administrator",
            role=models.UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        logger.info("Default admin user created: admin@foodsafety.com / admin123")
    else:
        logger.info("Admin user already exists")
