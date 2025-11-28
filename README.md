# 🏢 Griffe Hub

Sistema centralizado de soluções operacionais da Griffe Turismo.

## 📋 Descrição

O Griffe Hub é uma plataforma que centraliza diversas ferramentas operacionais:

- **🛂 Sistema de Passaportes**: Automação de preenchimento de formulários
- **✈️ Extrator de Faturas**: Extração automática de dados de faturas OFB
- **📊 Dashboard**: Visualização e análise de dados (em desenvolvimento)

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd Griffe_Hub
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

## 🎯 Uso

### Iniciar a aplicação

```bash
python run.py
```

Ou diretamente com Streamlit:
```bash
streamlit run frontend/streamlit_app.py
```

A aplicação estará disponível em: http://localhost:8501

## 📁 Estrutura do Projeto

```
Griffe_Hub/
├── frontend/                # Interface Streamlit
│   ├── streamlit_app.py    # Aplicação principal (hub)
│   ├── pages/              # Páginas do sistema
│   ├── components/         # Componentes reutilizáveis
│   └── assets/             # Recursos estáticos
│
├── backend/                # Lógica de negócio
│   ├── passaportes/        # Módulo de passaportes
│   ├── extrator_faturas/   # Módulo extrator
│   └── shared/             # Código compartilhado
│
├── data/                   # Dados e arquivos
│   ├── uploads/           # Arquivos enviados
│   ├── processed/         # Arquivos processados
│   └── temp/              # Temporários
│
└── logs/                   # Logs da aplicação
```

## 🔧 Funcionalidades

### Sistema de Passaportes

- Upload de planilhas Excel com dados dos solicitantes
- Normalização automática de dados
- Preenchimento automatizado de formulários
- Relatórios de processamento

### Extrator de Faturas

- Upload de PDFs de faturas OFB
- Extração automática de:
  - Dados de passageiros
  - Informações de voos
  - Valores e taxas
- Exportação para Excel

## 📝 Desenvolvimento

### Adicionar Nova Funcionalidade

1. Crie o módulo em `backend/`
2. Crie a página em `frontend/pages/`
3. Adicione a navegação em `streamlit_app.py`

### Testes

```bash
pytest tests/
```

## 🤝 Contribuindo

1. Crie uma branch para sua feature
2. Faça commit das mudanças
3. Push para a branch
4. Abra um Pull Request

## 📞 Suporte

- **Email**: suporte@griffe.com.br
- **Telefone**: (71) 3341-5100

## 📄 Licença

© 2025 Griffe Turismo - Todos os direitos reservados

## 🔄 Versões

- **v1.0.0** (Atual)
  - Sistema de Passaportes
  - Extrator de Faturas
  - Hub Central
