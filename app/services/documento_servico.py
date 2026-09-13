import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from fastapi import HTTPException, status, UploadFile
from app.config import settings
from app.core.logging_config import logger
from app.models.documento import Documento, TipoDocumentoEnum

DIRETORIO_METADADOS = Path(settings["storage"]["diretorio_metadata"])
ARQUIVO_METADADOS = DIRETORIO_METADADOS / "documentos.json"
DIRETORIO_DOCUMENTOS = Path(settings["storage"]["diretorio_documentos"])
TAMANHO_MAXIMO_MB = settings["upload"]["tamanho_maximo_mb"]

def _garantir_diretorios() -> None:
    DIRETORIO_METADADOS.mkdir(parents=True, exist_ok=True)
    DIRETORIO_DOCUMENTOS.mkdir(parents=True, exist_ok=True)


def ler_metadados() -> list[dict]:
    _garantir_diretorios()
    if not ARQUIVO_METADADOS.exists():
        return []
    try:
         with open(ARQUIVO_METADADOS, "r", encoding="utf-8") as arquivo:
                    return json.load(arquivo)
    except json.JSONDecodeError as erro:
         logger.error("JSON inválido em %s: %s", ARQUIVO_METADADOS.name, erro)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: O arquivo de metadados está corrompido.")


def salvar_metadados(dados: list[dict]) -> None:
    _garantir_diretorios()
    with open(ARQUIVO_METADADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)
    logger.debug("Arquivo %s atualizado com %s registros.", ARQUIVO_METADADOS.name, len(dados))


def listar_documentos_servico() -> list[dict]:
    return ler_metadados()


def buscar_documento_por_id_servico(identificador: int) -> dict:
    documentos = ler_metadados()
    for documento in documentos:
        if documento.get("id") == identificador:
            return documento
    logger.warning("Documento não encontrado: %s", identificador)
    raise HTTPException(status_code=404, detail="Documento não encontrado")


async def criar_documento_servico(
    arquivo: UploadFile,
    funcionario: str,
    setor: str,
    tipo_de_documento: TipoDocumentoEnum,
    competencia_m_a: str,
    descricao: str
) -> dict:
    _garantir_diretorios()

    #Validar tamanho do arquivo
    conteudo = await arquivo.read()
    tamanho_bytes = len(conteudo)
    if tamanho_bytes > TAMANHO_MAXIMO_MB * 1024 * 1024:
        logger.warning("Tentativa de upload excedendo o limite: %s MB", TAMANHO_MAXIMO_MB)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo excede o limite de {TAMANHO_MAXIMO_MB}MB."
        )

    documentos = ler_metadados()

    #Gerar identificador único
    novo_id = max([doc.get("id", 0) for doc in documentos], default=0) + 1

    #Preservar nome original e definir nome de armazenamento
    nome_original = arquivo.filename or "arquivo_sem_nome"
    #Evita sobrescrita usando o ID + nome original
    nome_armazenado = f"{novo_id}_{nome_original}"
    caminho_fisico = DIRETORIO_DOCUMENTOS / nome_armazenado

    #Armazenar fisicamente o arquivo
    try:
        with open(caminho_fisico, "wb") as buffer:
            buffer.write(conteudo)
    except Exception as erro:
        logger.error("Falha ao salvar arquivo físico: %s", erro)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao armazenar o arquivo fisicamente."
        )

    # 5. Identificar extensão
    extensao = Path(nome_original).suffix.replace(".", "").lower()

    # 6. Identificar tipo MIME
    tipo_mime = arquivo.content_type or "application/octet-stream"

    #Calcular hash SHA-256
    sha256_hash = hashlib.sha256(conteudo).hexdigest()

    #Registrar metadados no JSON
    novo_documento = Documento(
        id=novo_id,
        nome_original=nome_original,
        nome_armazenado=nome_armazenado,
        extensao=extensao,
        tipo_mime=tipo_mime,
        tamanho=tamanho_bytes,
        descricao=descricao,
        data_upload=datetime.now(timezone.utc),
        sha256=sha256_hash,
        funcionario=funcionario,
        setor=setor,
        tipo_de_documento=tipo_de_documento,
        competencia_m_a=competencia_m_a
    )

    documentos.append(novo_documento.model_dump(mode="json"))
    salvar_metadados(documentos)
    
    logger.info("Documento cadastrado: id=%s, nome_original=%s, tamanho=%s bytes", novo_id, nome_original, tamanho_bytes)

    return novo_documento.model_dump(mode="json")