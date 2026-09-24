import json
import hashlib
import zipfile 
import io
from pathlib import Path
from datetime import datetime, timezone
from fastapi import HTTPException, status, UploadFile
from app.config import settings
from app.core.logging_config import logger
from app.models.documento import Documento, TipoDocumentoEnum, DocumentoAtualizacao

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


def buscar_documento_por_id(identificador: int) -> dict:
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

    conteudo = await arquivo.read()
    tamanho_bytes = len(conteudo)
    if tamanho_bytes > TAMANHO_MAXIMO_MB * 1024 * 1024:
        logger.warning("Tentativa de upload excedendo o limite: %s MB", TAMANHO_MAXIMO_MB)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo excede o limite de {TAMANHO_MAXIMO_MB}MB."
        )

    documentos = ler_metadados()

    novo_id = max([doc.get("id", 0) for doc in documentos], default=0) + 1

    nome_original = arquivo.filename or "arquivo_sem_nome"
    nome_armazenado = f"{novo_id}_{nome_original}"
    caminho_fisico = DIRETORIO_DOCUMENTOS / nome_armazenado

    try:
        with open(caminho_fisico, "wb") as buffer:
            buffer.write(conteudo)
    except Exception as erro:
        logger.error("Falha ao salvar arquivo físico: %s", erro)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao armazenar o arquivo fisicamente."
        )

    extensao = Path(nome_original).suffix.replace(".", "").lower()

    tipo_mime = arquivo.content_type or "application/octet-stream"

    sha256_hash = hashlib.sha256(conteudo).hexdigest()

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


def obter_caminho_arquivo(identificador: int) -> dict:
    documento = buscar_documento_por_id(identificador)

    caminho_arquivo = DIRETORIO_DOCUMENTOS / documento["nome_armazenado"]

    if not caminho_arquivo.exists():
        logger.error("Arquivo não está no storage: %s", caminho_arquivo)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="O arquivo não foi encontrado")

    logger.info("Download: id=%s, nome_origial=%s", identificador, documento["nome_original"])


    return {
        "caminho": caminho_arquivo,
        "nome_original": documento["nome_original"],
        "tipo_mime": documento["tipo_mime"]
    }
         

def gerar_zip_funcionario(funcionario: str) -> io.BytesIO:
    documentos = listar_documentos_servico()
    documentos_funcionario = [
        documento
        for documento in documentos
        if documento["funcionario"].strip().casefold() == funcionario.strip().casefold()
    ]

    if not documentos_funcionario:
        logger.warning("Nenhum documento encontrado para o funcionário: %s", funcionario)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum documento encontrado para esse funcionário."
        )

    buffer_zip = io.BytesIO()
    arquivos_adicionados = 0

    with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for doc in documentos_funcionario:
            caminho_arquivo = DIRETORIO_DOCUMENTOS / doc["nome_armazenado"]
            if caminho_arquivo.exists():
                nome_no_zip = f'{doc["id"]}_{doc["nome_original"]}'
                zipf.write(caminho_arquivo, arcname=nome_no_zip)
                arquivos_adicionados += 1
            else:
                logger.warning("Arquivo físico ausente ao gerar ZIP: %s", caminho_arquivo)

    if arquivos_adicionados == 0:
        logger.error("Nenhum arquivo físico encontrado para gerar ZIP do funcionário: %s", funcionario)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Os documentos desse funcionário não foram encontrados no storage."
        )

    buffer_zip.seek(0)
    logger.info("ZIP gerado para funcionário=%s com %s arquivo(s)", funcionario, arquivos_adicionados)

    return buffer_zip

def atualizar_documento_servico(identificador: int, dados_atualizacao: DocumentoAtualizacao) -> dict:
    documentos = ler_metadados()
    
    indice_encontrado = None
    for indice, documento in enumerate(documentos):
        if documento.get("id") == identificador:
            indice_encontrado = indice
            break

    if indice_encontrado is None:
        logger.warning("Tentativa de atualizar documento inexistente: %s", identificador)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Documento não encontrado"
        )

    documento_atual = documentos[indice_encontrado]
    dados_novos = dados_atualizacao.model_dump(exclude_unset=True, mode="json")

    for campo, valor in dados_novos.items():
        documento_atual[campo] = valor

    salvar_metadados(documentos)

    logger.info("Documento atualizado: id=%s, campos=%s", identificador, list(dados_novos.keys()))

    return documento_atual