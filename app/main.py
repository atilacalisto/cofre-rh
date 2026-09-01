#somente coloque as bibliotecas, não remova nenhuma dessas 
import json
from  pathlib import Path 
from fastapi import FastAPI, HTTPException
from app.config import settings # essa biblioteca aqui vai importar o dicionario com as congig do config.yaml (r12)


app = FastAPI(
    title = "COFRE DIGITAL - SETOR: RECURSOS HUMANOS", description = "Gerenciamento de documentos do setor de recursos humanos"

)


#aqui ele vai extrair o caminho da pasta de metadados diretamente da config externa 
METADATA_DIR = Path(settings["storage"]["diretorio_metadata"])


#aqui ele vai definir o caminho completo apontado para o arquivo 'documentos.json'
METADATA_FILE = METADATA_DIR /'documentos.json'


def ler_metadados() -> list[dict]: #aqui ele infica que  a funcao sempre vai retornar uma lista de dicionarios, onde cada dicionario representa um documento
    if not METADATA_FILE.exists():
        return [] #aqui antes de abrir o arquivo ele chega se realmente ele existe, se o arquivi não tiver sido criado ele retorna uma lista vazia ao invez de inrerromper a execução com um erro

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        try:
            conteudo = file.read().strip()
            if not conteudo:
                return []

            return json.loads(conteudo)
        except json.JSONDecodeError:
            return []
        
            

@app.get("/")
def test():
    return{"test": "funcionou"}
        