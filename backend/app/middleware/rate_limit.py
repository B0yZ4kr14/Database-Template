"""
Rate Limiting Middleware
========================
Simple in-memory rate limiting for API endpoints

⚠️  IMPORTANTE - Limitação em Deploy Multi-Worker:
--------------------------------------------------
Este rate limiter usa armazenamento em memória (dicionário Python).
Em deploy com múltiplos workers (ex: 4 workers uvicorn), cada worker
mantém seu próprio contador de requests, permitindo Nx o limite
configurado (onde N = número de workers).

Recomendações:
1. Para deploy single-worker: usar limites como estão
2. Para deploy multi-worker: dividir limites pelo número de workers
   ou usar Redis para estado compartilhado
3. Para alta escala: implementar backend Redis para rate limiting

Exemplo multi-worker:
- Limite desejado: 60 req/min
- Workers: 4
- Limite por worker: 60 / 4 = 15 req/min
"""

import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    Tracks requests by client IP and endpoint
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Store: {client_ip: {endpoint: [(timestamp, count)]}}
        self.requests: Dict[str, Dict[str, list]] = {}
        self.window_size = 60  # 1 minute window
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, endpoint: str) -> Tuple[bool, int]:
        """
        Check if request should be rate limited
        
        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        now = time.time()
        
        # Initialize tracking for this IP
        if client_ip not in self.requests:
            self.requests[client_ip] = {}
        
        if endpoint not in self.requests[client_ip]:
            self.requests[client_ip][endpoint] = []
        
        # Clean old entries outside the window
        self.requests[client_ip][endpoint] = [
            ts for ts in self.requests[client_ip][endpoint]
            if now - ts < self.window_size
        ]
        
        # Check limit
        request_count = len(self.requests[client_ip][endpoint])
        
        if request_count >= self.requests_per_minute:
            # Calculate retry after
            oldest_request = min(self.requests[client_ip][endpoint])
            retry_after = int(self.window_size - (now - oldest_request))
            return True, max(1, retry_after)
        
        # Record this request
        self.requests[client_ip][endpoint].append(now)
        return False, 0
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for certain paths
        path = request.url.path
        if path in ["/", "/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        # Get endpoint identifier (method + path)
        endpoint = f"{request.method}:{path}"
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        is_limited, retry_after = self._is_rate_limited(client_ip, endpoint)
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
        
        return await call_next(request)


class EndpointRateLimiter:
    """
    Decorator-style rate limiter for specific endpoints
    More granular control than middleware
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        self.window_size = 60
    
    def __call__(self, request: Request):
        """Check rate limit for request"""
        client_ip = self._get_client_ip(request)
        endpoint = str(request.url.path)
        key = f"{client_ip}:{endpoint}"
        
        now = time.time()
        
        # Clean old entries
        if key in self.requests:
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < self.window_size
            ]
        else:
            self.requests[key] = []
        
        # Check limit
        if len(self.requests[key]) >= self.requests_per_minute:
            oldest = min(self.requests[key])
            retry_after = int(self.window_size - (now - oldest))
            
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Record request
        self.requests[key].append(now)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# Pre-configured limiters for different endpoint types
strict_limiter = EndpointRateLimiter(requests_per_minute=5)    # For sensitive operations
standard_limiter = EndpointRateLimiter(requests_per_minute=30)  # For standard operations
lenient_limiter = EndpointRateLimiter(requests_per_minute=60)   # For read operations
