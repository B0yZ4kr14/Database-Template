"""
Engine Models
=============
Modelos para informações de motores de banco de dados
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.constants import EngineType


class MaintenanceTool(BaseModel):
    """Ferramenta de manutenção"""
    id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    sql: str = Field(...)
    warning: Optional[str] = Field(default=None)


class DocLink(BaseModel):
    """Link de documentação"""
    name: str = Field(...)
    url: str = Field(...)
    description: Optional[str] = Field(default=None)


class EngineInfo(BaseModel):
    """Informações básicas do motor"""
    id: EngineType = Field(...)
    name: str = Field(...)
    icon: str = Field(...)
    port: Optional[int] = Field(default=None)
    description: str = Field(...)


class EngineDetails(BaseModel):
    """Detalhes completos do motor"""
    id: EngineType = Field(...)
    name: str = Field(...)
    icon: str = Field(...)
    port: Optional[int] = Field(default=None)
    description: str = Field(...)
    when_to_use: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    install_ubuntu: str = Field(...)
    install_arch: Optional[str] = Field(default=None)
    maintenance_tools: List[MaintenanceTool] = Field(default_factory=list)
    docs: List[DocLink] = Field(default_factory=list)
