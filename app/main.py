from fastapi import FastAPI
from app.routes.rotas import router
from app.core.logging_config import logger

app = FastAPI(
    title="COFRE DIGITAL - SETOR: RECURSOS HUMANOS",
    description="Gerenciamento de documentos do setor de recursos humanos"
)

app.include_router(router)
