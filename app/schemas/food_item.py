from typing import Optional
from pydantic import BaseModel

class FoodItemBase(BaseModel):
    canonical_name: str
    category: Optional[str] = None
    example_image_url: Optional[str] = None

class FoodItemCreate(FoodItemBase):
    pass

class FoodItemUpdate(FoodItemBase):
    pass

class FoodItemInDBBase(FoodItemBase):
    id: int

    class Config:
        from_attributes = True

class FoodItem(FoodItemInDBBase):
    pass
