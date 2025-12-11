"""
USDA FoodData Central JSON Importer

Imports nutrition data from USDA FoodData Central foundation foods JSON file.
The file should be downloaded from: https://fdc.nal.usda.gov/download-datasets.html

Usage:
    python -m app.db.import_usda <path_to_json_file>
    
Example:
    python -m app.db.import_usda FoodData_Central_foundation_food_json_2025-04-24.json
"""

import json
import asyncio
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db import models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Nutrient mapping from USDA to our database fields
NUTRIENT_MAPPINGS = {
    # Macronutrients
    "1008": "calories_per_100g",      # Energy (kcal)
    "1003": "protein_per_100g",       # Protein
    "1005": "carbs_per_100g",         # Carbohydrate, by difference
    "1004": "fat_per_100g",           # Total lipid (fat)
    "1079": "fiber_per_100g",         # Fiber, total dietary
    "2000": "sugar_per_100g",         # Sugars, total
    
    # Vitamins (convert to appropriate units)
    "1106": "vitamin_a_mcg",          # Vitamin A, RAE (mcg)
    "1162": "vitamin_c_mg",           # Vitamin C (mg)
    "1114": "vitamin_d_mcg",          # Vitamin D (mcg)
    "1109": "vitamin_e_mg",           # Vitamin E (mg)
    "1185": "vitamin_k_mcg",          # Vitamin K (mcg)
    "1165": "vitamin_b1_mg",          # Thiamin (mg)
    "1166": "vitamin_b2_mg",          # Riboflavin (mg)
    "1167": "vitamin_b3_mg",          # Niacin (mg)
    "1175": "vitamin_b6_mg",          # Vitamin B-6 (mg)
    "1178": "vitamin_b12_mcg",        # Vitamin B-12 (mcg)
    "1177": "folate_mcg",             # Folate, total (mcg)
    
    # Minerals
    "1087": "calcium_mg",             # Calcium, Ca (mg)
    "1089": "iron_mg",                # Iron, Fe (mg)
    "1090": "magnesium_mg",           # Magnesium, Mg (mg)
    "1091": "phosphorus_mg",          # Phosphorus, P (mg)
    "1092": "potassium_mg",           # Potassium, K (mg)
    "1093": "sodium_mg",              # Sodium, Na (mg)
    "1095": "zinc_mg",                # Zinc, Zn (mg)
    
    # Water content
    "1051": "water_content_percent",  # Water (g) - will convert to percent
}

# Food category mappings
CATEGORY_MAPPINGS = {
    "vegetables": "Vegetables",
    "fruits": "Fruits",
    "dairy": "Dairy",
    "meat": "Meat & Poultry",
    "fish": "Fish & Seafood",
    "grains": "Grains",
    "legumes": "Legumes",
    "nuts": "Nuts & Seeds",
}

def categorize_food(description: str, category: str = None) -> str:
    """Determine food category from description or USDA category"""
    description_lower = description.lower()
    
    if category:
        category_lower = category.lower()
        for key, value in CATEGORY_MAPPINGS.items():
            if key in category_lower:
                return value
    
    # Simple keyword matching
    if any(word in description_lower for word in ["vegetable", "lettuce", "tomato", "carrot", "spinach"]):
        return "Vegetables"
    elif any(word in description_lower for word in ["fruit", "apple", "banana", "orange", "berry"]):
        return "Fruits"
    elif any(word in description_lower for word in ["fish", "salmon", "tuna", "tilapia"]):
        return "Fish & Seafood"
    elif any(word in description_lower for word in ["chicken", "beef", "pork", "meat"]):
        return "Meat & Poultry"
    elif any(word in description_lower for word in ["rice", "wheat", "oat", "grain"]):
        return "Grains"
    elif any(word in description_lower for word in ["bean", "lentil", "pea"]):
        return "Legumes"
    
    return "Other"

