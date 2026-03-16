"""
Config Routes
=============
Endpoints para gerenciamento de configurações
"""

from fastapi import APIRouter, HTTPException

from app.core.config import logger
from app.models import DatabaseConfig, ApiResponse
from app.services.storage import storage_service

router = APIRouter()


@router.get("")
async def get_config():
    """Obtém configuração atual do banco de dados"""
    config = storage_service.load_config()
    
    if not config:
        # Configuração padrão
        config = DatabaseConfig().model_dump()
        storage_service.save_config(config)
    
    return config


@router.post("")
async def set_config(config: DatabaseConfig):
    """Salva configuração do banco de dados"""
    try:
        storage_service.save_config(config.model_dump())
        logger.info(f"Configuração salva para motor: {config.engine}")
        
        return ApiResponse(
            success=True,
            message="Configuração salva com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao salvar configuração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configuração: {str(e)}")
