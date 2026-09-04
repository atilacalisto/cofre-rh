import json
from pathlib import Path
from fastapi import HTTPException
from app.config import settings
from app.models.documento import Documento

DIRETORIO_METADADOS = Path(settings["storage"]["diretorio_metadata"])
ARQUIVO_METADADOS = DIRETORIO_METADADOS / "documentos.json"


def ler_metadados() -> list[dict]:
    if not ARQUIVO_METADADOS.exists():
        return []
    with open(ARQUIVO_METADADOS, "r", encoding="utf-8") as arquivo:
        try:
            return json.load(arquivo)
        except json.JSONDecodeError:
            return []


def salvar_metadados(dados: list[dict]) -> None:
    DIRETORIO_METADADOS.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_METADADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def listar_documentos_servico() -> list[dict]:
    return ler_metadados()


def buscar_documento_por_id_servico(identificador: int) -> dict:
    documentos = ler_metadados()
    for documento in documentos:
        if documento.get("id") == identificador:
            return documento
    raise HTTPException(status_code=404, detail="Documento não encontrado")


def criar_documento_servico(documento: Documento) -> dict:
    documentos = ler_metadados()
    for item in documentos:
        if item.get("id") == documento.id:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um documento cadastrado com o ID {documento.id}."
            )
    novo_documento = documento.model_dump(mode="json")
    documentos.append(novo_documento)
    salvar_metadados(documentos)
    return novo_documento