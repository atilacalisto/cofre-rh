from fastapi import FastAPI
from app.routes.rotas import roteador_documentos

app = FastAPI(
    title="COFRE DIGITAL - SETOR: RECURSOS HUMANOS",
    description="Gerenciamento de documentos do setor de recursos humanos"
)

app.include_router(roteador_documentos)


@app.get("/")
def test():
    return {"status": "online", "projeto": "Cofre RH"}