from typing import Optional
from pydantic import BaseModel

class VendorProfileBase(BaseModel):
    shop_name: str
    location: Optional[str] = None

class VendorProfileCreate(VendorProfileBase):
    pass

class VendorProfileUpdate(VendorProfileBase):
    verified: Optional[bool] = None

class VendorProfileInDBBase(VendorProfileBase):
    id: int
    user_id: int
    verified: bool

    class Config:
        from_attributes = True

class VendorProfile(VendorProfileInDBBase):
    pass
