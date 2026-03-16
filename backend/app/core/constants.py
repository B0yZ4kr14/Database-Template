"""
Constants
=========
Constantes utilizadas em toda a aplicação
"""

from enum import Enum


class EngineType(str, Enum):
    """Tipos de motores de banco de dados suportados"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MARIADB = "mariadb"
    FIREBIRD = "firebird"


class MaintenanceAction(str, Enum):
    """Ações de manutenção disponíveis"""
    VACUUM = "vacuum"
    VACUUM_FULL = "vacuum_full"
    ANALYZE = "analyze"
    REINDEX = "reindex"
    REINDEX_DATABASE = "reindex_database"
    INTEGRITY_CHECK = "integrity_check"
    OPTIMIZE_TABLE = "optimize_table"
    CHECK_TABLE = "check_table"
    REPAIR_TABLE = "repair_table"
    GFIX_V = "gfix_v"
    GFIX_SWEEP = "gfix_sweep"
    GBAK = "gbak"
    GSTAT = "gstat"


class BackupType(str, Enum):
    """Tipos de backup"""
    FULL = "full"
    INCREMENTAL = "incremental"


class BackupInterval(str, Enum):
    """Intervalos de backup"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Configurações padrão por motor
DEFAULT_PORTS = {
    EngineType.SQLITE: None,
    EngineType.POSTGRESQL: 5432,
    EngineType.MARIADB: 3306,
    EngineType.FIREBIRD: 3050,
}

DEFAULT_DATABASES = {
    EngineType.SQLITE: "database",
    EngineType.POSTGRESQL: "my_database",
    EngineType.MARIADB: "my_database",
    EngineType.FIREBIRD: "my_database",
}

DEFAULT_USERS = {
    EngineType.SQLITE: "",
    EngineType.POSTGRESQL: "postgres",
    EngineType.MARIADB: "root",
    EngineType.FIREBIRD: "SYSDBA",
}

# Limites
MAX_HISTORY_ENTRIES = 50
MAX_BACKUP_RETENTION_DAYS = 365

# Timeouts
CONNECTION_TIMEOUT = 30
REQUEST_TIMEOUT = 60
