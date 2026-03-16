"""
Authentication Routes
=====================
Endpoints for user authentication
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.core.config import settings, logger
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token
)
from app.middleware.auth import get_current_user

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


# Pydantic models
class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    username: str = Field(..., description="Authenticated username")


class UserResponse(BaseModel):
    """User info response model"""
    username: str = Field(..., description="Username")
    authenticated: bool = Field(default=True, description="Authentication status")


# Simple user storage (in production, use a proper database)
# This is a basic implementation for demonstration
# In production, use a proper user management system
DEFAULT_USERS = {
    "admin": {
        "password_hash": get_password_hash("admin"),  # Change in production!
        "role": "admin"
    }
}


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user with username and password
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        True if authentication succeeds
    """
    user = DEFAULT_USERS.get(username)
    if not user:
        return False
    return verify_password(password, user["password_hash"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and return JWT token
    
    Args:
        credentials: Login credentials (username and password)
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Login attempt for user: {credentials.username}")
    
    if not authenticate_user(credentials.username, credentials.password):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": credentials.username, "role": DEFAULT_USERS[credentials.username]["role"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info(f"Successful login for user: {credentials.username}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        username=credentials.username
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint
    Note: JWT tokens cannot be truly invalidated server-side without a token blacklist.
    Client should discard the token.
    """
    return {"message": "Logout successful. Please discard your token."}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(username: str = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Returns:
        User information
    """
    return UserResponse(username=username, authenticated=True)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(username: str = Depends(get_current_user)):
    """
    Refresh access token
    
    Returns:
        New JWT access token
    """
    user = DEFAULT_USERS.get(username)
    role = user["role"] if user else "user"
    
    access_token = create_access_token(
        data={"sub": username, "role": role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info(f"Token refreshed for user: {username}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        username=username
    )


# Health check for auth system
@router.get("/health")
async def auth_health():
    """Check authentication system health"""
    return {
        "status": "healthy",
        "auth_enabled": True,
        "token_algorithm": settings.ALGORITHM,
        "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }
