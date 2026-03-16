"""
Backup Routes
=============
Endpoints para operações de backup
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends

from app.core.config import logger
from app.models import DatabaseConfig, BackupConfig
from app.services.backup import backup_service
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import strict_limiter, standard_limiter
from fastapi import Request

router = APIRouter()


@router.get("/config")
async def get_backup_config():
    """Obtém configuração de backup"""
    config = backup_service.get_config()
    return config.model_dump()


@router.post("/config")
async def set_backup_config(config: BackupConfig):
    """Salva configuração de backup"""
    if backup_service.save_config(config):
        return {"success": True, "message": "Configuração de backup salva"}
    raise HTTPException(status_code=500, detail="Erro ao salvar configuração")


@router.post("/execute")
async def execute_backup(
    config: DatabaseConfig,
    background_tasks: BackgroundTasks,
    request: Request,
    user: str = Depends(get_current_user)
):
    # Rate limiting: 5 backups per minute
    strict_limiter(request)
    """Executa backup do banco de dados"""
    logger.info(f"Executando backup de {config.engine}")
    
    backup_config = backup_service.get_config()
    
    # Preparar configuração de conexão completa
    db_config = {
        'host': getattr(config, 'host', None),
        'port': getattr(config, 'port', None),
        'username': getattr(config, 'username', None),
        'password': getattr(config, 'password', None),
        'database': config.database,
        'file_path': getattr(config, 'file_path', None),
        'ssl_mode': getattr(config, 'ssl_mode', None),
        'charset': getattr(config, 'charset', None),
    }
    
    result = backup_service.execute_backup(
        backup_config,
        config.engine.value,
        config.database,
        db_config=db_config
    )
    
    return result.model_dump()


@router.post("/restore")
async def restore_backup(
    backup_id: str, 
    config: DatabaseConfig,
    request: Request,
    user: str = Depends(get_current_user)
):
    # Rate limiting: 5 restores per minute
    strict_limiter(request)
    """Restaura backup do banco de dados"""
    logger.info(f"Restaurando backup {backup_id}")
    
    # Preparar configuração de conexão completa
    db_config = {
        'host': getattr(config, 'host', None),
        'port': getattr(config, 'port', None),
        'username': getattr(config, 'username', None),
        'password': getattr(config, 'password', None),
        'database': config.database,
        'file_path': getattr(config, 'file_path', None),
        'ssl_mode': getattr(config, 'ssl_mode', None),
        'charset': getattr(config, 'charset', None),
    }
    
    result = backup_service.restore_backup(
        backup_id, 
        config.engine.value, 
        config.database,
        db_config=db_config
    )
    return result.model_dump()


@router.get("/history")
async def get_backup_history():
    """Obtém histórico de backups"""
    history = backup_service.get_history()
    return {"backups": [entry.model_dump() for entry in history]}


@router.delete("/{backup_id}")
async def delete_backup(
    backup_id: str,
    request: Request,
    user: str = Depends(get_current_user)
):
    # Rate limiting: 10 deletes per minute
    standard_limiter(request)
    """Remove um backup específico"""
    logger.info(f"Removendo backup {backup_id}")
    
    if backup_service.delete_backup(backup_id):
        return {"success": True, "message": "Backup removido com sucesso"}
    
    raise HTTPException(status_code=404, detail="Backup não encontrado")


@router.post("/upload-restore")
async def upload_and_restore(
    file: UploadFile = File(...),
    config: DatabaseConfig = ...,
    user: str = Depends(get_current_user)
):
    """Faz upload de um arquivo de backup e restaura"""
    logger.info(f"Upload de arquivo de backup: {file.filename}")
    
    result = await backup_service.upload_and_restore(file, config)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result.model_dump()
