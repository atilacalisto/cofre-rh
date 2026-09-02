import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.config import settings
from app.models import Documento


app = FastAPI(
    title="COFRE DIGITAL - SETOR RH", description="Gerenciamento de documentos do setor de recursos humanos"
)

DIRETORIO_METADADOS = Path(settings["storage"]["diretorio_metadata"])
ARQUIVO_METADADOS = DIRETORIO_METADADOS / "documentos.json"


def ler_metadados() -> list[dict]:
    if not ARQUIVO_METADADOS.exists():
        return[]

    with open(ARQUIVO_METADADOS, "r", encoding="utf-8") as arquivo: 
        try: 
            return json.load(arquivo)
        except json.JSONDecodeError:
            return []

def salvar_metadados(dados: list[dict]) -> None: 
    #aqui ele vai garantor a exitencia do diretorio 
    DIRETORIO_METADADOS.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_METADADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4 , ensure_ascii=False)



# --- REQUISITO F1: Cadastrar Metadados do Documento ---
@app.post("/documentos", response_model=Documento, status_code=201)
def criar_documento(documento: Documento):
    """Cadastra os metadados de um novo documento no arquivo de persistência."""
    documentos = ler_metadados()

    for item in documentos:
        if item.get("id") == documento.id:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um documento cadastrado com o ID {documento.id}."
            )

    # mode="json" converte datas (datetime/date) em textos formatados no padrão ISO
    novo_documento = documento.model_dump(mode="json")
    documentos.append(novo_documento)
    salvar_metadados(documentos)

    return documento

#requisito 2 - listar os documentos 
@app.get("/documentos", response_model=list[Documento])
def listar_documentos():
    return ler_metadados() 


#pt para buscar o arquivo por id
@app.get("/documento/{id}", response_model=Documento)
def buscar_documento_porID(id:int):
    documentos = ler_metadados()

    for documento in documentos: 
        if documento.get("id") == id: 
            return documento

    raise HTTPException(status_code=404, detail="Documento não encontrado")
