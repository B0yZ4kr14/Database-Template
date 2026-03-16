"""
Core Configuration
==================
Configurações centralizadas da aplicação
"""

import os
import sys
import logging
import secrets
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "Database API"
    APP_VERSION: str = "2.0.2"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Diretórios
    BASE_DIR: Path = Path("/opt/database")
    DATA_DIR: Path = Path("/opt/database/data")
    BACKUP_DIR: Path = Path("/opt/database/backups")
    LOG_DIR: Path = Path("/var/log/database")
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # CORS - Configuração segura por padrão
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        description="Lista de origins permitidas para CORS"
    )
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_HEADERS: List[str] = ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Banco de Dados Padrão
    DB_ENGINE: str = "postgresql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "my_database"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_SSL_MODE: str = "prefer"
    
    # Backup
    BACKUP_AUTO: bool = False
    BACKUP_INTERVAL: str = "daily"
    BACKUP_RETENTION_DAYS: int = 7
    BACKUP_COMPRESSION: bool = True
    BACKUP_ENCRYPTION: bool = False
    
    # Segurança
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Chave secreta para tokens JWT. Gerada automaticamente se não definida."
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Valida e converte CORS_ORIGINS para lista"""
        if isinstance(v, str):
            # Se for string, split por vírgula
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if isinstance(v, list) else ["*"]
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida nível de log"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL deve ser um de: {valid_levels}")
        return v_upper
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Valida que SECRET_KEY não é o valor inseguro padrão legado"""
        if v == "change-me-in-production":
            raise ValueError(
                "SECRET_KEY não pode ser o valor padrão inseguro 'change-me-in-production'. "
                "Defina uma chave segura via variável de ambiente ou deixe o sistema gerar uma."
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global de configurações
settings = Settings()


def setup_logging() -> logging.Logger:
    """Configura logging da aplicação"""
    
    # Garantir que diretório de logs existe (tentar múltiplos locais)
    log_dir = settings.LOG_DIR
    fallback_dirs = [
        settings.BASE_DIR / "logs",
        Path("/tmp/database-logs"),
        Path("."),
    ]
    
    for dir_path in [log_dir] + fallback_dirs:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            if dir_path.exists() and os.access(dir_path, os.W_OK):
                log_dir = dir_path
                break
        except (PermissionError, OSError):
            continue
    
    # Configurar handlers
    handlers = [logging.StreamHandler()]
    
    try:
        file_handler = logging.FileHandler(
            log_dir / "api.log",
            mode='a'
        )
        handlers.append(file_handler)
    except (PermissionError, IOError) as e:
        # Log para stderr se não conseguir criar arquivo
        sys.stderr.write(f"Aviso: Não foi possível criar arquivo de log em {log_dir}: {e}\n")
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
        handlers=handlers,
        force=True  # Força reconfiguração se já existir
    )
    
    return logging.getLogger(__name__)


# Logger global
logger = setup_logging()
