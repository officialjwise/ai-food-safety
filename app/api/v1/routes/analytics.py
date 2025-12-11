from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db

router = APIRouter()

@router.get("/market")
async def get_market_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_admin),
) -> Any:
    """
    Get market-wide analytics (Admin only).
    """
    # Example: Count total users, vendors, surplus listings
    total_users = await db.scalar(select(func.count(models.User.id)))
    total_vendors = await db.scalar(select(func.count(models.VendorProfile.id)))
    total_surplus = await db.scalar(select(func.count(models.SurplusListing.id)))
    
    return {
        "total_users": total_users,
        "total_vendors": total_vendors,
        "total_surplus_listings": total_surplus
    }

@router.get("/vendor")
async def get_vendor_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_vendor),
) -> Any:
    """
    Get vendor-specific analytics.
    """
    result = await db.execute(select(models.VendorProfile).filter(models.VendorProfile.user_id == current_user.id))
    vendor_profile = result.scalars().first()
    
    if not vendor_profile:
        return {"error": "Vendor profile not found"}

    # Example: Count active surplus listings
    active_surplus = await db.scalar(
        select(func.count(models.SurplusListing.id))
        .filter(models.SurplusListing.vendor_id == vendor_profile.id)
        .filter(models.SurplusListing.status == models.SurplusStatus.AVAILABLE)
    )
    
    return {
        "active_surplus_listings": active_surplus
    }
