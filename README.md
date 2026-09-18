# Cofre Digital de Arquivos — Setor: Recursos Humanos (cofre-rh)

Trabalho Prático 1 da disciplina **QXD0099 — Desenvolvimento de Software para Persistência**, UFC Campus Quixadá, com o professor Francisco Victor da Silva Pinheiro.

## Descrição

O **cofre-rh** é uma API desenvolvida em **Python** com **FastAPI** para gerenciamento de documentos do setor de Recursos Humanos de uma empresa. O sistema permite o upload, consulta, atualização, remoção e backup de documentos, além de manter metadados específicos do domínio de RH.


## Funcionalidades

O sistema implementa os seguintes requisitos funcionais (F1–F17):

| Código | Funcionalidade |
|--------|----------------|
| F1 | Upload de arquivo |
| F2 | Listagem de documentos |
| F3 | Consulta de documento por ID |
| F4 | Consulta/filtragem de documentos |
| F5 | Download de documento |
| F6 | Atualização de documento |
| F7 | Remoção de documento |
| F8 | Verificação de integridade (hash SHA-256) |
| F9/F10 | Backup |
| F11 | Sistema de logging estruturado |
| F12 | Configuração via arquivo YAML |
| F13 | Filtros avançados |
| F14/F15 | Estatísticas |
| F16 | Exportação para CSV |
| F17 | Geração de ZIP com todos os documentos de um funcionário |

## Tecnologias utilizadas

- Python 3
- FastAPI
- Pydantic
- PyYAML
- `logging` (dictConfig)

## Estrutura do projeto

```
cofre-rh/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── core/
│   │   └── logging_config.py
│   ├── routes/
│   └── services/
│       └── documento_servico.py
├── storage/
│   ├── metadata/
│   │   └── documentos.json
│   └── logs/
├── config.yaml
├── logging.yaml
├── requirements.txt
├── .gitignore
└── README.md
```

## Configuração

O projeto utiliza dois arquivos de configuração na raiz:

- **`config.yaml`**: parâmetros de armazenamento, upload e logging (`storage.*`, `upload.*`, `logging.arquivo`, `logging.nivel`).
- **`logging.yaml`**: configuração do sistema de logs, carregada separadamente via `dictConfig`, para facilitar a manutenção por toda a equipe.

## Instalação e execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/atilacalisto/cofre-rh
   cd cofre-rh
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Acesse a documentação interativa (Swagger UI) em:
   ```
   http://localhost:8000/docs
   ```
