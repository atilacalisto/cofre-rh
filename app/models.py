from datetime import datetime 
from enum import Enum
from pydantic import BaseModel, Field


# Padronização dos tipos de documento de RH - assim eu nao preciso colocar dados misturados (como atestado e contrato na mesma base, fica melhoe pra organizae)
class TipoDocumentoEnum(str, Enum):
    ATESTADO = "Atestado"
    HOLERITE = "Holerite"
    CONTRATO = "Contrato"
    TERMO_RESCISAO = "Termo de Rescisão"
    FERIAS = "Aviso de Férias"
    OUTRO = "Outro"


class Documento(BaseModel):
    #como os dados vao ser vistos no swagger(atila 14:44)
    id: int 
    nome_original: str
    nome_armazenado: str
    extensao: str
    tipo_mime: str       
    tamanho: int 
    descricao: str        
    data_upload: datetime 
    sha256: str

    # Dados de Recursos Humanos (Todos OBRIGATÓRIOS - não mude, deixei todos eles obrigatorios)
    funcionario: str = Field(..., description="Nome do Funcionário")
    setor: str = Field(..., description="Setor de alocação")
    tipo_de_documento: TipoDocumentoEnum = Field(..., description="Tipo do Documento")
    competencia_m_a: str = Field(..., description="Mês/Ano de referência (ex: 08/2026)")