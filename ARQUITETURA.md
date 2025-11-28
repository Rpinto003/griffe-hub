# 📐 Arquitetura do Griffe Hub

## Visão Geral

O Griffe Hub é um sistema modular que centraliza diversas ferramentas operacionais da Griffe Turismo. A arquitetura segue o padrão frontend/backend com separação clara de responsabilidades.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      GRIFFE HUB                              │
│                   (Sistema Central)                          │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
          ▼                                   ▼
┌────────────────────┐              ┌────────────────────┐
│     FRONTEND       │              │     BACKEND        │
│    (Streamlit)     │◄────────────►│  (Python Logic)    │
└────────────────────┘              └────────────────────┘
          │                                   │
          │                                   │
┌─────────┴──────────┐         ┌──────────────┴─────────────┐
│                    │         │                            │
│  Hub Principal     │         │  Módulos:                  │
│  ├─ Passaportes    │         │  ├─ passaportes/          │
│  ├─ Extrator       │         │  │  ├─ data_processor.py  │
│  └─ Dashboard      │         │  │  └─ automation.py      │
│                    │         │  │                         │
│  Componentes:      │         │  ├─ extrator_faturas/     │
│  ├─ sidebar        │         │  │  └─ extractor.py       │
│  ├─ header         │         │  │                         │
│  └─ utils          │         │  └─ shared/               │
│                    │         │     └─ utils.py            │
└────────────────────┘         └────────────────────────────┘
          │                                   │
          │                                   │
          └───────────────┬───────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │      DATA       │
                 │                 │
                 │  ├─ uploads/   │
                 │  ├─ processed/ │
                 │  └─ temp/      │
                 └─────────────────┘
```

## Componentes Principais

### 1. Frontend (Streamlit)

**Responsabilidades:**
- Interface do usuário
- Validação de entrada
- Visualização de dados
- Navegação entre módulos

**Arquivos:**
```
frontend/
├── streamlit_app.py      # Hub central
├── pages/
│   ├── 1_Passaportes.py
│   └── 2_Extrator_Faturas.py
└── components/
    └── (componentes reutilizáveis)
```

### 2. Backend (Python)

**Responsabilidades:**
- Lógica de negócio
- Processamento de dados
- Automação
- Integração com APIs externas

**Arquivos:**
```
backend/
├── config.py              # Configurações centralizadas
├── passaportes/
│   ├── data_processor.py  # Normalização de dados
│   └── automation.py      # Selenium automation
├── extrator_faturas/
│   └── extractor.py       # Extração de PDFs
└── shared/
    └── utils.py           # Funções compartilhadas
```

### 3. Camada de Dados

**Responsabilidades:**
- Armazenamento temporário
- Cache de uploads
- Arquivos processados

**Estrutura:**
```
data/
├── uploads/      # Arquivos enviados pelo usuário
├── processed/    # Arquivos após processamento
└── temp/         # Arquivos temporários
```

## Fluxo de Dados

### Extrator de Faturas

```
1. Upload PDF (Frontend)
   └─> bytes do arquivo
   
2. Processamento (Backend)
   └─> extractor.processar_pdf()
       ├─ Extrai texto do PDF
       ├─ Identifica fatura
       ├─ Localiza passageiros
       ├─ Extrai dados de voos
       └─ Retorna DataFrame
   
3. Visualização (Frontend)
   └─> DataFrame → Excel download
```

### Sistema de Passaportes

```
1. Upload Excel (Frontend)
   └─> DataFrame bruto
   
2. Normalização (Backend)
   └─> ProcessadorDados.normalizar()
       ├─ Mapeia colunas
       ├─ Limpa dados
       └─ Retorna DataFrame normalizado
   
3. Automação (Backend)
   └─> AutomacaoPassaporte.preencher_formulario()
       ├─ Inicializa navegador
       ├─ Acessa site PF
       ├─ Preenche campos
       └─> Retorna status
   
4. Relatório (Frontend)
   └─> Estatísticas e download
```

## Padrões de Código

### Nomenclatura

- **Arquivos**: snake_case (ex: `data_processor.py`)
- **Classes**: PascalCase (ex: `ProcessadorDados`)
- **Funções**: snake_case (ex: `processar_pdf()`)
- **Constantes**: UPPER_CASE (ex: `MAX_VOOS`)

### Estrutura de Módulos

Cada módulo do backend segue esta estrutura:

```python
modulo/
├── __init__.py         # Exporta APIs públicas
├── processor.py        # Lógica de processamento
├── models.py          # Modelos de dados (se necessário)
└── utils.py           # Funções auxiliares
```

### Tratamento de Erros

```python
try:
    # Operação
    resultado = processar_dados(dados)
    logger.info("Sucesso")
    return resultado
