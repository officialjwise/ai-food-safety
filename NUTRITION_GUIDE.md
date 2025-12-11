# Nutrition Database Integration Guide

## Overview

The nutrition lookup system maps food items to comprehensive FAO/USDA nutrient data. This enables the platform to provide scientific, authoritative nutritional information alongside food safety predictions.

## How It Works

### 1. **Data Flow**

```
User scans food → ML identifies food type → System queries nutrition_data table → Returns comprehensive nutrient profile
```

### 2. **Database Structure**

#### `food_items` Table
- Canonical food names (e.g., "Tomato", "Spinach", "Tilapia")
- Categories (Vegetables, Fruits, Fish, etc.)
- Links to nutrition data

#### `nutrition_data` Table
- **Source Information**: FAO, USDA, WHO, or Manual
- **Macronutrients**: Calories, protein, carbs, fats, fiber, sugar
- **Vitamins**: A, B-complex, C, D, E, K, folate
- **Minerals**: Calcium, iron, magnesium, phosphorus, potassium, sodium, zinc
- **Properties**: Water content, spoilage risk, storage recommendations, shelf life

### 3. **Data Sources**

The system supports multiple authoritative sources:

1. **USDA FoodData Central** (https://fdc.nal.usda.gov/)
   - Most comprehensive US database
   - ~350,000+ foods
   - Download formats: JSON, CSV

2. **FAO/INFOODS** (https://www.fao.org/infoods/infoods/en/)
   - International food composition data
   - Regional African food data
   - Good for local foods

3. **WHO Nutrient Requirements**
   - Reference values for nutrients
   - Dietary guidelines

## Implementation Locations

### 1. **Nutrition Service** 
`app/services/nutrition_service.py`

The nutrition lookup happens here:

```python
async def get_nutrition_by_food_id(db: AsyncSession, food_item_id: int) -> dict:
    # Fetches nutrition data from database
    # Returns structured nutrient information
```

### 2. **Food Items Routes**
`app/api/v1/routes/food_items.py`

Endpoints for managing food items and nutrition:

- `GET /api/v1/food-items` - List all food items
- `GET /api/v1/food-items/search?q=tomato` - Search foods
- `GET /api/v1/food-items/{id}/nutrition` - Get nutrition data
- `POST /api/v1/food-items/{id}/nutrition` - Add nutrition data (Admin)
- `PUT /api/v1/food-items/{id}/nutrition` - Update nutrition data (Admin)

### 3. **Inference Integration**
`app/api/v1/routes/inference.py`

When a user scans food:

```python
# ML predicts food type
prediction = await ml_service.predict(image_path)

# Find matching food item
food_item = await db.execute(
    select(models.FoodItem)
    .filter(models.FoodItem.canonical_name.ilike(f"%{prediction['label']}%"))
).scalars().first()

# Get nutrition data
if food_item:
    nutrition = await nutrition_service.get_nutrition_by_food_id(db, food_item.id)
```

### 4. **Data Seeding**
`app/db/seed_nutrition.py`

Utility to populate database with sample FAO/USDA data:

```bash
python -m app.db.seed_nutrition
```

## How to Add FAO/USDA Data

### Option 1: Manual Entry (Small Scale)

1. **Use the Admin API**:
```bash
# Create food item
POST /api/v1/food-items
{
  "canonical_name": "Watermelon",
  "category": "Fruits"
}

# Add nutrition data
POST /api/v1/food-items/{id}/nutrition
{
  "data_source": "USDA",
  "source_id": "09326",
  "calories_per_100g": 30,
  "protein_per_100g": 0.6,
  ...
}
```

### Option 2: Bulk Import from USDA (Recommended)

1. **Download USDA FoodData Central**:
   - Visit: https://fdc.nal.usda.gov/download-datasets.html
   - Download "Foundation Foods" or "SR Legacy"
   - Format: CSV or JSON

2. **Create Import Script**:

```python
# app/db/import_usda.py
import csv
import asyncio
from app.db.database import AsyncSessionLocal
from app.db import models

async def import_usda_csv(filepath):
    async with AsyncSessionLocal() as db:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create food item
                food_item = models.FoodItem(
                    canonical_name=row['description'],
                    category=row['food_category']
                )
                db.add(food_item)
                await db.flush()
                
                # Create nutrition data
                nutrition = models.NutritionData(
                    food_item_id=food_item.id,
                    data_source="USDA",
                    source_id=row['fdc_id'],
                    calories_per_100g=float(row['energy_kcal']),
                    protein_per_100g=float(row['protein']),
                    # ... map other fields
                )
                db.add(nutrition)
        
        await db.commit()

# Run: python -m app.db.import_usda
```

### Option 3: External API Integration

Connect to USDA API in real-time:

```python
# app/services/usda_api_service.py
import httpx

class USDAService:
    API_KEY = "your-api-key"
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    
    async def search_food(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/foods/search",
                params={"api_key": self.API_KEY, "query": query}
            )
            return response.json()
```

## Data Mapping Strategy

### FAO/USDA Field Mapping

| Our Field | USDA Field | FAO Field |
|-----------|------------|-----------|
| `calories_per_100g` | Energy (kcal) | ENERC |
| `protein_per_100g` | Protein | PROT |
| `carbs_per_100g` | Carbohydrate | CHO |
| `fat_per_100g` | Total lipid (fat) | FAT |
| `fiber_per_100g` | Fiber, total dietary | FIBT |
| `vitamin_a_mcg` | Vitamin A, RAE | VITA |
| `vitamin_c_mg` | Vitamin C | VITC |
| `calcium_mg` | Calcium, Ca | CA |
| `iron_mg` | Iron, Fe | FE |

### Food Category Standardization

Map vendor inputs to standard categories:

```python
CATEGORY_MAPPINGS = {
    "tomatoes": "Vegetables",
    "fresh fish": "Fish",
    "chicken": "Poultry",
    "plantain": "Starchy Vegetables",
    # ...
}
```

## Example: Complete Workflow

### 1. Seed Sample Data
```bash
python -m app.db.seed_nutrition
```

### 2. Test Nutrition Lookup
```bash
GET /api/v1/food-items/search?q=tomato

Response:
{
  "success": true,
  "data": [{
    "id": 1,
    "name": "Tomato",
    "category": "Vegetables",
    "has_nutrition_data": true
  }]
}
```

### 3. Get Full Nutrition Data
```bash
GET /api/v1/food-items/1/nutrition

Response:
{
  "success": true,
  "data": {
    "food_name": "Tomato",
    "data_source": "USDA",
    "macronutrients": {
      "calories_per_100g": 18.0,
      "protein_per_100g": 0.9,
      ...
    },
    "vitamins": {...},
    "minerals": {...},
    "properties": {
      "spoilage_risk_level": "medium",
      "shelf_life_days": 7
    }
  }
}
```

### 4. Scanner Integration
```bash
POST /api/v1/inference
(upload image of tomato)

Response includes:
- ML prediction (Fresh/Stale/Spoiled)
- Contamination score
- Complete nutrition data from database
- Storage recommendations
- Spoilage risk assessment
```

## Grant Proposal Integration

For your grant applications, emphasize:

1. **Scientific Validity**: "Nutrition data sourced from FAO and USDA FoodData Central, ensuring scientific accuracy"

2. **Comprehensive Coverage**: "Platform provides 30+ nutrient data points per food item, including vitamins, minerals, and preservation metadata"

3. **Local Food Support**: "Database includes regional African foods (cassava, plantain, garden egg) mapped to FAO nutrient standards"

4. **Safety Integration**: "Combines AI contamination detection with nutrient density analysis and spoilage risk modeling"

## Next Steps

1. **Expand Database**: Add more local African foods
2. **API Integration**: Connect to USDA API for real-time lookups
3. **Vendor Contributions**: Allow verified vendors to suggest new foods
4. **Community Validation**: NGOs can verify nutrition data for local foods

---

**Need Help?**
- USDA API Docs: https://fdc.nal.usda.gov/api-guide.html
- FAO INFOODS: https://www.fao.org/infoods/infoods/tables-and-databases/en/
