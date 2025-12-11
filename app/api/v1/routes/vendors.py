from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db
from app.schemas import vendor as vendor_schemas

router = APIRouter()

@router.post("/profile", response_model=vendor_schemas.VendorProfile)
async def create_vendor_profile(
    *,
    db: AsyncSession = Depends(get_db),
    profile_in: vendor_schemas.VendorProfileCreate,
    current_user: models.User = Depends(dependencies.get_current_active_vendor),
) -> Any:
    """
    Create vendor profile for current user.
    """
    result = await db.execute(select(models.VendorProfile).filter(models.VendorProfile.user_id == current_user.id))
    existing_profile = result.scalars().first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Vendor profile already exists")
    
    profile = models.VendorProfile(
        **profile_in.model_dump(),
        user_id=current_user.id
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("/profile", response_model=vendor_schemas.VendorProfile)
async def read_vendor_profile(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_vendor),
) -> Any:
    """
    Get vendor profile for current user.
    """
    result = await db.execute(select(models.VendorProfile).filter(models.VendorProfile.user_id == current_user.id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Vendor profile not found")
    return profile