except Exception as e:
    logger.error(f"Erro: {str(e)}")
    raise
```

### Logging

Todos os módulos backend devem usar logging:

```python
from backend.shared.utils import setup_logger

logger = setup_logger(__name__)

logger.info("Iniciando processamento")
logger.warning("Aviso")
logger.error("Erro crítico")
```

## Configurações

### Variáveis de Ambiente (.env)

```env
# Aplicação
APP_NAME=Griffe Hub
ENVIRONMENT=development

# Paths
DATA_PATH=./data
LOGS_PATH=./logs

# Módulos
PASSAPORTES_URL=https://...
FATURAS_PASTA_PDFS=./data/uploads

# Logs
LOG_LEVEL=INFO
```

### Configuração Central (config.py)

```python
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"

APP_NAME = os.getenv("APP_NAME", "Griffe Hub")
```

## Extensibilidade

### Adicionar Novo Módulo

1. **Criar estrutura backend:**
```bash
backend/novo_modulo/
├── __init__.py
├── processor.py
└── models.py
```

2. **Criar página frontend:**
```bash
frontend/pages/3_Novo_Modulo.py
```

3. **Adicionar ao hub:**
```python
# streamlit_app.py
if st.button("Abrir Novo Módulo"):
    st.switch_page("pages/3_Novo_Modulo.py")
```

4. **Importar no frontend:**
```python
# pages/3_Novo_Modulo.py
from novo_modulo.processor import Processador
```

## Dependências

### Core
- streamlit: Interface web
- pandas: Manipulação de dados
- pdfplumber: Extração de PDFs

### Automação
- selenium: Automação web
- webdriver-manager: Gerenciamento de drivers

### Utilitários
- python-dotenv: Variáveis de ambiente
- xlsxwriter: Geração de Excel

## Segurança

### Dados Sensíveis

- ❌ Nunca commitar arquivos .env
- ❌ Nunca commitar dados de usuários
- ✅ Usar .gitignore para excluir dados
- ✅ Logs não devem conter dados sensíveis

### Validação de Entrada

- Sempre validar uploads
- Limitar tamanho de arquivos
- Verificar tipos de arquivo
- Sanitizar nomes de arquivo

## Performance

### Otimizações

1. **Cache de dados:**
```python
@st.cache_data
def processar_dados_pesados(dados):
    # ...
```

2. **Processamento em lote:**
```python
df_final = pd.concat(all_dataframes, ignore_index=True)
```

3. **Lazy loading:**
```python
if processamento_necessario:
    resultado = processar()
```

## Monitoramento

### Logs

Todos os logs são salvos em `logs/app.log`:

```
2025-11-06 10:30:15 - extractor - INFO - Processando fatura_01.pdf
2025-11-06 10:30:20 - extractor - INFO - Extraídos 50 passageiros
2025-11-06 10:30:21 - extractor - INFO - Processo concluído
```

### Métricas

- Número de processos por dia
- Taxa de sucesso/erro
- Tempo médio de processamento

## Documentação

### Docstrings

```python
def processar_pdf(pdf_bytes: bytes, nome_arquivo: str) -> pd.DataFrame:
    """
    Processa um PDF de fatura e retorna DataFrame com dados extraídos
    
    Args:
        pdf_bytes: Bytes do arquivo PDF
        nome_arquivo: Nome do arquivo para referência
    
    Returns:
        DataFrame com dados extraídos
        
    Raises:
        ValueError: Se PDF inválido
        ProcessingError: Se erro no processamento
    """
```

## Manutenção

### Atualização de Dependências

```bash
pip install --upgrade -r requirements.txt
```

### Testes

```bash
pytest tests/
```

### Backup

- Fazer backup regular da pasta `data/`
- Versionar mudanças no código
- Manter logs por período definido

## Roadmap

### v1.1 (Planejado)
- [ ] Dashboard Analytics
- [ ] Integração com banco de dados
- [ ] API REST
- [ ] Autenticação de usuários

### v2.0 (Futuro)
- [ ] Deploy em cloud
- [ ] Múltiplos tenants
- [ ] Mobile app
- [ ] IA/ML para previsões

---

**Versão da Documentação:** 1.0  
**Última Atualização:** Novembro 2025  
**Mantenedor:** Equipe Griffe Turismo
