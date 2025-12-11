from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class VendorPriceBase(BaseModel):
    food_item_id: int
    price_per_unit: float  # Previously 'price'
    quantity_unit: Optional[str] = None  # kg, bunch, piece, crate, bag
    currency: str = "GHS"  # Ghana Cedis
    freshness_status: Optional[str] = None  # fresh, semi-fresh, slightly_spoiled
    stock_availability: bool = True
    measurement_accuracy_flag: bool = True
    market_location: Optional[str] = None

class VendorPriceCreate(VendorPriceBase):
    pass

class VendorPriceUpdate(BaseModel):
    price_per_unit: Optional[float] = None
    quantity_unit: Optional[str] = None
    freshness_status: Optional[str] = None
    stock_availability: Optional[bool] = None
    market_location: Optional[str] = None

class VendorPrice(VendorPriceBase):
    id: int
    vendor_id: int
    date_posted: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
