from typing import Optional
from pydantic import BaseModel, EmailStr

class OTPRequest(BaseModel):
    """Request OTP for admin login"""
    email: EmailStr

class OTPVerify(BaseModel):
    """Verify OTP code"""
    email: EmailStr
    code: str

class OTPResponse(BaseModel):
    """OTP request response"""
    success: bool
    message: str
    email: Optional[str] = None
