from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db
from app.schemas import ngo as ngo_schemas

router = APIRouter()

@router.post("/profile", response_model=ngo_schemas.NGOProfile)
async def create_ngo_profile(
    *,
    db: AsyncSession = Depends(get_db),
    profile_in: ngo_schemas.NGOProfileCreate,
    current_user: models.User = Depends(dependencies.get_current_active_ngo),
) -> Any:
    """
    Create NGO profile for current user
    """
    # Check if profile already exists
    result = await db.execute(
        select(models.NGOProfile).filter(models.NGOProfile.user_id == current_user.id)
    )
    existing_profile = result.scalars().first()
    
    if existing_profile:
        raise HTTPException(status_code=400, detail="NGO profile already exists")
    
    ngo_profile = models.NGOProfile(
        **profile_in.model_dump(),
        user_id=current_user.id
    )
    db.add(ngo_profile)
    await db.commit()
    await db.refresh(ngo_profile)
    
    return ngo_profile

@router.get("/profile", response_model=ngo_schemas.NGOProfile)
async def get_ngo_profile(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_ngo),
) -> Any:
    """
    Get current NGO's profile
    """
    result = await db.execute(
        select(models.NGOProfile).filter(models.NGOProfile.user_id == current_user.id)
    )
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="NGO profile not found")
    
    return profile

@router.put("/profile", response_model=ngo_schemas.NGOProfile)
async def update_ngo_profile(
    *,
    db: AsyncSession = Depends(get_db),
    profile_in: ngo_schemas.NGOProfileUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_ngo),
) -> Any:
    """
    Update NGO profile
    """
    result = await db.execute(
        select(models.NGOProfile).filter(models.NGOProfile.user_id == current_user.id)
    )
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="NGO profile not found")
    
    # Update only provided fields
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return profile

@router.get("/claims", response_model=list[ngo_schemas.SurplusClaim])
async def list_ngo_claims(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_ngo),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all claims made by current NGO
    """
    # Get NGO profile
    result = await db.execute(
        select(models.NGOProfile).filter(models.NGOProfile.user_id == current_user.id)
    )
    ngo_profile = result.scalars().first()
    
    if not ngo_profile:
        raise HTTPException(status_code=404, detail="NGO profile not found")
    
    # Get claims
    result = await db.execute(
        select(models.SurplusClaim)
        .filter(models.SurplusClaim.ngo_id == ngo_profile.id)
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()

@router.post("/claims/{claim_id}/collect", response_model=ngo_schemas.SurplusClaim)
async def mark_claim_collected(
    *,
    db: AsyncSession = Depends(get_db),
    claim_id: int,
    update_data: ngo_schemas.SurplusClaimUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_ngo),
) -> Any:
    """
    Mark a claim as collected with photo proof
    """
    from datetime import datetime
    
    # Get NGO profile
    result = await db.execute(
        select(models.NGOProfile).filter(models.NGOProfile.user_id == current_user.id)
    )
    ngo_profile = result.scalars().first()
    
    if not ngo_profile:
        raise HTTPException(status_code=404, detail="NGO profile not found")
    
    # Get claim
    result = await db.execute(
        select(models.SurplusClaim)
        .filter(models.SurplusClaim.id == claim_id)
        .filter(models.SurplusClaim.ngo_id == ngo_profile.id)
    )
    claim = result.scalars().first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Update claim
    claim.status = "collected"
    claim.timestamp_collected = datetime.utcnow()
    
    if update_data.collection_photo_proof:
        claim.collection_photo_proof = update_data.collection_photo_proof
    if update_data.notes:
        claim.notes = update_data.notes
    
    db.add(claim)
    
    # Update surplus status
    result = await db.execute(
        select(models.SurplusListing)
        .filter(models.SurplusListing.id == claim.surplus_id)
    )
    surplus = result.scalars().first()
    
    if surplus:
        surplus.status = models.SurplusStatus.COLLECTED
        db.add(surplus)
    
    await db.commit()
    await db.refresh(claim)
    
    return claim

@router.delete("/claims/{claim_id}")
async def cancel_claim(
    *,
    db: AsyncSession = Depends(get_db),
    claim_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_ngo),
) -> Any:
    """
    Cancel a surplus claim
    """
    # Get NGO profile
    result = await db.execute(
        select(models.NGOProfile).filter(models.NGOProfile.user_id == current_user.id)
    )
    ngo_profile = result.scalars().first()
    
    if not ngo_profile:
        raise HTTPException(status_code=404, detail="NGO profile not found")
    
    # Get claim
    result = await db.execute(
        select(models.SurplusClaim)
        .filter(models.SurplusClaim.id == claim_id)
        .filter(models.SurplusClaim.ngo_id == ngo_profile.id)
    )
    claim = result.scalars().first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Update claim and surplus
    claim.status = "cancelled"
    db.add(claim)
    
    result = await db.execute(
        select(models.SurplusListing)
        .filter(models.SurplusListing.id == claim.surplus_id)
    )
    surplus = result.scalars().first()
    
    if surplus:
        surplus.status = models.SurplusStatus.AVAILABLE
        db.add(surplus)
    
    await db.commit()
    
    return {"success": True, "message": "Claim cancelled successfully"}
