"""
Engines Routes
==============
Endpoints para informações sobre motores de banco de dados
"""

from fastapi import APIRouter, HTTPException

from app.core.constants import EngineType
from app.data.engines import ENGINE_DETAILS, ENGINES_LIST

router = APIRouter()


@router.get("")
async def get_engines():
    """Lista todos os motores disponíveis"""
    return {"engines": [engine.model_dump() for engine in ENGINES_LIST]}


@router.get("/{engine_id}")
async def get_engine_details(engine_id: EngineType):
    """Obtém detalhes de um motor específico"""
    details = ENGINE_DETAILS.get(engine_id)
    
    if not details:
        raise HTTPException(status_code=404, detail="Motor não encontrado")
    
    return details.model_dump()
