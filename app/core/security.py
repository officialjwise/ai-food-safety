from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
import random
import string
import redis.asyncio as redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis connection for token blacklisting
redis_client = None

async def get_redis():
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create a refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def generate_otp(length: int = None) -> str:
    """Generate a random OTP code"""
    if length is None:
        length = settings.OTP_LENGTH
    return ''.join(random.choices(string.digits, k=length))

def hash_otp(otp: str) -> str:
    """Hash an OTP code"""
    return pwd_context.hash(otp)

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verify an OTP code"""
    return pwd_context.verify(plain_otp, hashed_otp)

async def blacklist_token(token: str, expire_seconds: int = None):
    """Add token to blacklist in Redis"""
    if expire_seconds is None:
        expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    redis_conn = await get_redis()
    await redis_conn.setex(f"blacklist:{token}", expire_seconds, "1")

async def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    redis_conn = await get_redis()
    result = await redis_conn.get(f"blacklist:{token}")
    return result is not None

