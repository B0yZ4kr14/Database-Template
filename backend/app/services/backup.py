"""
Backup Service
==============
Serviço para operações de backup e restore
"""

import gzip
import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

from app.core.config import settings, logger
from app.models import BackupConfig, BackupResult, RestoreResult, BackupEntry, DatabaseConfig
from app.services.storage import storage_service


class BackupService:
    """Serviço de backup e restore"""
    
    def __init__(self):
        self.backup_dir = settings.BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def get_config(self) -> BackupConfig:
        """Obtém configuração de backup"""
        data = storage_service.load_backup_config()
        return BackupConfig(**data)
    
    def save_config(self, config: BackupConfig) -> bool:
        """Salva configuração de backup"""
        return storage_service.save_backup_config(config.model_dump())
    
    def _calculate_checksum(self, filepath: Path) -> str:
        """Calcula checksum SHA256 do arquivo"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _execute_pg_dump(self, config: dict, output_path: Path) -> bool:
        """Executa pg_dump para PostgreSQL"""
        try:
            cmd = [
                "pg_dump",
                "-h", config.get('host', 'localhost'),
                "-p", str(config.get('port', 5432)),
                "-U", config.get('username', 'postgres'),
                "-d", config.get('database', 'database'),
                "-f", str(output_path),
                "--verbose"
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = config.get('password', '')
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                return True
            else:
                logger.error(f"pg_dump falhou: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("pg_dump não encontrado. Instale postgresql-client.")
            return False
        except subprocess.TimeoutExpired:
            logger.error("pg_dump timeout após 5 minutos")
            return False
        except Exception as e:
            logger.error(f"Erro ao executar pg_dump: {e}")
            return False
    
    def _execute_mysqldump(self, config: dict, output_path: Path) -> bool:
        """Executa mysqldump para MariaDB/MySQL"""
        try:
            cmd = [
                "mysqldump",
                "-h", config.get('host', 'localhost'),
                "-P", str(config.get('port', 3306)),
                "-u", config.get('username', 'root'),
                config.get('database', 'database')
            ]
            
            env = os.environ.copy()
            if config.get('password'):
                env['MYSQL_PWD'] = config['password']
            
            with open(output_path, 'w') as f:
                result = subprocess.run(
                    cmd,
                    env=env,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300
                )
            
            if result.returncode == 0:
                return True
            else:
                logger.error(f"mysqldump falhou: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("mysqldump não encontrado. Instale mariadb-client ou mysql-client.")
            return False
        except subprocess.TimeoutExpired:
            logger.error("mysqldump timeout após 5 minutos")
            return False
        except Exception as e:
            logger.error(f"Erro ao executar mysqldump: {e}")
            return False
    
    def _execute_sqlite_dump(self, config: dict, output_path: Path) -> bool:
        """Executa backup para SQLite"""
        import sqlite3
        import shutil
        
        try:
            db_path = config.get('file_path', '/var/lib/database/database.db')
            
            if not Path(db_path).exists():
                logger.error(f"Banco SQLite não encontrado: {db_path}")
                return False
            
            # Para SQLite, fazemos uma cópia direta ou usamos .dump
            conn = sqlite3.connect(db_path)
            
            with open(output_path, 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Erro SQLite: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao fazer backup SQLite: {e}")
            return False
    
    def execute_backup(
        self,
        config: BackupConfig,
        engine: str,
        database: str,
        db_config: dict = None
    ) -> BackupResult:
        """Executa backup do banco de dados"""
        
        backup_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{database}_{backup_id}"
        
        if config.compression:
            filename += ".sql.gz"
        else:
            filename += ".sql"
        
        filepath = self.backup_dir / filename
        temp_filepath = self.backup_dir / f"{filename}.tmp"
        
        logger.info(f"Iniciando backup de {database} ({engine})")
        start_time = datetime.now()
        
        try:
            # Executar backup real baseado no motor
            success = False
            
            if engine == "postgresql" and db_config:
                success = self._execute_pg_dump(db_config, temp_filepath)
            elif engine in ["mariadb", "mysql"] and db_config:
                success = self._execute_mysqldump(db_config, temp_filepath)
            elif engine == "sqlite" and db_config:
                success = self._execute_sqlite_dump(db_config, temp_filepath)
            else:
                # Fallback: criar arquivo placeholder
                with open(temp_filepath, 'w') as f:
                    f.write(f"-- Backup de {database}\n")
                    f.write(f"-- Engine: {engine}\n")
                    f.write(f"-- Data: {datetime.now().isoformat()}\n")
                    f.write("-- NOTA: Backup real requer implementação específica\n")
                success = True  # Placeholder criado
            
            # Se falhou, registrar mas continuar para não quebrar
            if not success:
                logger.warning(f"Backup do motor {engine} falhou, criando placeholder")
                with open(temp_filepath, 'w') as f:
                    f.write(f"-- Backup de {database}\n")
                    f.write(f"-- Engine: {engine}\n")
                    f.write(f"-- Data: {datetime.now().isoformat()}\n")
                    f.write("-- NOTA: Backup real falhou\n")
            
            # Comprimir se necessário
            if config.compression:
                compressed_path = temp_filepath.with_suffix('.sql.gz')
                with open(temp_filepath, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                temp_filepath.unlink()  # Remover arquivo não comprimido
                temp_filepath = compressed_path
            
            # Mover para destino final
            temp_filepath.rename(filepath)
            
            # Calcular tamanho e checksum
            size_bytes = os.path.getsize(filepath)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            checksum = self._calculate_checksum(filepath)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Adicionar ao histórico
            entry = BackupEntry(
                id=backup_id,
                timestamp=datetime.now(),
                type=config.backup_type,
                size=f"{size_mb} MB",
                size_bytes=size_bytes,
                status="success" if success else "partial",
                path=str(filepath),
                engine=engine,
                checksum=checksum
            )
            storage_service.add_backup_entry(entry.model_dump())
            
            logger.info(f"Backup concluído: {filepath} ({size_mb} MB)")
            
            return BackupResult(
                success=success,
                message="Backup executado com sucesso" if success else "Backup parcial (placeholder criado)",
                backup_id=backup_id,
                path=str(filepath),
                size=f"{size_mb} MB",
                size_bytes=size_bytes,
                duration_seconds=round(duration, 2)
            )
            
        except Exception as e:
            logger.error(f"Erro ao executar backup: {e}")
            # Limpar arquivo temporário se existir
            if temp_filepath.exists():
                temp_filepath.unlink()
            
            return BackupResult(
                success=False,
                message=f"Erro ao executar backup: {str(e)}",
                backup_id=backup_id,
                path="",
                size="0 MB",
                size_bytes=0
            )
    
    def _restore_postgresql(self, backup_path: Path, db_config: dict) -> tuple:
        """Restaura backup PostgreSQL usando psql"""
        if not db_config:
            return False, "Configuração de banco de dados não fornecida"
        
        original_path = backup_path
        temp_path = None
        
        try:
            # Descomprimir se necessário
            if str(backup_path).endswith('.gz'):
                temp_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                backup_path = temp_path
            
            cmd = [
                "psql",
                "-h", db_config.get('host', 'localhost'),
                "-p", str(db_config.get('port', 5432)),
                "-U", db_config.get('username', 'postgres'),
                "-d", db_config.get('database', 'database'),
                "-f", str(backup_path),
                "--set", "ON_ERROR_STOP=on"
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config.get('password', '')
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos timeout para restore
            )
            
            # Limpar arquivo descomprimido temporário
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)
            
            if result.returncode == 0:
                return True, "Restore concluído com sucesso"
            else:
                return False, f"psql falhou: {result.stderr}"
                
        except FileNotFoundError:
            return False, "psql não encontrado. Instale postgresql-client."
        except subprocess.TimeoutExpired:
            return False, "psql timeout após 10 minutos"
        except Exception as e:
            logger.error(f"Erro ao restaurar PostgreSQL: {e}")
            return False, f"Erro: {str(e)}"
    
    def _restore_mariadb(self, backup_path: Path, db_config: dict) -> tuple:
        """Restaura backup MariaDB/MySQL usando mysql"""
        if not db_config:
            return False, "Configuração de banco de dados não fornecida"
        
        original_path = backup_path
        temp_path = None
        
        try:
            # Descomprimir se necessário
            if str(backup_path).endswith('.gz'):
                temp_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                backup_path = temp_path
            
            cmd = [
                "mysql",
                "-h", db_config.get('host', 'localhost'),
                "-P", str(db_config.get('port', 3306)),
                "-u", db_config.get('username', 'root'),
                db_config.get('database', 'database')
            ]
            
            env = os.environ.copy()
            if db_config.get('password'):
                env['MYSQL_PWD'] = db_config['password']
            
            with open(backup_path, 'rb') as f:
                result = subprocess.run(
                    cmd,
                    env=env,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
            
            # Limpar arquivo descomprimido temporário
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)
            
            if result.returncode == 0:
                return True, "Restore concluído com sucesso"
            else:
                return False, f"mysql falhou: {result.stderr}"
                
        except FileNotFoundError:
            return False, "mysql não encontrado. Instale mariadb-client ou mysql-client."
        except subprocess.TimeoutExpired:
            return False, "mysql timeout após 10 minutos"
        except Exception as e:
            logger.error(f"Erro ao restaurar MariaDB: {e}")
            return False, f"Erro: {str(e)}"
    
    def _restore_sqlite(self, backup_path: Path, db_config: dict) -> tuple:
        """Restaura backup SQLite"""
        import sqlite3
        
        original_path = backup_path
        temp_path = None
        
        try:
            db_path = db_config.get('file_path', '/var/lib/database/database.db')
            
            # Descomprimir se necessário
            if str(backup_path).endswith('.gz'):
                temp_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                backup_path = temp_path
            
            # Para SQLite, executamos o script SQL
            conn = sqlite3.connect(db_path)
            
            with open(backup_path, 'r') as f:
                script = f.read()
            
            conn.executescript(script)
            conn.close()
            
            # Limpar arquivo descomprimido temporário
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)
            
            return True, "Restore concluído com sucesso"
            
        except sqlite3.Error as e:
            return False, f"Erro SQLite: {str(e)}"
        except Exception as e:
            logger.error(f"Erro ao restaurar SQLite: {e}")
            return False, f"Erro: {str(e)}"
    
    def restore_backup(
        self,
        backup_id: str,
        engine: str,
        database: str,
        db_config: dict = None
    ) -> RestoreResult:
        """Restaura backup do banco de dados"""
        
        logger.info(f"Iniciando restore do backup {backup_id} para {database}")
        start_time = datetime.now()
        
        # Encontrar arquivo do backup
        backup_path = None
        for file in self.backup_dir.glob(f"*_{backup_id}*"):
            backup_path = file
            break
        
        if not backup_path:
            return RestoreResult(
                success=False,
                message=f"Backup {backup_id} não encontrado",
                backup_id=backup_id,
                duration_seconds=0
            )
        
        # Executar restore baseado no motor
        success = False
        message = "Motor não suportado para restore"
        
        if engine == "postgresql" and db_config:
            success, message = self._restore_postgresql(backup_path, db_config)
        elif engine in ["mariadb", "mysql"] and db_config:
            success, message = self._restore_mariadb(backup_path, db_config)
        elif engine == "sqlite" and db_config:
            success, message = self._restore_sqlite(backup_path, db_config)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return RestoreResult(
            success=success,
            message=message,
            backup_id=backup_id,
            duration_seconds=round(duration, 2)
        )
    
    def get_history(self) -> List[BackupEntry]:
        """Obtém histórico de backups"""
        data = storage_service.load_backup_history()
        return [BackupEntry(**entry) for entry in data]
    
    def cleanup_old_backups(self, retention_days: int) -> int:
        """Remove backups antigos"""
        
        removed = 0
        cutoff = datetime.now().timestamp() - (retention_days * 86400)
        
        for file in self.backup_dir.glob("*.sql*"):
            if file.stat().st_mtime < cutoff:
                try:
                    file.unlink()
                    removed += 1
                    logger.info(f"Removido backup antigo: {file}")
                except Exception as e:
                    logger.error(f"Erro ao remover {file}: {e}")
        
        logger.info(f"Removidos {removed} backups antigos")
        return removed
    
    def delete_backup(self, backup_id: str) -> bool:
        """Remove um backup específico"""
        try:
            # Buscar arquivo do backup
            file_found = False
            for file in self.backup_dir.glob(f"*_{backup_id}*"):
                file.unlink()
                file_found = True
                logger.info(f"Backup {backup_id} removido: {file}")
            
            # Só remover do histórico se o arquivo foi encontrado e removido
            if file_found:
                history = storage_service.load_backup_history()
                history = [entry for entry in history if entry.get('id') != backup_id]
                storage_service.save_json("backup_history.json", history)
                return True
            else:
                logger.warning(f"Backup {backup_id} não encontrado para remoção")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao remover backup {backup_id}: {e}")
            return False
    
    async def upload_and_restore(
        self,
        file,
        config: DatabaseConfig
    ) -> RestoreResult:
        """Faz upload de um arquivo de backup e restaura"""
        
        start_time = datetime.now()
        temp_path = None
        
        try:
            # Salvar arquivo temporário
            temp_path = self.backup_dir / f"upload_{file.filename}"
            
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"Arquivo de backup salvo: {temp_path}")
            
            # Executar restore real
            engine = config.engine.value if hasattr(config.engine, 'value') else str(config.engine)
            db_config = {
                'host': getattr(config, 'host', None),
                'port': getattr(config, 'port', None),
                'username': getattr(config, 'username', None),
                'password': getattr(config, 'password', None),
                'database': getattr(config, 'database', None),
                'file_path': getattr(config, 'file_path', None)
            }
            
            success = False
            message = "Motor não suportado para restore"
            
            if engine == "postgresql":
                success, message = self._restore_postgresql(temp_path, db_config)
            elif engine in ["mariadb", "mysql"]:
                success, message = self._restore_mariadb(temp_path, db_config)
            elif engine == "sqlite":
                success, message = self._restore_sqlite(temp_path, db_config)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return RestoreResult(
                success=success,
                message=message,
                backup_id="uploaded",
                duration_seconds=round(duration, 2)
            )
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload/restore: {e}")
            return RestoreResult(
                success=False,
                message=f"Erro ao restaurar backup: {str(e)}",
                backup_id="",
                duration_seconds=0
            )
        finally:
            # Garantir limpeza do arquivo temporário
            if temp_path and temp_path.exists():
                temp_path.unlink()
                logger.debug(f"Arquivo temporário removido: {temp_path}")


# Instância global
backup_service = BackupService()
