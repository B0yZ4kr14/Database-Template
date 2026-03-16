"""
Migration Routes
================
Endpoints para migração de dados
"""

from fastapi import APIRouter, HTTPException

from app.core.config import logger
from app.models import DatabaseConfig, MigrationResult
from app.services.migration import migration_service

router = APIRouter()


@router.post("/export")
async def export_data(config: DatabaseConfig, format: str = "sql"):
    """Exporta dados do banco"""
    logger.info(f"Exportando dados de {config.engine} no formato {format}")
    
    result = migration_service.export_data(config, format)
    return result


@router.post("/import")
async def import_data(config: DatabaseConfig, file_path: str):
    """Importa dados para o banco"""
    logger.info(f"Importando dados para {config.engine}")
    
    result = migration_service.import_data(config, file_path)
    return result


@router.post("/execute")
async def execute_migration(source: DatabaseConfig, target: DatabaseConfig):
    """Executa migração entre motores"""
    logger.info(f"Migração de {source.engine} para {target.engine}")
    
    result = migration_service.execute_migration(source, target)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result.model_dump()
