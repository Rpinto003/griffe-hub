# 🚀 Guia de Início Rápido - Griffe Hub

## Instalação

### 1. Clonar/Baixar o Projeto

Certifique-se de que você tem a pasta `Griffe_Hub` completa com todos os arquivos.

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

## Executar a Aplicação

### Método 1: Script run.py (Recomendado)

```bash
python run.py
```

### Método 2: Streamlit Direto

```bash
streamlit run frontend/streamlit_app.py
```

A aplicação abrirá no navegador em: `http://localhost:8501`

## Estrutura do Projeto

```
Griffe_Hub/
├── frontend/              # Interface Streamlit
│   ├── streamlit_app.py  # Página principal (Hub)
│   └── pages/            # Páginas das aplicações
│       ├── 1_Passaportes.py
│       └── 2_Extrator_Faturas.py
│
├── backend/              # Lógica de negócio
│   ├── passaportes/     # Módulo de passaportes
│   │   ├── data_processor.py
│   │   └── automation.py
│   │
│   ├── extrator_faturas/ # Módulo extrator
│   │   └── extractor.py
│   │
│   └── shared/           # Código compartilhado
│       └── utils.py
│
└── data/                 # Dados da aplicação
    ├── uploads/         # Arquivos enviados
    ├── processed/       # Arquivos processados
    └── temp/           # Temporários
```

## Usar as Aplicações

### Sistema de Passaportes

1. Acesse a página "Passaportes" pelo menu
2. Faça upload de uma planilha Excel com dados dos solicitantes
3. Clique em "Normalizar Dados"
4. Na aba "Preenchimento", você pode:
   - Visualizar dados de cada solicitante
   - Executar automação (requer Selenium)
   - Marcar como concluído
5. Na aba "Relatório", veja estatísticas do processamento

**Formato da Planilha:**
- Colunas aceitas: nome, cpf, rg, data_nascimento, nome_mae, nome_pai, etc.
- O sistema reconhece variações nos nomes das colunas

### Extrator de Faturas

1. Acesse a página "Extrator de Faturas" pelo menu
2. Faça upload de um ou mais arquivos PDF de faturas OFB
3. Clique em "Processar Faturas"
4. Visualize os dados extraídos
5. Baixe a planilha Excel com os resultados

**Dados Extraídos:**
- Informações da fatura (número, data)
- Dados dos passageiros
- E-tickets e localizadores
- Informações de voos
- Tarifas e taxas

## Configuração

Edite o arquivo `.env` para personalizar configurações:

```env
APP_NAME=Griffe Hub
ENVIRONMENT=development
PASSAPORTES_URL=https://servicos.dpf.gov.br/sinpa/inicializacaoSolicitacao.do
LOG_LEVEL=INFO
```

## Solução de Problemas

### Erro: "Módulo backend não encontrado"

**Solução:** Certifique-se de que está executando a partir da raiz do projeto e que a estrutura de pastas está correta.

### Erro ao processar PDF

**Solução:** Verifique se o PDF está no formato correto (fatura OFB) e não está corrompido.

### Selenium não funciona

**Solução:** 
1. Instale o Chrome atualizado
2. Execute: `pip install selenium webdriver-manager`
3. Certifique-se de ter conexão com internet (para baixar chromedriver)

### Aplicação não abre

**Solução:**
1. Verifique se a porta 8501 está livre
2. Tente especificar outra porta: `streamlit run frontend/streamlit_app.py --server.port=8502`

## Próximos Passos

### Desenvolver Automação de Passaportes

O arquivo `backend/passaportes/automation.py` contém um template básico. Para implementar:

1. Analise o site da Polícia Federal
2. Identifique os seletores (IDs, classes) dos campos
3. Implemente a lógica de preenchimento no método `preencher_formulario()`

### Adicionar Nova Funcionalidade

1. Crie um módulo em `backend/nome_modulo/`
2. Crie uma página em `frontend/pages/3_Nome_Modulo.py`
3. Adicione link na página principal

## Suporte

- **Email:** suporte@griffe.com.br
- **Telefone:** (71) 3341-5100

## Licença

© 2025 Griffe Turismo - Todos os direitos reservados
