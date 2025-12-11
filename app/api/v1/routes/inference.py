from typing import Any, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.db import models
from app.db.database import get_db
from app.schemas import inference as inference_schemas
from app.services.ml_service import ml_service
from app.services.nutrition_service import nutrition_service

router = APIRouter()

@router.post("/", response_model=inference_schemas.InferenceResponse)
async def create_inference(
    *,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Upload image for food safety inference.
    """
    # In a real app, save file to S3/disk
    image_path = f"uploads/{file.filename}"
    
    # Call ML Service
    prediction = await ml_service.predict(image_path)
    
    # Try to find matching food item by label
    result = await db.execute(
        select(models.FoodItem)
        .filter(models.FoodItem.canonical_name.ilike(f"%{prediction['label']}%"))
    )
    food_item = result.scalars().first()
    
    # Get nutrition data if food item found
    nutrition = None
    if food_item:
        nutrition = await nutrition_service.get_nutrition_by_food_id(db, food_item.id)
    
    inference = models.MLInference(
        user_id=current_user.id,
        image_path=image_path,
        food_item_id=food_item.id if food_item else None,
        label=prediction["label"],
        confidence=prediction["confidence"],
        contamination_score=prediction["contamination_score"]
    )
    db.add(inference)
    await db.commit()
    await db.refresh(inference)
    
    response = inference_schemas.InferenceResponse.model_validate(inference)
    response.nutrition_info = nutrition
    return response


@router.get("/{id}", response_model=inference_schemas.InferenceResponse)
async def read_inference(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get inference result by ID.
    """
    result = await db.execute(select(models.MLInference).filter(models.MLInference.id == id))
    inference = result.scalars().first()
    if not inference:
        raise HTTPException(status_code=404, detail="Inference not found")
    if inference.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this inference")
        
    return inference
