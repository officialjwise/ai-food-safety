from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db
from app.schemas import food_item as food_schemas
from app.schemas import nutrition as nutrition_schemas
from app.services.nutrition_service import nutrition_service

router = APIRouter()

@router.get("/", response_model=List[food_schemas.FoodItem])
async def list_food_items(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: str = None,
) -> Any:
    """
    List all food items with optional category filter
    """
    query = select(models.FoodItem)
    
    if category:
        query = query.filter(models.FoodItem.category == category)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/search")
async def search_food_items(
    db: AsyncSession = Depends(get_db),
    q: str = "",
    limit: int = 10,
) -> Any:
    """
    Search food items by name
    """
    results = await nutrition_service.search_foods(db, q, limit)
    return {
        "success": True,
        "message": f"Found {len(results)} items",
        "data": results
    }

@router.get("/{id}", response_model=food_schemas.FoodItem)
async def get_food_item(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    """
    Get food item by ID
    """
    result = await db.execute(select(models.FoodItem).filter(models.FoodItem.id == id))
    food_item = result.scalars().first()
    
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
    
    return food_item

@router.get("/{id}/nutrition")
async def get_food_nutrition(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    """
    Get comprehensive nutrition data for a food item
    """
    nutrition_data = await nutrition_service.get_nutrition_by_food_id(db, id)
    
    if not nutrition_data:
        raise HTTPException(
            status_code=404,
            detail="Nutrition data not found for this food item"
        )
    
    return {
        "success": True,
        "message": "Nutrition data retrieved successfully",
        "data": nutrition_data
    }

@router.post("/", response_model=food_schemas.FoodItem)
async def create_food_item(
    *,
    db: AsyncSession = Depends(get_db),
    food_in: food_schemas.FoodItemCreate,
    current_user: models.User = Depends(dependencies.get_current_active_admin),
) -> Any:
    """
    Create a new food item (Admin only)
    """
    # Check if food item already exists
    result = await db.execute(
        select(models.FoodItem)
        .filter(models.FoodItem.canonical_name == food_in.canonical_name)
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Food item with this name already exists"
        )
    
    food_item = models.FoodItem(**food_in.model_dump())
    db.add(food_item)
    await db.commit()
    await db.refresh(food_item)
    
    return food_item

@router.post("/{id}/nutrition")
async def add_nutrition_data(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    nutrition_in: nutrition_schemas.NutritionDataCreate,
    current_user: models.User = Depends(dependencies.get_current_active_admin),
) -> Any:
    """
    Add nutrition data for a food item (Admin only)
    """
    # Check if food item exists
    result = await db.execute(select(models.FoodItem).filter(models.FoodItem.id == id))
    food_item = result.scalars().first()
    
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
    
    # Check if nutrition data already exists
    result = await db.execute(
        select(models.NutritionData)
        .filter(models.NutritionData.food_item_id == id)
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Nutrition data already exists for this food item. Use PUT to update."
        )
    
    # Create nutrition data
    nutrition_data = models.NutritionData(
        **nutrition_in.model_dump(),
        food_item_id=id
    )
    db.add(nutrition_data)
    await db.commit()
    
    return {
        "success": True,
        "message": "Nutrition data added successfully",
        "food_item_id": id
    }

@router.put("/{id}/nutrition")
async def update_nutrition_data(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    nutrition_in: nutrition_schemas.NutritionDataUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_admin),
) -> Any:
    """
    Update nutrition data for a food item (Admin only)
    """
    # Get existing nutrition data
    result = await db.execute(
        select(models.NutritionData)
        .filter(models.NutritionData.food_item_id == id)
    )
    nutrition_data = result.scalars().first()
    
    if not nutrition_data:
        raise HTTPException(
            status_code=404,
            detail="Nutrition data not found for this food item"
        )
    
    # Update only provided fields
    update_data = nutrition_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(nutrition_data, field, value)
    
    db.add(nutrition_data)
    await db.commit()
    
    return {
        "success": True,
        "message": "Nutrition data updated successfully"
    }
