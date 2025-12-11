"""
Utility script to seed nutrition data from FAO/USDA sources

This script helps populate the database with nutrition data from authoritative sources:
- FAO (Food and Agriculture Organization)
- USDA FoodData Central
- Manual entry for local foods

Usage:
    python -m app.db.seed_nutrition
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal, engine
from app.db import models
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

# Sample nutrition data based on FAO/USDA standards
# This is a starter dataset - you should expand this with actual FAO/USDA data
NUTRITION_DATABASE = {
    # Vegetables
    "Tomato": {
        "category": "Vegetables",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "11529",
            "calories_per_100g": 18.0,
            "protein_per_100g": 0.9,
            "carbs_per_100g": 3.9,
            "fat_per_100g": 0.2,
            "fiber_per_100g": 1.2,
            "sugar_per_100g": 2.6,
            "vitamin_a_mcg": 42.0,
            "vitamin_c_mg": 13.7,
            "vitamin_k_mcg": 7.9,
            "potassium_mg": 237.0,
            "water_content_percent": 94.5,
            "spoilage_risk_level": "medium",
            "recommended_storage": "room_temp",
            "shelf_life_days": 7
        }
    },
    "Spinach": {
        "category": "Vegetables",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "11457",
            "calories_per_100g": 23.0,
            "protein_per_100g": 2.9,
            "carbs_per_100g": 3.6,
            "fat_per_100g": 0.4,
            "fiber_per_100g": 2.2,
            "vitamin_a_mcg": 469.0,
            "vitamin_c_mg": 28.1,
            "vitamin_k_mcg": 482.9,
            "iron_mg": 2.71,
            "calcium_mg": 99.0,
            "potassium_mg": 558.0,
            "water_content_percent": 91.4,
            "spoilage_risk_level": "high",
            "recommended_storage": "refrigerate",
            "shelf_life_days": 5
        }
    },
    
    # Fruits
    "Banana": {
        "category": "Fruits",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "09040",
            "calories_per_100g": 89.0,
            "protein_per_100g": 1.1,
            "carbs_per_100g": 22.8,
            "fat_per_100g": 0.3,
            "fiber_per_100g": 2.6,
            "sugar_per_100g": 12.2,
            "vitamin_c_mg": 8.7,
            "vitamin_b6_mg": 0.4,
            "potassium_mg": 358.0,
            "magnesium_mg": 27.0,
            "water_content_percent": 74.9,
            "spoilage_risk_level": "medium",
            "recommended_storage": "room_temp",
            "shelf_life_days": 5
        }
    },
    "Apple": {
        "category": "Fruits",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "09003",
            "calories_per_100g": 52.0,
            "protein_per_100g": 0.3,
            "carbs_per_100g": 13.8,
            "fat_per_100g": 0.2,
            "fiber_per_100g": 2.4,
            "sugar_per_100g": 10.4,
            "vitamin_c_mg": 4.6,
            "potassium_mg": 107.0,
            "water_content_percent": 85.6,
            "spoilage_risk_level": "low",
            "recommended_storage": "refrigerate",
            "shelf_life_days": 30
        }
    },
    
    # Proteins
    "Tilapia": {
        "category": "Fish",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "15261",
            "calories_per_100g": 96.0,
            "protein_per_100g": 20.1,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 1.7,
            "fiber_per_100g": 0.0,
            "vitamin_b12_mcg": 1.6,
            "phosphorus_mg": 170.0,
            "potassium_mg": 302.0,
            "sodium_mg": 52.0,
            "water_content_percent": 78.1,
            "spoilage_risk_level": "high",
            "recommended_storage": "refrigerate",
            "shelf_life_days": 2
        }
    },
    "Chicken Breast": {
        "category": "Poultry",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "05062",
            "calories_per_100g": 165.0,
            "protein_per_100g": 31.0,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 3.6,
            "vitamin_b6_mg": 0.6,
            "vitamin_b12_mcg": 0.3,
            "phosphorus_mg": 228.0,
            "potassium_mg": 256.0,
            "water_content_percent": 65.0,
            "spoilage_risk_level": "high",
            "recommended_storage": "refrigerate",
            "shelf_life_days": 2
        }
    },
    
    # Grains & Staples
    "Rice (White)": {
        "category": "Grains",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "20044",
            "calories_per_100g": 130.0,
            "protein_per_100g": 2.7,
            "carbs_per_100g": 28.2,
            "fat_per_100g": 0.3,
            "fiber_per_100g": 0.4,
            "iron_mg": 0.2,
            "potassium_mg": 35.0,
            "water_content_percent": 68.4,
            "spoilage_risk_level": "low",
            "recommended_storage": "room_temp",
            "shelf_life_days": 365
        }
    },
    "Plantain": {
        "category": "Starchy Vegetables",
        "nutrition": {
            "data_source": "USDA",
            "source_id": "09277",
            "calories_per_100g": 122.0,
            "protein_per_100g": 1.3,
            "carbs_per_100g": 31.9,
            "fat_per_100g": 0.4,
            "fiber_per_100g": 2.3,
            "vitamin_a_mcg": 56.0,
            "vitamin_c_mg": 18.4,
            "vitamin_b6_mg": 0.3,
            "potassium_mg": 499.0,
            "magnesium_mg": 37.0,
            "water_content_percent": 65.3,
            "spoilage_risk_level": "medium",
            "recommended_storage": "room_temp",
            "shelf_life_days": 7
        }
    },
    
    # Local African Foods (Manual entry based on FAO data)
    "Cassava": {
        "category": "Root Vegetables",
        "nutrition": {
            "data_source": "FAO",
            "source_id": "FAO-1550",
            "calories_per_100g": 160.0,
            "protein_per_100g": 1.4,
            "carbs_per_100g": 38.1,
            "fat_per_100g": 0.3,
            "fiber_per_100g": 1.8,
            "vitamin_c_mg": 20.6,
            "calcium_mg": 16.0,
            "phosphorus_mg": 27.0,
            "potassium_mg": 271.0,
            "water_content_percent": 59.7,
            "spoilage_risk_level": "medium",
            "recommended_storage": "room_temp",
            "shelf_life_days": 3
        }
    },
    "Garden Egg": {
        "category": "Vegetables",
        "nutrition": {
            "data_source": "FAO",
            "source_id": "FAO-2103",
            "calories_per_100g": 24.0,
            "protein_per_100g": 1.0,
            "carbs_per_100g": 5.7,
            "fat_per_100g": 0.2,
            "fiber_per_100g": 2.5,
            "vitamin_c_mg": 2.2,
            "calcium_mg": 9.0,
            "iron_mg": 0.24,
            "potassium_mg": 230.0,
            "water_content_percent": 92.0,
            "spoilage_risk_level": "medium",
            "recommended_storage": "refrigerate",
            "shelf_life_days": 7
        }
    }
}

async def seed_nutrition_data():
    """Seed the database with FAO/USDA nutrition data"""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting nutrition data seeding...")
            
            for food_name, data in NUTRITION_DATABASE.items():
                # Check if food item exists
                result = await db.execute(
                    select(models.FoodItem)
                    .filter(models.FoodItem.canonical_name == food_name)
                )
                food_item = result.scalars().first()
                
                # Create food item if it doesn't exist
                if not food_item:
                    food_item = models.FoodItem(
                        canonical_name=food_name,
                        category=data["category"]
                    )
                    db.add(food_item)
                    await db.flush()  # Get the ID without committing
                    logger.info(f"Created food item: {food_name}")
                
                # Check if nutrition data exists
                result = await db.execute(
                    select(models.NutritionData)
                    .filter(models.NutritionData.food_item_id == food_item.id)
                )
                existing_nutrition = result.scalars().first()
                
                if existing_nutrition:
                    logger.info(f"Nutrition data already exists for {food_name}, skipping...")
                    continue
                
                # Create nutrition data
                nutrition_data = models.NutritionData(
                    food_item_id=food_item.id,
                    **data["nutrition"]
                )
                db.add(nutrition_data)
                logger.info(f"Added nutrition data for: {food_name}")
            
            await db.commit()
            logger.info("Successfully seeded nutrition data!")
            
        except Exception as e:
            logger.error(f"Error seeding nutrition data: {str(e)}")
            await db.rollback()
            raise

async def clear_nutrition_data():
    """Clear all nutrition data (use with caution!)"""
    async with AsyncSessionLocal() as db:
        try:
            # Delete all nutrition data
            await db.execute("DELETE FROM nutrition_data")
            # Delete all food items
            await db.execute("DELETE FROM food_items")
            await db.commit()
            logger.info("Cleared all nutrition data")
        except Exception as e:
            logger.error(f"Error clearing nutrition data: {str(e)}")
            await db.rollback()
            raise

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    print("=== Nutrition Data Seeder ===")
    print("1. Seed sample nutrition data")
    print("2. Clear all nutrition data (WARNING: Destructive!)")
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(seed_nutrition_data())
        print("\n✓ Nutrition data seeded successfully!")
        print("You can now test the endpoints at /api/v1/food-items")
    elif choice == "2":
        confirm = input("Are you sure? Type 'YES' to confirm: ")
        if confirm == "YES":
            asyncio.run(clear_nutrition_data())
            print("\n✓ Nutrition data cleared")
        else:
            print("Cancelled")
    else:
        print("Invalid choice")
