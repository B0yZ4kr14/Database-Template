"""
Response Models
===============
Modelos Pydantic para respostas da API
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ApiResponse(BaseModel):
    """Resposta padrão da API"""
    success: bool = Field(default=True)
    message: str = Field(default="")
    data: Optional[Dict[str, Any]] = Field(default=None)


class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str = Field(default="healthy")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="2.0.2")
    environment: str = Field(default="production")
    uptime: Optional[float] = Field(default=None)


class ConnectionTestResult(BaseModel):
    """Resultado do teste de conexão"""
    success: bool = Field(...)
    message: str = Field(...)
    details: Optional[Dict[str, Any]] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_ms: Optional[int] = Field(default=None)


class ConnectionHistoryEntry(BaseModel):
    """Entrada do histórico de conexões"""
    id: str = Field(...)
    timestamp: datetime = Field(...)
    engine: str = Field(...)
    host: str = Field(...)
    database: str = Field(...)
    status: str = Field(...)
    message: str = Field(...)


class MaintenanceResult(BaseModel):
    """Resultado da ação de manutenção"""
    success: bool = Field(...)
    action: str = Field(...)
    message: str = Field(...)
    sql_executed: Optional[str] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    affected_rows: Optional[int] = Field(default=None)


class MigrationResult(BaseModel):
    """Resultado da migração"""
    success: bool = Field(...)
    message: str = Field(...)
    source_engine: str = Field(...)
    target_engine: str = Field(...)
    tables_migrated: int = Field(default=0)
    records_migrated: int = Field(default=0)
    duration_seconds: Optional[float] = Field(default=None)


class BackupEntry(BaseModel):
    """Entrada de backup no histórico"""
    id: str = Field(...)
    timestamp: datetime = Field(...)
    type: str = Field(...)
    size: str = Field(...)
    size_bytes: int = Field(...)
    status: str = Field(...)
    path: str = Field(...)
    engine: str = Field(...)
    checksum: Optional[str] = Field(default=None)


class BackupResult(BaseModel):
    """Resultado do backup"""
    success: bool = Field(...)
    message: str = Field(...)
    backup_id: str = Field(...)
    path: str = Field(...)
    size: str = Field(...)
    size_bytes: int = Field(...)
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_seconds: Optional[float] = Field(default=None)


class RestoreResult(BaseModel):
    """Resultado da restauração"""
    success: bool = Field(...)
    message: str = Field(...)
    backup_id: str = Field(...)
    duration_seconds: Optional[float] = Field(default=None)
