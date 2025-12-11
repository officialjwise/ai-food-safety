from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db
from app.schemas import price as price_schemas

router = APIRouter()

@router.post("/", response_model=price_schemas.VendorPrice)
async def create_price(
    *,
    db: AsyncSession = Depends(get_db),
    price_in: price_schemas.VendorPriceCreate,
    current_user: models.User = Depends(dependencies.get_current_active_vendor),
) -> Any:
    """
    Create a new price listing.
    """
    # Ensure vendor profile exists
    result = await db.execute(select(models.VendorProfile).filter(models.VendorProfile.user_id == current_user.id))
    vendor_profile = result.scalars().first()
    if not vendor_profile:
        raise HTTPException(status_code=400, detail="Vendor profile required")

    price = models.VendorPrice(
        **price_in.model_dump(),
        vendor_id=vendor_profile.id
    )
    db.add(price)
    await db.commit()
    await db.refresh(price)
    return price

@router.get("/", response_model=List[price_schemas.VendorPrice])
async def read_prices(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.get_current_active_vendor),
) -> Any:
    """
    Get prices for the current vendor.
    """
    result = await db.execute(select(models.VendorProfile).filter(models.VendorProfile.user_id == current_user.id))
    vendor_profile = result.scalars().first()
    if not vendor_profile:
        return []

    result = await db.execute(
        select(models.VendorPrice)
        .filter(models.VendorPrice.vendor_id == vendor_profile.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
