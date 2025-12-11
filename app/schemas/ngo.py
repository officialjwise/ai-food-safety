from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# NGO Profile Schemas

class NGOProfileBase(BaseModel):
    organization_name: str
    organization_type: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    operational_hours: Optional[str] = None
    focus_areas: Optional[str] = None  # JSON string
    partner_code: Optional[str] = None
    preferred_pickup_window: Optional[str] = None
    delivery_capacity: Optional[int]= None

class NGOProfileCreate(NGOProfileBase):
    pass

class NGOProfileUpdate(BaseModel):
    organization_name: Optional[str] = None
    organization_type: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    operational_hours: Optional[str] = None
    focus_areas: Optional[str] = None
    preferred_pickup_window: Optional[str] = None
    delivery_capacity: Optional[int] = None

class NGOProfile(NGOProfileBase):
    id: int
    user_id: int
    verification_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Surplus Claim Schemas

class SurplusClaimBase(BaseModel):
    notes: Optional[str] = None

class SurplusClaimCreate(SurplusClaimBase):
    surplus_id: int

class SurplusClaimUpdate(BaseModel):
    collection_photo_proof: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class SurplusClaim(SurplusClaimBase):
    id: int
    surplus_id: int
    ngo_id: int
    timestamp_claimed: datetime
    timestamp_collected: Optional[datetime] = None
    collection_photo_proof: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Saved Item Schemas

class SavedItemCreate(BaseModel):
    item_id: int

class SavedItem(BaseModel):
    id: int
    user_id: int
    item_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Price Lookup History Schema

class PriceLookupHistory(BaseModel):
    id: int
    user_id: int
    item_id: Optional[int] = None
    search_query: Optional[str] = None
    location_used: Optional[str] = None
    found_price_range: Optional[str] = None  # JSON string
    timestamp: datetime

    class Config:
        from_attributes = True
