"""
Maintenance Routes
==================
Endpoints para operações de manutenção
"""

from fastapi import APIRouter, HTTPException, Path, Depends

from app.core.config import logger
from app.core.constants import EngineType
from app.models import DatabaseConfig, MaintenanceResult
from app.services.maintenance import maintenance_service
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import strict_limiter
from fastapi import Request

router = APIRouter()


@router.get("/tools/{engine_id}")
async def get_maintenance_tools(engine_id: EngineType):
    """Lista ferramentas de manutenção para um motor"""
    tools = maintenance_service.get_tools(engine_id)
    return {"tools": [tool.model_dump() for tool in tools]}


@router.post("/{action}")
async def execute_maintenance(
    request: Request,
    action: str = Path(..., description="Nome da ação de manutenção"),
    config: DatabaseConfig = ...,
    user: str = Depends(get_current_user)
):
    """Executa ação de manutenção no banco de dados"""
    # Rate limiting: 5 maintenance operations per minute
    strict_limiter(request)
    logger.info(f"Executando manutenção: {action} em {config.engine}")
    
    result = maintenance_service.execute_action(action, config)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result.model_dump()
