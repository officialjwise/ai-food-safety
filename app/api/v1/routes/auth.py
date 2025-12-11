from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1 import dependencies
from app.core import security
from app.core.exceptions import OTPError, AuthenticationError
from app.db import models
from app.db.database import get_db
from app.schemas import token as token_schemas
from app.schemas import user as user_schemas
from app.schemas import otp as otp_schemas
from app.services.email_service import email_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=token_schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get access and refresh tokens
    """
    result = await db.execute(select(models.User).filter(models.User.email == form_data.username))
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create tokens
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)
    
    # Store refresh token in database
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = models.RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_token_expires
    )
    db.add(db_refresh_token)
    await db.commit()
    
    logger.info(f"User {user.email} logged in successfully")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/signup", response_model=user_schemas.User)
async def create_user_signup(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: user_schemas.UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in
    """
    result = await db.execute(select(models.User).filter(models.User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    user = models.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"New user registered: {user.email}")
    return user

@router.post("/admin/request-otp")
async def request_admin_otp(
    *,
    db: AsyncSession = Depends(get_db),
    otp_request: otp_schemas.OTPRequest,
) -> Any:
    """
    Request OTP for admin login via email
    """
    # Check if user exists and is admin
    result = await db.execute(select(models.User).filter(models.User.email == otp_request.email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="OTP login is only available for admin users")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Generate OTP
    otp_code = security.generate_otp()
    hashed_otp = security.hash_otp(otp_code)
    
    # Store OTP in database
    otp_expires = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    db_otp = models.OTPCode(
        email=otp_request.email,
        code=hashed_otp,
        expires_at=otp_expires
    )
    db.add(db_otp)
    await db.commit()
    
    # Send OTP email
    email_sent = await email_service.send_otp_email(otp_request.email, otp_code)
    
    if not email_sent:
        logger.error(f"Failed to send OTP email to {otp_request.email}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email. Please check email configuration."
        )
    
    logger.info(f"OTP sent to admin user: {otp_request.email}")
    
    return {
        "success": True,
        "message": f"OTP sent to {otp_request.email}",
        "email": otp_request.email
    }

@router.post("/admin/verify-otp", response_model=token_schemas.Token)
async def verify_admin_otp(
    *,
    db: AsyncSession = Depends(get_db),
    otp_verify: otp_schemas.OTPVerify,
) -> Any:
    """
    Verify OTP and issue access and refresh tokens
    """
    # Get user
    result = await db.execute(select(models.User).filter(models.User.email == otp_verify.email))
    user = result.scalars().first()
    
    if not user:
        raise OTPError("Invalid OTP")
    
    # Get latest unused OTP for this email
    result = await db.execute(
        select(models.OTPCode)
        .filter(models.OTPCode.email == otp_verify.email)
        .filter(models.OTPCode.is_used == False)
        .filter(models.OTPCode.expires_at > datetime.utcnow())
        .order_by(models.OTPCode.created_at.desc())
    )
    otp_record = result.scalars().first()
    
    if not otp_record:
        raise OTPError("OTP expired or invalid")
    
    # Verify OTP
    if not security.verify_otp(otp_verify.code, otp_record.code):
        raise OTPError("Invalid OTP")
    
    # Mark OTP as used
    otp_record.is_used = True
    db.add(otp_record)
    
    # Create tokens
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)
    
    # Store refresh token
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = models.RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_token_expires
    )
    db.add(db_refresh_token)
    await db.commit()
    
    logger.info(f"Admin user {user.email} logged in via OTP")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=token_schemas.Token)
async def refresh_access_token(
    *,
    db: AsyncSession = Depends(get_db),
    refresh_token: str,
) -> Any:
    """
    Refresh access token using refresh token
    """
    try:
        # Decode refresh token
        payload = security.decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token")
        
        # Check if token is blacklisted
        if await security.is_token_blacklisted(refresh_token):
            raise AuthenticationError("Token has been revoked")
        
        # Check if refresh token exists in database and is valid
        result = await db.execute(
            select(models.RefreshToken)
            .filter(models.RefreshToken.token == refresh_token)
            .filter(models.RefreshToken.is_revoked == False)
            .filter(models.RefreshToken.expires_at > datetime.utcnow())
        )
        db_token = result.scalars().first()
        
        if not db_token:
            raise AuthenticationError("Invalid or expired refresh token")
        
        # Get user
        result = await db.execute(select(models.User).filter(models.User.id == int(user_id)))
        user = result.scalars().first()
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Create new tokens
        new_access_token = security.create_access_token(user.id)
        new_refresh_token = security.create_refresh_token(user.id)
        
        # Revoke old refresh token
        db_token.is_revoked = True
        db.add(db_token)
        
        # Store new refresh token
        refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_db_refresh_token = models.RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=refresh_token_expires
        )
        db.add(new_db_refresh_token)
        await db.commit()
        
        logger.info(f"Access token refreshed for user {user.email}")
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise AuthenticationError("Failed to refresh token")

@router.post("/logout")
async def logout(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    refresh_token: str,
) -> Any:
    """
    Logout user by revoking refresh token
    """
    # Revoke refresh token in database
    result = await db.execute(
        select(models.RefreshToken)
        .filter(models.RefreshToken.token == refresh_token)
        .filter(models.RefreshToken.user_id == current_user.id)
    )
    db_token = result.scalars().first()
    
    if db_token:
        db_token.is_revoked = True
        db.add(db_token)
        await db.commit()
    
    # Blacklist refresh token in Redis
    await security.blacklist_token(refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    
    logger.info(f"User {current_user.email} logged out")
    
    return {
        "success": True,
        "message": "Logged out successfully"
    }

