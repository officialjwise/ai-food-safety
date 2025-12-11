from typing import Optional
from pydantic import BaseModel

class NutritionMacronutrients(BaseModel):
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    fiber_per_100g: Optional[float] = None
    sugar_per_100g: Optional[float] = None

class NutritionVitamins(BaseModel):
    vitamin_a_mcg: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    vitamin_d_mcg: Optional[float] = None
    vitamin_e_mg: Optional[float] = None
    vitamin_k_mcg: Optional[float] = None
    vitamin_b1_thiamine_mg: Optional[float] = None
    vitamin_b2_riboflavin_mg: Optional[float] = None
    vitamin_b3_niacin_mg: Optional[float] = None
    vitamin_b6_mg: Optional[float] = None
    vitamin_b12_mcg: Optional[float] = None
    folate_mcg: Optional[float] = None

class NutritionMinerals(BaseModel):
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    magnesium_mg: Optional[float] = None
    phosphorus_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    sodium_mg: Optional[float] = None
    zinc_mg: Optional[float] = None

class NutritionProperties(BaseModel):
    water_content_percent: Optional[float] = None
    spoilage_risk_level: Optional[str] = None
    recommended_storage: Optional[str] = None
    shelf_life_days: Optional[int] = None

class NutritionDataBase(BaseModel):
    food_item_id: int
    data_source: Optional[str] = "Manual"
    source_id: Optional[str] = None
    
    # Macronutrients
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    fiber_per_100g: Optional[float] = None
    sugar_per_100g: Optional[float] = None
    
    # Vitamins
    vitamin_a_mcg: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    vitamin_d_mcg: Optional[float] = None
    vitamin_e_mg: Optional[float] = None
    vitamin_k_mcg: Optional[float] = None
    vitamin_b1_mg: Optional[float] = None
    vitamin_b2_mg: Optional[float] = None
    vitamin_b3_mg: Optional[float] = None
    vitamin_b6_mg: Optional[float] = None
    vitamin_b12_mcg: Optional[float] = None
    folate_mcg: Optional[float] = None
    
    # Minerals
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    magnesium_mg: Optional[float] = None
    phosphorus_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    sodium_mg: Optional[float] = None
    zinc_mg: Optional[float] = None
    
    # Properties
    water_content_percent: Optional[float] = None
    spoilage_risk_level: Optional[str] = None
    recommended_storage: Optional[str] = None
    shelf_life_days: Optional[int] = None

class NutritionDataCreate(NutritionDataBase):
    pass

class NutritionDataUpdate(BaseModel):
    data_source: Optional[str] = None
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    fiber_per_100g: Optional[float] = None
    spoilage_risk_level: Optional[str] = None
    recommended_storage: Optional[str] = None
    shelf_life_days: Optional[int] = None

class NutritionDataResponse(BaseModel):
    food_name: str
    category: Optional[str] = None
    data_source: Optional[str] = None
    macronutrients: NutritionMacronutrients
    vitamins: NutritionVitamins
    minerals: NutritionMinerals
    properties: NutritionProperties

    class Config:
        from_attributes = True
