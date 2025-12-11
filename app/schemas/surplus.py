from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.db.models import SurplusStatus

class SurplusListingBase(BaseModel):
    food_item_id: int
    quantity: float
    expiry_date: datetime

class SurplusListingCreate(SurplusListingBase):
    pass

class SurplusListingUpdate(BaseModel):
    quantity: Optional[float] = None
    expiry_date: Optional[datetime] = None
    status: Optional[SurplusStatus] = None

class SurplusListingInDBBase(SurplusListingBase):
    id: int
    vendor_id: int
    status: SurplusStatus
    created_at: datetime
    claimed_by_ngo_id: Optional[int] = None

    class Config:
        from_attributes = True

class SurplusListing(SurplusListingInDBBase):
    pass
