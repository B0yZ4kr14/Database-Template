"""
Docs Routes
===========
Endpoints para documentação dos motores
"""

from fastapi import APIRouter

from app.core.constants import EngineType
from app.data.engines import ENGINE_DETAILS

router = APIRouter()


@router.get("/{engine_id}")
async def get_engine_docs(engine_id: EngineType):
    """Obtém links de documentação para um motor"""
    details = ENGINE_DETAILS.get(engine_id)
    
    return {
        "engine": engine_id.value,
        "docs": [doc.model_dump() for doc in details.docs] if details else [],
        "install_ubuntu": details.install_ubuntu if details else "",
        "install_arch": details.install_arch if details else ""
    }
