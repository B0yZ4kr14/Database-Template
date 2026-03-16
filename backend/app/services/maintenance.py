"""
Maintenance Service
===================
Serviço para operações de manutenção de banco de dados
"""

import sqlite3
import time
from typing import List, Dict

from app.core.config import logger
from app.core.constants import EngineType
from app.models import DatabaseConfig, MaintenanceResult, MaintenanceTool


class MaintenanceService:
    """Serviço de manutenção de banco de dados"""
    
    # Ferramentas disponíveis por motor
    TOOLS: Dict[EngineType, List[MaintenanceTool]] = {
        EngineType.SQLITE: [
            MaintenanceTool(
                id="vacuum",
                name="VACUUM",
                description="Compacta o banco e recupera espaço",
                sql="VACUUM;"
            ),
            MaintenanceTool(
                id="integrity_check",
                name="Integrity Check",
                description="Verifica integridade dos dados",
                sql="PRAGMA integrity_check;"
            ),
            MaintenanceTool(
                id="reindex",
                name="Reindex",
                description="Reconstrói todos os índices",
                sql="REINDEX;"
            ),
            MaintenanceTool(
                id="analyze",
                name="Analyze",
                description="Atualiza estatísticas das tabelas",
                sql="ANALYZE;"
            ),
        ],
        EngineType.POSTGRESQL: [
            MaintenanceTool(
                id="vacuum_full",
                name="VACUUM FULL",
                description="Compacta e recupera espaço",
                sql="VACUUM FULL;",
                warning="Bloqueia tabelas durante a execução"
            ),
            MaintenanceTool(
                id="analyze",
                name="ANALYZE",
                description="Atualiza estatísticas",
                sql="ANALYZE;"
            ),
            MaintenanceTool(
                id="reindex_database",
                name="REINDEX DATABASE",
                description="Reconstrói índices",
                sql="REINDEX DATABASE {database};"
            ),
            MaintenanceTool(
                id="pg_checksums",
                name="pg_checksums",
                description="Verifica checksums das páginas",
                sql="pg_checksums --check"
            ),
        ],
        EngineType.MARIADB: [
            MaintenanceTool(
                id="optimize_table",
                name="OPTIMIZE TABLE",
                description="Otimiza tabelas",
                sql="OPTIMIZE TABLE {table};"
            ),
            MaintenanceTool(
                id="analyze_table",
                name="ANALYZE TABLE",
                description="Atualiza estatísticas",
                sql="ANALYZE TABLE {table};"
            ),
            MaintenanceTool(
                id="check_table",
                name="CHECK TABLE",
                description="Verifica integridade",
                sql="CHECK TABLE {table};"
            ),
            MaintenanceTool(
                id="repair_table",
                name="REPAIR TABLE",
                description="Repara tabelas corrompidas",
                sql="REPAIR TABLE {table};"
            ),
        ],
        EngineType.FIREBIRD: [
            MaintenanceTool(
                id="gfix_v",
                name="gfix -v",
                description="Verifica integridade",
                sql="gfix -v -full {database}"
            ),
            MaintenanceTool(
                id="gfix_sweep",
                name="gfix -sweep",
                description="Limpa versões antigas",
                sql="gfix -sweep {database}"
            ),
            MaintenanceTool(
                id="gbak",
                name="gbak",
                description="Backup/Restore",
                sql="gbak -b {database} {backup}"
            ),
            MaintenanceTool(
                id="gstat",
                name="gstat",
                description="Estatísticas",
                sql="gstat -h {database}"
            ),
        ],
    }
    
    def get_tools(self, engine: EngineType) -> List[MaintenanceTool]:
        """Retorna ferramentas disponíveis para um motor"""
        return self.TOOLS.get(engine, [])
    
    def _sanitize_identifier(self, identifier: str) -> str:
        """
        Sanitiza identificadores SQL para prevenir SQL injection.
        Apenas permite caracteres alfanuméricos, underscore e pontos.
        """
        if not identifier:
            return ""
        
        # Remover caracteres perigosos
        sanitized = ''.join(c for c in identifier if c.isalnum() or c in '_-.')
        
        # Limitar tamanho
        return sanitized[:128]
    
    def _format_sql(self, sql_template: str, config: DatabaseConfig) -> str:
        """
        Formata SQL template de forma segura, sanitizando inputs.
        """
        # Sanitizar identificadores
        safe_database = self._sanitize_identifier(config.database)
        safe_table = "*"  # Placeholder para todas as tabelas
        safe_backup = self._sanitize_identifier(f"{config.database}_backup")
        
        try:
            formatted = sql_template.format(
                database=safe_database,
                table=safe_table,
                backup=safe_backup
            )
        except (KeyError, ValueError):
            # Se falhar a formatação, retorna o SQL original
            formatted = sql_template
        
        return formatted
    
    def _execute_sql_sqlite(self, sql: str, config: DatabaseConfig) -> tuple:
        """Executa SQL em banco SQLite"""
        import sqlite3
        from pathlib import Path
        
        db_path = config.file_path or "/var/lib/database/database.db"
        
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            conn.execute("PRAGMA busy_timeout = 5000")
            
            cursor = conn.cursor()
            
            # Para PRAGMA e VACUUM, executamos diretamente
            if sql.strip().upper().startswith('PRAGMA'):
                cursor.execute(sql)
                result = cursor.fetchone()
                conn.close()
                return True, f"Resultado: {result[0] if result else 'OK'}"
            elif sql.strip().upper() == 'VACUUM':
                conn.execute(sql)
                conn.close()
                return True, "Database compactado com sucesso"
            elif sql.strip().upper() == 'REINDEX':
                conn.execute(sql)
                conn.close()
                return True, "Índices reconstruídos com sucesso"
            elif sql.strip().upper() == 'ANALYZE':
                conn.execute(sql)
                conn.close()
                return True, "Estatísticas atualizadas com sucesso"
            else:
                cursor.execute(sql)
                conn.commit()
                conn.close()
                return True, "Comando executado com sucesso"
                
        except sqlite3.Error as e:
            logger.error(f"Erro SQLite: {e}")
            return False, f"Erro SQLite: {str(e)}"
        except Exception as e:
            logger.error(f"Erro inesperado SQLite: {e}")
            return False, f"Erro: {str(e)}"
    
    def _execute_sql_postgresql(self, sql: str, config: DatabaseConfig) -> tuple:
        """Executa SQL em banco PostgreSQL"""
        try:
            import psycopg2
            from psycopg2 import Error as Psycopg2Error
            
            conn = psycopg2.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.username,
                password=config.password,
                sslmode=config.ssl_mode or 'prefer',
                connect_timeout=10
            )
            
            conn.autocommit = True  # Necessário para VACUUM
            cursor = conn.cursor()
            
            # Executar o comando
            cursor.execute(sql)
            
            # Tentar obter resultado se houver
            try:
                result = cursor.fetchone()
                message = f"Resultado: {result[0] if result else 'OK'}"
            except psycopg2.ProgrammingError:
                message = "Comando executado com sucesso"
            
            cursor.close()
            conn.close()
            
            return True, message
            
        except ImportError:
            return False, "Driver psycopg2 não instalado. Execute: pip install psycopg2-binary"
        except Psycopg2Error as e:
            logger.error(f"Erro PostgreSQL: {e}")
            return False, f"Erro PostgreSQL: {str(e)}"
        except Exception as e:
            logger.error(f"Erro inesperado PostgreSQL: {e}")
            return False, f"Erro: {str(e)}"
    
    def _execute_sql_mariadb(self, sql: str, config: DatabaseConfig) -> tuple:
        """Executa SQL em banco MariaDB/MySQL"""
        try:
            import pymysql
            from pymysql import Error as PyMySQLError
            
            conn = pymysql.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database,
                charset=config.charset or 'utf8mb4',
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            cursor.execute(sql)
            
            # Tentar obter resultado
            if cursor.rowcount > 0:
                result = cursor.fetchone()
                message = f"Resultado: {result[0] if result else 'OK'}"
            else:
                message = "Comando executado com sucesso"
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, message
            
        except ImportError:
            return False, "Driver pymysql não instalado. Execute: pip install pymysql"
        except PyMySQLError as e:
            logger.error(f"Erro MariaDB: {e}")
            return False, f"Erro MariaDB: {str(e)}"
        except Exception as e:
            logger.error(f"Erro inesperado MariaDB: {e}")
            return False, f"Erro: {str(e)}"
    
    def _execute_sql_firebird(self, sql: str, config: DatabaseConfig) -> tuple:
        """Executa comando externo para Firebird (gfix, gbak, etc)"""
        import subprocess
        
        # Para Firebird, os comandos são executáveis externos
        try:
            # Substituir placeholders no comando
            cmd = sql.format(
                database=config.database,
                backup=f"{config.database}.backup"
            )
            
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, result.stdout or "Comando executado com sucesso"
            else:
                return False, f"Erro: {result.stderr}"
                
        except FileNotFoundError as e:
            return False, f"Comando não encontrado: {e}"
        except subprocess.TimeoutExpired:
            return False, "Timeout ao executar comando"
        except Exception as e:
            logger.error(f"Erro Firebird: {e}")
            return False, f"Erro: {str(e)}"
    
    def execute_action(
        self,
        action: str,
        config: DatabaseConfig
    ) -> MaintenanceResult:
        """Executa ação de manutenção"""
        
        start_time = time.time()
        
        # Validar ação
        valid_actions = [tool.id for tool in self.get_tools(config.engine)]
        if action not in valid_actions:
            return MaintenanceResult(
                success=False,
                action=action,
                message=f"Ação não permitida: {action}"
            )
        
        # Buscar ferramenta
        tool = next(
            (t for t in self.get_tools(config.engine) if t.id == action),
            None
        )
        
        if not tool:
            return MaintenanceResult(
                success=False,
                action=action,
                message=f"Ferramenta não encontrada: {action}"
            )
        
        # Formatar SQL de forma segura
        sql = self._format_sql(tool.sql, config)
        
        # Executar SQL real baseado no motor
        logger.info(f"Executando manutenção: {action} ({config.engine})")
        logger.info(f"SQL: {sql}")
        
        executors = {
            EngineType.SQLITE: self._execute_sql_sqlite,
            EngineType.POSTGRESQL: self._execute_sql_postgresql,
            EngineType.MARIADB: self._execute_sql_mariadb,
            EngineType.FIREBIRD: self._execute_sql_firebird,
        }
        
        executor = executors.get(config.engine)
        if executor:
            success, message = executor(sql, config)
        else:
            success = False
            message = f"Motor não suportado: {config.engine}"
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return MaintenanceResult(
            success=success,
            action=action,
            message=f"{tool.name}: {message}",
            sql_executed=sql,
            duration_ms=duration_ms
        )


# Instância global
maintenance_service = MaintenanceService()
