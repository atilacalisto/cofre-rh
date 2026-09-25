from fastapi import APIRouter, status, UploadFile, File, Form
from app.models.models import Documento, TipoDocumentoEnum, DocumentoAtualizacao
from fastapi.responses import FileResponse, StreamingResponse
from urllib.parse import quote
from app.services.servico import (
    listar_documentos_servico,
    buscar_documento_por_id as buscar_documento_por_id_servico,
    criar_documento_servico,
    obter_caminho_arquivo,
    gerar_zip_funcionario,
    atualizar_documento_servico,
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


@router.get("/{documento_id}", response_model=Documento)
def buscar_documento_por_id(documento_id: int):
    return buscar_documento_por_id_servico(documento_id)

@router.get("/{id}/download_arquivo")
def download_arquivo(id: int):
    info = obter_caminho_arquivo(id)

    return FileResponse(
        path=info["caminho"],
        filename=info["nome_original"],
        media_type=info["tipo_mime"]
    )


@router.get("/funcionario/{funcionario}/zip")
def download_zip_funcionario(funcionario: str):
    buffer_zip = gerar_zip_funcionario(funcionario)
    nome_arquivo = quote(f"documentos_{funcionario}.zip")

    return StreamingResponse(
        buffer_zip,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{nome_arquivo}"}
    )

@router.put("/{documento_id}", response_model=Documento)
def atualizar_documento(documento_id: int, dados_atualizacao: DocumentoAtualizacao):
    return atualizar_documento_servico(documento_id, dados_atualizacao)