"""
Storage Service
===============
Serviço para persistência de dados em JSON
"""

import json
import uuid
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.config import settings, logger
from app.core.constants import MAX_HISTORY_ENTRIES


class StorageService:
    """Serviço de armazenamento de dados"""
    
    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self.ensure_directories()
    
    def ensure_directories(self):
        """Garante que os diretórios existam"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        settings.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, filename: str) -> Path:
        """Retorna caminho completo do arquivo"""
        return self.data_dir / filename
    
    def _json_serializer(self, obj: Any) -> str:
        """Serializador JSON customizado"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        raise TypeError(f"Tipo não serializável: {type(obj)}")
    
    def load_json(self, filename: str, default: Any = None) -> Any:
        """Carrega dados de arquivo JSON"""
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            return default
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar {filename}: {e}")
            # Backup do arquivo corrompido
            backup_path = file_path.with_suffix('.json.bak')
            file_path.rename(backup_path)
            logger.info(f"Arquivo corrompido movido para {backup_path}")
            return default
        except Exception as e:
            logger.error(f"Erro ao carregar {filename}: {e}")
            return default
    
    def save_json(self, filename: str, data: Any) -> bool:
        """Salva dados em arquivo JSON com lock para evitar race conditions"""
        file_path = self._get_file_path(filename)
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            # Escrever em arquivo temporário primeiro
            with open(temp_path, 'w', encoding='utf-8') as f:
                # Usar lock exclusivo
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(
                        data, 
                        f, 
                        indent=2, 
                        ensure_ascii=False, 
                        default=self._json_serializer
                    )
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            # Mover arquivo temporário para o destino final (atômico)
            temp_path.replace(file_path)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar {filename}: {e}")
            # Limpar arquivo temporário se existir
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Carrega configuração do banco de dados"""
        return self.load_json("db_config.json")
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Salva configuração do banco de dados"""
        return self.save_json("db_config.json", config)
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Carrega histórico de conexões"""
        return self.load_json("connection_history.json", [])
    
    def add_history_entry(self, entry: Dict[str, Any]) -> bool:
        """Adiciona entrada ao histórico com lock para evitar race conditions"""
        file_path = self._get_file_path("connection_history.json")
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            # Usar lock de arquivo para operação atômica read-modify-write
            with open(temp_path, 'w', encoding='utf-8') as lock_file:
                # Lock exclusivo durante toda a operação
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    # Recarregar histórico dentro do lock (estado mais recente)
                    history = self.load_history()
                    
                    # Gerar UUID completo (não truncado)
                    entry['id'] = str(uuid.uuid4())
                    entry['timestamp'] = datetime.now().isoformat()
                    
                    history.insert(0, entry)
                    history = history[:MAX_HISTORY_ENTRIES]
                    
                    # Salvar dentro do lock
                    json.dump(
                        history,
                        lock_file,
                        indent=2,
                        ensure_ascii=False,
                        default=self._json_serializer
                    )
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            
            # Mover arquivo atomicamente
            temp_path.replace(file_path)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar ao histórico: {e}")
            # Limpar arquivo temporário se existir
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def clear_history(self) -> bool:
        """Limpa histórico de conexões"""
        return self.save_json("connection_history.json", [])
    
    def load_backup_config(self) -> Dict[str, Any]:
        """Carrega configuração de backup"""
        default = {
            "auto_backup": False,
            "interval": "daily",
            "retention_days": 7,
            "compression": True,
            "encryption": False,
            "destination": str(settings.BACKUP_DIR),
            "backup_type": "full"
        }
        return self.load_json("backup_config.json", default)
    
    def save_backup_config(self, config: Dict[str, Any]) -> bool:
        """Salva configuração de backup"""
        return self.save_json("backup_config.json", config)
    
    def load_backup_history(self) -> List[Dict[str, Any]]:
        """Carrega histórico de backups"""
        return self.load_json("backup_history.json", [])
    
    def add_backup_entry(self, entry: Dict[str, Any]) -> bool:
        """Adiciona entrada ao histórico de backups"""
        try:
            history = self.load_backup_history()
            history.insert(0, entry)
            return self.save_json("backup_history.json", history)
        except Exception as e:
            logger.error(f"Erro ao adicionar backup ao histórico: {e}")
            return False


# Instância global
storage_service = StorageService()
