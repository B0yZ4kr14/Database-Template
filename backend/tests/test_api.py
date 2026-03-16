"""
API Tests
=========
Testes para endpoints da API
"""

import os
import sys

# Garante que o diretório backend esteja no PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRoot:
    """Testes para rota raiz"""
    
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Database API"
        assert "version" in data


class TestHealth:
    """Testes para health check"""
    
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestEngines:
    """Testes para motores"""
    
    def test_list_engines(self):
        response = client.get("/api/engines")
        assert response.status_code == 200
        data = response.json()
        assert "engines" in data
        assert len(data["engines"]) == 4
    
    def test_get_engine_details(self):
        response = client.get("/api/engines/postgresql")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "postgresql"


class TestConfig:
    """Testes para configuração"""
    
    def test_get_config(self):
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "engine" in data
    
    def test_post_config(self):
        config = {
            "engine": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "username": "postgres",
            "password": "test"
        }
        response = client.post("/api/config", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestConnection:
    """Testes para conexão"""
    
    def test_get_history(self):
        response = client.get("/api/connection-history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data


class TestMaintenance:
    """Testes para manutenção"""
    
    def test_get_tools(self):
        response = client.get("/api/maintenance/tools/postgresql")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data


class TestBackup:
    """Testes para backup"""
    
    def test_get_backup_config(self):
        response = client.get("/api/backup/config")
        assert response.status_code == 200
        data = response.json()
        assert "auto_backup" in data
    
    def test_get_backup_history(self):
        response = client.get("/api/backup/history")
        assert response.status_code == 200
        data = response.json()
        assert "backups" in data


class TestDocs:
    """Testes para documentação"""
    
    def test_get_docs(self):
        response = client.get("/api/docs/postgresql")
        assert response.status_code == 200
        data = response.json()
        assert "docs" in data
