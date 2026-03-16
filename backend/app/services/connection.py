"""
Connection Service
==================
Serviço para testar conexões com bancos de dados
"""

import sqlite3
import time
from pathlib import Path

from app.core.config import logger
from app.core.constants import EngineType
from app.models import DatabaseConfig, ConnectionTestResult


class ConnectionService:
    """Serviço de teste de conexões"""
    
    # Timeouts em segundos
    TIMEOUTS = {
        EngineType.SQLITE: 5,
        EngineType.POSTGRESQL: 10,
        EngineType.MARIADB: 10,
        EngineType.FIREBIRD: 10,
    }
    
    def test_connection(self, config: DatabaseConfig) -> ConnectionTestResult:
        """Testa conexão com o banco de dados"""
        
        start_time = time.time()
        
        test_methods = {
            EngineType.SQLITE: self._test_sqlite,
            EngineType.POSTGRESQL: self._test_postgresql,
            EngineType.MARIADB: self._test_mariadb,
            EngineType.FIREBIRD: self._test_firebird,
        }
        
        test_method = test_methods.get(config.engine)
        if not test_method:
            return ConnectionTestResult(
                success=False,
                message=f"Motor não suportado: {config.engine}",
                duration_ms=0
            )
        
        try:
            result = test_method(config)
        except Exception as e:
            # Capturar exceções específicas, não KeyboardInterrupt
            logger.error(f"Erro inesperado no teste de conexão: {e}")
            result = ConnectionTestResult(
                success=False,
                message=f"Erro inesperado: {str(e)}"
            )
        
        # Calcular duração
        duration_ms = int((time.time() - start_time) * 1000)
        result.duration_ms = duration_ms
        
        return result
    
    def _test_sqlite(self, config: DatabaseConfig) -> ConnectionTestResult:
        """Testa conexão SQLite"""
        conn = None
        try:
            db_path = config.file_path or "/var/lib/myapp/database.db"
            
            # Criar diretório se não existir
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Timeout explícito para SQLite
            conn = sqlite3.connect(db_path, timeout=self.TIMEOUTS[EngineType.SQLITE])
            conn.execute("PRAGMA busy_timeout = 5000")  # 5 segundos
            
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            
            file_size = Path(db_path).stat().st_size if Path(db_path).exists() else 0
            
            return ConnectionTestResult(
                success=True,
                message="Conexão SQLite estabelecida com sucesso!",
                details={
                    "version": version,
                    "path": db_path,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2)
                }
            )
        except sqlite3.Error as e:
            logger.error(f"Erro SQLite: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Erro SQLite: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erro inesperado SQLite: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Falha na conexão SQLite: {str(e)}"
            )
        finally:
            if conn is not None:
                conn.close()
    
    def _test_postgresql(self, config: DatabaseConfig) -> ConnectionTestResult:
        """Testa conexão PostgreSQL"""
        conn = None
        try:
            import psycopg2
            from psycopg2 import Error as Psycopg2Error
            
            conn = psycopg2.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.username,
                password=config.password,
                sslmode=config.ssl_mode,
                connect_timeout=self.TIMEOUTS[EngineType.POSTGRESQL]
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT pg_database_size(%s)", (config.database,))
            size = cursor.fetchone()[0]
            
            return ConnectionTestResult(
                success=True,
                message="Conexão PostgreSQL estabelecida com sucesso!",
                details={
                    "version": version,
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 2)
                }
            )
        except ImportError:
            return ConnectionTestResult(
                success=False,
                message="Driver psycopg2 não instalado. Execute: pip install psycopg2-binary"
            )
        except Psycopg2Error as e:
            logger.error(f"Erro PostgreSQL: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Erro PostgreSQL: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erro inesperado PostgreSQL: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Falha na conexão PostgreSQL: {str(e)}"
            )
        finally:
            if conn is not None:
                conn.close()
    
    def _test_mariadb(self, config: DatabaseConfig) -> ConnectionTestResult:
        """Testa conexão MariaDB"""
        conn = None
        try:
            import pymysql
            from pymysql import Error as PyMySQLError
            
            conn = pymysql.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database,
                charset=config.charset,
                connect_timeout=self.TIMEOUTS[EngineType.MARIADB]
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            return ConnectionTestResult(
                success=True,
                message="Conexão MariaDB estabelecida com sucesso!",
                details={"version": version}
            )
        except ImportError:
            return ConnectionTestResult(
                success=False,
                message="Driver pymysql não instalado. Execute: pip install pymysql"
            )
        except PyMySQLError as e:
            logger.error(f"Erro MariaDB: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Erro MariaDB: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erro inesperado MariaDB: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Falha na conexão MariaDB: {str(e)}"
            )
        finally:
            if conn is not None:
                conn.close()
    
    def _test_firebird(self, config: DatabaseConfig) -> ConnectionTestResult:
        """Testa conexão Firebird"""
        conn = None
        try:
            import fdb
            from fdb import Error as FdbError
            
            conn = fdb.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.username,
                password=config.password,
                timeout=self.TIMEOUTS[EngineType.FIREBIRD]
            )
            
            version = conn.firebird_version
            
            return ConnectionTestResult(
                success=True,
                message="Conexão Firebird estabelecida com sucesso!",
                details={"version": version}
            )
        except ImportError:
            return ConnectionTestResult(
                success=False,
                message="Driver fdb não instalado. Execute: pip install fdb"
            )
        except FdbError as e:
            logger.error(f"Erro Firebird: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Erro Firebird: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erro inesperado Firebird: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Falha na conexão Firebird: {str(e)}"
            )
        finally:
            if conn is not None:
                conn.close()


# Instância global
connection_service = ConnectionService()
