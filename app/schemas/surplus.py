from datetime import datetime
from typing import Optional
from pydantic import BaseModel
# from app.db.models import SurplusStatus # This import is no longer needed as SurplusStatus is replaced by str

class SurplusListingBase(BaseModel):
    food_item_id: int
    surplus_title: str  # NEW - required
    quantity: float
    condition_status: Optional[str] = None  # edible, near_expiry
    notes: Optional[str] = None
    photos: Optional[str] = None  # JSON array of image URLs
    expiry_date: datetime
    pickup_deadline: Optional[datetime] = None
    pickup_location: Optional[str] = None

class SurplusListingCreate(SurplusListingBase):
    pass

class SurplusListingUpdate(BaseModel):
    surplus_title: Optional[str] = None
    quantity: Optional[float] = None
    condition_status: Optional[str] = None
    notes: Optional[str] = None
    photos: Optional[str] = None
    expiry_date: Optional[datetime] = None
    pickup_deadline: Optional[datetime] = None
    pickup_location: Optional[str] = None
    status: Optional[str] = None

class SurplusListing(SurplusListingBase):
    id: int
    vendor_id: int
    status: str  # available, claimed, collected, expired
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
