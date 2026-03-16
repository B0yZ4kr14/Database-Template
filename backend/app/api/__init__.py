# API module
from fastapi import APIRouter

from .routes import health, config, engines, connection, maintenance, backup, migration, docs, auth

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(engines.router, prefix="/engines", tags=["engines"])
api_router.include_router(connection.router, prefix="/test-connection", tags=["connection"])
api_router.include_router(connection.history_router, prefix="/connection-history", tags=["connection"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"])
api_router.include_router(migration.router, prefix="/migration", tags=["migration"])
api_router.include_router(docs.router, prefix="/docs", tags=["docs"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
