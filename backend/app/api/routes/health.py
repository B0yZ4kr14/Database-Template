"""
Health Routes
=============
Endpoints para verificação de saúde da API
"""

import time
from datetime import datetime
from fastapi import APIRouter

from app.core.config import settings
from app.models import HealthResponse

router = APIRouter()

# Track application start time for uptime calculation
_START_TIME = time.time()


@router.get("", response_model=HealthResponse)
async def health_check():
    """Verificação de saúde da API"""
    uptime_seconds = time.time() - _START_TIME
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        uptime=uptime_seconds
    )
