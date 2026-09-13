from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from app.models.documento import Documento, TipoDocumentoEnum
from app.services.documento_servico import (
    listar_documentos_servico,
    buscar_documento_por_id_servico,
    criar_documento_servico,
)

router = APIRouter(prefix="/documentos", tags=["Documentos"])


@router.post("", response_model=Documento, status_code=status.HTTP_201_CREATED)
async def criar_documento(
    arquivo: UploadFile = File(..., description="Arquivo a ser enviado"),
    funcionario: str = Form(...),
    setor: str = Form(...),
    tipo_de_documento: TipoDocumentoEnum = Form(...),
    competencia_m_a: str = Form(...),
    descricao: str = Form(...)
):
    return await criar_documento_servico(
        arquivo=arquivo,
        funcionario=funcionario,
        setor=setor,
        tipo_de_documento=tipo_de_documento,
        competencia_m_a=competencia_m_a,
        descricao=descricao
    )


@router.get("", response_model=list[Documento])
def listar_documentos():
    return listar_documentos_servico()


@router.get("/{id}", response_model=Documento)
def buscar_documento_por_id(id: int):
    return buscar_documento_por_id_servico(id)