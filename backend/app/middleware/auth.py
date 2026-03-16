"""
Authentication Middleware
=========================
JWT authentication middleware and dependencies
"""

from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import get_username_from_token
from app.core.config import logger

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Middleware for authentication"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Middleware implementation if needed
        await self.app(scope, receive, send)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Get current authenticated user from token
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Username from token
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    username = get_username_from_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Authenticated user: {username}")
    return username


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency to require authentication
    Same as get_current_user but with explicit naming
    """
    return await get_current_user(credentials)


async def optional_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]:
    """
    Optional authentication - returns username if valid, None otherwise
    Does not raise exception for invalid/missing token
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return get_username_from_token(token)
