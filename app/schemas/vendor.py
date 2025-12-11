from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class VendorProfileBase(BaseModel):
    business_name: str  # Previously shop_name
    owner_full_name: Optional[str] = None
    business_type: Optional[str] = None  # market_stall, grocery, farmer, distributor
    business_registration_number: Optional[str] = None
    location_text: Optional[str] = None  # Previously location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    profile_photo: Optional[str] = None

class VendorProfileCreate(VendorProfileBase):
    pass

class VendorProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    owner_full_name: Optional[str] = None
    business_type: Optional[str] = None
    business_registration_number: Optional[str] = None
    location_text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    profile_photo: Optional[str] = None

class VendorProfile(VendorProfileBase):
    id: int
    user_id: int
    verified_status: str  # pending, approved, rejected
    rating_score: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