def estimate_spoilage_risk(category: str, water_content: float = None) -> tuple:
    """Estimate spoilage risk and storage recommendations"""
    high_risk_categories = ["Fish & Seafood", "Meat & Poultry", "Dairy"]
    medium_risk_categories = ["Vegetables", "Fruits"]
    
    if category in high_risk_categories:
        return "high", "refrigerate", 2
    elif category in medium_risk_categories:
        if water_content and water_content > 85:
            return "high", "refrigerate", 5
        return "medium", "refrigerate", 7
    else:
        return "low", "room_temp", 30

async def import_usda_json(filepath: str, limit: int = None):
    """Import USDA FoodData Central JSON file"""
    
    file_path = Path(filepath)
    if not file_path.exists():
        logger.error(f"File not found: {filepath}")
        return
    
    logger.info(f"Loading JSON file: {filepath}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON: {str(e)}")
        return
    
    # Get foundation foods
    if 'FoundationFoods' in data:
        foods = data['FoundationFoods']
    elif isinstance(data, list):
        foods = data
    else:
        logger.error("Unexpected JSON structure")
        return
    
    if limit:
        foods = foods[:limit]
    
    logger.info(f"Found {len(foods)} foods to import")
    
    async with AsyncSessionLocal() as db:
        imported_count = 0
        skipped_count = 0
        
        for idx, food in enumerate(foods, 1):
            try:
                description = food.get('description', 'Unknown')
                fdc_id = food.get('fdcId')
                
                logger.info(f"[{idx}/{len(foods)}] Processing: {description}")
                
                # Check if food already exists
                result = await db.execute(
                    select(models.FoodItem)
                    .filter(models.FoodItem.canonical_name == description)
                )
                existing_food = result.scalars().first()
                
                if existing_food:
                    logger.info(f"  ↳ Already exists, skipping...")
                    skipped_count += 1
                    continue
                
                # Extract category
                category_desc = food.get('foodCategory', {}).get('description', '')
                category = categorize_food(description, category_desc)
                
                # Create food item
                food_item = models.FoodItem(
                    canonical_name=description,
                    category=category
                )
                db.add(food_item)
                await db.flush()
                
                # Extract nutrients
                nutrients_data = {}
                food_nutrients = food.get('foodNutrients', [])
                
                for nutrient in food_nutrients:
                    nutrient_id = str(nutrient.get('nutrient', {}).get('number', ''))
                    amount = nutrient.get('amount')
                    
                    if nutrient_id in NUTRIENT_MAPPINGS and amount is not None:
                        field_name = NUTRIENT_MAPPINGS[nutrient_id]
                        nutrients_data[field_name] = float(amount)
                
                # Estimate spoilage properties
                water_content = nutrients_data.get('water_content_percent', 0)
                risk, storage, shelf_life = estimate_spoilage_risk(category, water_content)
                
                # Create nutrition data
                nutrition_data = models.NutritionData(
                    food_item_id=food_item.id,
                    data_source="USDA",
                    source_id=str(fdc_id),
                    **nutrients_data,
                    spoilage_risk_level=risk,
                    recommended_storage=storage,
                    shelf_life_days=shelf_life
                )
                db.add(nutrition_data)
                
                imported_count += 1
                logger.info(f"  ✓ Imported with {len(nutrients_data)} nutrients")
                
                # Commit every 50 items to avoid memory issues
                if imported_count % 50 == 0:
                    await db.commit()
                    logger.info(f"  → Committed batch ({imported_count} total)")
                
            except Exception as e:
                logger.error(f"  ✗ Error importing {description}: {str(e)}")
                continue
        
        # Final commit
        await db.commit()
        
        logger.info(f"\n=== Import Complete ===")
        logger.info(f"Imported: {imported_count}")
        logger.info(f"Skipped: {skipped_count}")
        logger.info(f"Total: {len(foods)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.db.import_usda <path_to_json_file> [limit]")
        print("\nExample:")
        print("  python -m app.db.import_usda FoodData_Central_foundation_food_json_2025-04-24.json")
        print("  python -m app.db.import_usda FoodData_Central_foundation_food_json_2025-04-24.json 100")
        sys.exit(1)
    
    filepath = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if limit:
        print(f"Importing first {limit} foods from: {filepath}")
    else:
        print(f"Importing all foods from: {filepath}")
    
    asyncio.run(import_usda_json(filepath, limit))
