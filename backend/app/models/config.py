"""
Configuration Models
====================
Modelos Pydantic para configurações
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.core.constants import EngineType, BackupInterval, BackupType


class DatabaseConfig(BaseModel):
    """Configuração de conexão com banco de dados"""
    
    engine: EngineType = Field(
        default=EngineType.POSTGRESQL,
        description="Motor do banco de dados"
    )
    host: str = Field(
        default="localhost",
        description="Host do servidor",
        min_length=1
    )
    port: int = Field(
        default=5432,
        description="Porta de conexão",
        ge=0,
        le=65535
    )
    database: str = Field(
        default="my_database",
        description="Nome do banco de dados",
        min_length=1
    )
    username: str = Field(
        default="postgres",
        description="Usuário de conexão"
    )
    password: str = Field(
        default="",
        description="Senha de conexão"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Caminho do arquivo (SQLite)"
    )
    ssl_mode: str = Field(
        default="prefer",
        description="Modo SSL (PostgreSQL)"
    )
    charset: str = Field(
        default="utf8mb4",
        description="Charset (MariaDB)"
    )
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int, info) -> int:
        """Valida porta conforme o motor"""
        # Em Pydantic v2, usamos info.data para acessar outros campos
        engine = info.data.get('engine')
        if engine == EngineType.SQLITE and v != 0:
            return 0
        return v
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: Optional[str], info) -> Optional[str]:
        """Valida caminho do arquivo para SQLite"""
        engine = info.data.get('engine')
        if engine == EngineType.SQLITE and not v:
            return "/var/lib/myapp/database.db"
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "engine": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "my_database",
                "username": "postgres",
                "password": "senha_segura"
            }
        }


class BackupConfig(BaseModel):
    """Configuração de backup"""
    
    auto_backup: bool = Field(
        default=False,
        description="Ativar backup automático"
    )
    interval: BackupInterval = Field(
        default=BackupInterval.DAILY,
        description="Intervalo entre backups"
    )
    retention_days: int = Field(
        default=7,
        description="Dias para reter backups",
        ge=1,
        le=365
    )
    compression: bool = Field(
        default=True,
        description="Comprimir backups"
    )
    encryption: bool = Field(
        default=False,
        description="Criptografar backups"
    )
    destination: str = Field(
        default="/opt/database/backups",
        description="Diretório de destino"
    )
    backup_type: BackupType = Field(
        default=BackupType.FULL,
        description="Tipo de backup"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "auto_backup": True,
                "interval": "daily",
                "retention_days": 14,
                "compression": True,
                "encryption": False
            }
        }
