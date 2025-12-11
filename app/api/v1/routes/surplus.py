from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db
from app.schemas import surplus as surplus_schemas

router = APIRouter()

@router.post("/", response_model=surplus_schemas.SurplusListing)
async def create_surplus(
    *,
    db: AsyncSession = Depends(get_db),
    surplus_in: surplus_schemas.SurplusListingCreate,
    current_user: models.User = Depends(dependencies.get_current_active_vendor),
) -> Any:
    """
    Create a new surplus listing.
    """
    result = await db.execute(select(models.VendorProfile).filter(models.VendorProfile.user_id == current_user.id))
    vendor_profile = result.scalars().first()
    if not vendor_profile:
        raise HTTPException(status_code=400, detail="Vendor profile required")

    surplus = models.SurplusListing(
        **surplus_in.model_dump(),
        vendor_id=vendor_profile.id
    )
    db.add(surplus)
    await db.commit()
    await db.refresh(surplus)
    return surplus

@router.get("/", response_model=List[surplus_schemas.SurplusListing])
async def read_surplus(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get all available surplus listings.
    """
    result = await db.execute(
        select(models.SurplusListing)
        .filter(models.SurplusListing.status == models.SurplusStatus.AVAILABLE)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/{id}/claim", response_model=surplus_schemas.SurplusListing)
async def claim_surplus(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Claim a surplus listing (NGO only).
    """
    if current_user.role != models.UserRole.NGO:
        raise HTTPException(status_code=403, detail="Only NGOs can claim surplus")

    result = await db.execute(select(models.SurplusListing).filter(models.SurplusListing.id == id))
    surplus = result.scalars().first()
    if not surplus:
        raise HTTPException(status_code=404, detail="Surplus listing not found")
    if surplus.status != models.SurplusStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Surplus listing not available")

    surplus.status = models.SurplusStatus.CLAIMED
    surplus.claimed_by_ngo_id = current_user.id
    db.add(surplus)
    await db.commit()
    await db.refresh(surplus)
    return surplus
