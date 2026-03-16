#!/usr/bin/env python3
"""
Database Backend API
====================
API FastAPI modularizada para gerenciamento de bancos de dados

Versão: 2.0.2
"""

import traceback
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.config import settings, logger
from app.api import api_router
from app.middleware.rate_limit import RateLimitMiddleware


def create_application() -> FastAPI:
    """Factory para criar aplicação FastAPI"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="API para gerenciamento de múltiplos motores de banco de dados",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Rate Limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=60
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # Rotas
    app.include_router(api_router, prefix="/api")
    
    # Rota raiz
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
            "environment": settings.ENVIRONMENT
        }
    
    # Handler para ValidationError do Pydantic
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Dados inválidos",
                "errors": exc.errors()
            }
        )
    
    # Handler de erros global
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log completo do erro com traceback
        logger.error(f"Erro não tratado: {exc}")
        logger.error(traceback.format_exc())
        
        # Não expor detalhes internos em produção
        if settings.ENVIRONMENT == "production":
            message = "Erro interno do servidor"
        else:
            message = f"Erro interno: {str(exc)}"
        
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": message}
        )
    
    return app


# Criar aplicação
app = create_application()


if __name__ == "__main__":
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
