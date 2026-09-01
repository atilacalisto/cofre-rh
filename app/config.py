"""
Carrega o arquivo de configuração externo (config.yaml) e disponibiliza
seus valores para o resto da aplicação (F12 — Arquivo de Configuração).

Uso em outros módulos:
    from app.config import settings
    print(settings["storage"]["diretorio_documentos"])
"""

from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def carregar_configuracao(caminho: Path = CONFIG_PATH) -> dict:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {caminho}")
    with open(caminho, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Configuração carregada uma única vez, na importação do módulo.
settings = carregar_configuracao()
