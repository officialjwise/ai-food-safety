from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import models
import logging

logger = logging.getLogger(__name__)

class NutritionService:
    """Service for retrieving and managing nutrition data"""
    
    async def get_nutrition_by_food_name(self, db: AsyncSession, food_name: str) -> dict:
        """
        Get nutrition information by food name (case-insensitive search)
        """
        try:
            # Search for food item by canonical name
            result = await db.execute(
                select(models.FoodItem)
                .filter(models.FoodItem.canonical_name.ilike(f"%{food_name}%"))
            )
            food_item = result.scalars().first()
            
            if not food_item:
                logger.warning(f"Food item not found: {food_name}")
                return None
            
            return await self.get_nutrition_by_food_id(db, food_item.id)
            
        except Exception as e:
            logger.error(f"Error fetching nutrition data for {food_name}: {str(e)}")
            return None
    
    async def get_nutrition_by_food_id(self, db: AsyncSession, food_item_id: int) -> dict:
        """
        Get nutrition information by food item ID
        """
        try:
            # Fetch nutrition data with food item details
            result = await db.execute(
                select(models.NutritionData)
                .filter(models.NutritionData.food_item_id == food_item_id)
            )
            nutrition = result.scalars().first()
            
            if not nutrition:
                logger.warning(f"Nutrition data not found for food_item_id: {food_item_id}")
                return None
            
            # Get food item details
            result = await db.execute(
                select(models.FoodItem)
                .filter(models.FoodItem.id == food_item_id)
            )
            food_item = result.scalars().first()
            
            return {
                "food_name": food_item.canonical_name if food_item else "Unknown",
                "category": food_item.category if food_item else None,
                "data_source": nutrition.data_source,
                "macronutrients": {
                    "calories_per_100g": nutrition.calories_per_100g,
                    "protein_per_100g": nutrition.protein_per_100g,
                    "carbs_per_100g": nutrition.carbs_per_100g,
                    "fat_per_100g": nutrition.fat_per_100g,
                    "fiber_per_100g": nutrition.fiber_per_100g,
                    "sugar_per_100g": nutrition.sugar_per_100g,
                },
                "vitamins": {
                    "vitamin_a_mcg": nutrition.vitamin_a_mcg,
                    "vitamin_c_mg": nutrition.vitamin_c_mg,
                    "vitamin_d_mcg": nutrition.vitamin_d_mcg,
                    "vitamin_e_mg": nutrition.vitamin_e_mg,
                    "vitamin_k_mcg": nutrition.vitamin_k_mcg,
                    "vitamin_b1_thiamine_mg": nutrition.vitamin_b1_mg,
                    "vitamin_b2_riboflavin_mg": nutrition.vitamin_b2_mg,
                    "vitamin_b3_niacin_mg": nutrition.vitamin_b3_mg,
                    "vitamin_b6_mg": nutrition.vitamin_b6_mg,
                    "vitamin_b12_mcg": nutrition.vitamin_b12_mcg,
                    "folate_mcg": nutrition.folate_mcg,
                },
                "minerals": {
                    "calcium_mg": nutrition.calcium_mg,
                    "iron_mg": nutrition.iron_mg,
                    "magnesium_mg": nutrition.magnesium_mg,
                    "phosphorus_mg": nutrition.phosphorus_mg,
                    "potassium_mg": nutrition.potassium_mg,
                    "sodium_mg": nutrition.sodium_mg,
                    "zinc_mg": nutrition.zinc_mg,
                },
                "properties": {
                    "water_content_percent": nutrition.water_content_percent,
                    "spoilage_risk_level": nutrition.spoilage_risk_level,
                    "recommended_storage": nutrition.recommended_storage,
                    "shelf_life_days": nutrition.shelf_life_days,
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching nutrition data for food_item_id {food_item_id}: {str(e)}")
            return None
    
    async def search_foods(self, db: AsyncSession, query: str, limit: int = 10) -> list:
        """
        Search for food items by name
        """
        try:
            result = await db.execute(
                select(models.FoodItem)
                .filter(models.FoodItem.canonical_name.ilike(f"%{query}%"))
                .limit(limit)
            )
            food_items = result.scalars().all()
            
            return [
                {
                    "id": item.id,
                    "name": item.canonical_name,
                    "category": item.category,
                    "has_nutrition_data": item.nutrition is not None
                }
                for item in food_items
            ]
            
        except Exception as e:
            logger.error(f"Error searching foods: {str(e)}")
            return []

nutrition_service = NutritionService()

