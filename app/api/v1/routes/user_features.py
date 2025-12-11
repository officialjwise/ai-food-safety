from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db
from app.schemas import ngo as ngo_schemas

router = APIRouter()

# Saved Items

@router.post("/saved-items", response_model=ngo_schemas.SavedItem)
async def save_food_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_data: ngo_schemas.SavedItemCreate,
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Save a food item to user's favorites
    """
    # Check if already saved
    result = await db.execute(
        select(models.SavedItem)
        .filter(models.SavedItem.user_id == current_user.id)
        .filter(models.SavedItem.item_id == item_data.item_id)
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already saved")
    
    # Check if food item exists
    result = await db.execute(
        select(models.FoodItem).filter(models.FoodItem.id == item_data.item_id)
    )
    food_item = result.scalars().first()
    
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
    
    saved_item = models.SavedItem(
        user_id=current_user.id,
        item_id=item_data.item_id
    )
    db.add(saved_item)
    await db.commit()
    await db.refresh(saved_item)
    
    return saved_item

@router.get("/saved-items", response_model=list[ngo_schemas.SavedItem])
async def list_saved_items(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List user's saved food items
    """
    result = await db.execute(
        select(models.SavedItem)
        .filter(models.SavedItem.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()

@router.delete("/saved-items/{item_id}")
async def delete_saved_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int,
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Remove food item from favorites
    """
    result = await db.execute(
        select(models.SavedItem)
        .filter(models.SavedItem.user_id == current_user.id)
        .filter(models.SavedItem.item_id == item_id)
    )
    saved_item = result.scalars().first()
    
    if not saved_item:
        raise HTTPException(status_code=404, detail="Saved item not found")
    
    await db.delete(saved_item)
    await db.commit()
    
    return {"success": True, "message": "Item removed from favorites"}

# Scan History

@router.get("/scan-history")
async def get_scan_history(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """
    Get user's ML inference (scan) history
    """
    result = await db.execute(
        select(models.MLInference)
        .filter(models.MLInference.user_id == current_user.id)
        .order_by(models.MLInference.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()

# Price Lookup History

@router.get("/price-history", response_model=list[ngo_schemas.PriceLookupHistory])
async def get_price_lookup_history(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """
    Get user's price lookup history
    """
    result = await db.execute(
        select(models.PriceLookupHistory)
        .filter(models.PriceLookupHistory.user_id == current_user.id)
        .order_by(models.PriceLookupHistory.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()
