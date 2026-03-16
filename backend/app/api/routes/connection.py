"""
Connection Routes
=================
Endpoints para teste de conexão e histórico
"""

from fastapi import APIRouter, HTTPException

from app.core.config import logger
from app.models import DatabaseConfig, ConnectionTestResult
from app.services.connection import connection_service
from app.services.storage import storage_service

router = APIRouter()
history_router = APIRouter()


@router.post("", response_model=ConnectionTestResult)
async def test_connection(config: DatabaseConfig):
    """Testa conexão com o banco de dados"""
    logger.info(f"Testando conexão com {config.engine}")
    
    result = connection_service.test_connection(config)
    
    # Adicionar ao histórico
    storage_service.add_history_entry({
        "engine": config.engine.value,
        "host": config.host if config.engine.value != "sqlite" else "localhost",
        "database": config.database if config.engine.value != "sqlite" else (config.file_path or "database.db"),
        "status": "success" if result.success else "error",
        "message": result.message
    })
    
    return result


@history_router.get("")
async def get_connection_history():
    """Obtém histórico de conexões"""
    return {"history": storage_service.load_history()}


@history_router.delete("")
async def clear_connection_history():
    """Limpa histórico de conexões"""
    if storage_service.clear_history():
        return {"success": True, "message": "Histórico limpo com sucesso"}
    raise HTTPException(status_code=500, detail="Erro ao limpar histórico")
