from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class VendorPriceBase(BaseModel):
    food_item_id: int
    price: float
    currency: str = "USD"

class VendorPriceCreate(VendorPriceBase):
    pass

class VendorPriceUpdate(BaseModel):
    price: Optional[float] = None
    currency: Optional[str] = None

class VendorPriceInDBBase(VendorPriceBase):
    id: int
    vendor_id: int
    date_posted: datetime

    class Config:
        from_attributes = True

class VendorPrice(VendorPriceInDBBase):
    pass
