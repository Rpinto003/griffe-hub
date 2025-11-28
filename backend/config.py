# -*- coding: utf-8 -*-
"""
Griffe Hub - Configurações Centralizadas
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Paths do projeto
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Subpastas de dados
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
TEMP_DIR = DATA_DIR / "temp"

# Criar diretórios se não existirem
for directory in [DATA_DIR, LOGS_DIR, UPLOADS_DIR, PROCESSED_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configurações da aplicação
APP_NAME = os.getenv("APP_NAME", "Griffe Hub")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Configurações de Passaportes
PASSAPORTES_URL = os.getenv(
    "PASSAPORTES_URL",
    "https://servicos.dpf.gov.br/sinpa/inicializacaoSolicitacao.do"
)

# Configurações de Extrator de Faturas
FATURAS_PASTA_PDFS = Path(os.getenv("FATURAS_PASTA_PDFS", str(UPLOADS_DIR)))
MAX_VOOS = 8

# Configurações de Logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# Padrões de extração de PDF
MONEY_PT = r'(?:\d{1,3}(?:\.\d{3})*,\d{2})'
TIME_HM = r'(?:\d{2}:\d{2})'
