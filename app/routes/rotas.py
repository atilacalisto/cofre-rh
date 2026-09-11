from fastapi import APIRouter, HTTPException, status
from app.models.documento import Documento
from app.services.documento_servico import (
    listar_documentos_servico,
    buscar_documento_por_id_servico,
    criar_documento_servico,
)

router = APIRouter(prefix="/documentos", tags=["Documentos"])


@router.post("", response_model=Documento, status_code=201)
def criar_documento(documento: Documento):
    return criar_documento_servico(documento)


@router.get("", response_model=list[Documento])
def listar_documentos():
    return listar_documentos_servico()


@router.get("/{id}", response_model=Documento)
def buscar_documento_por_id(id: int):
    return buscar_documento_por_id_servico(id)