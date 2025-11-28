# -*- coding: utf-8 -*-
"""
GRIFFE HUB - Sistema de Alocação de Intercâmbio Internacional

Interface Streamlit para alocação automática de estudantes em escolas,
mantendo coesão de grupos sempre que possível.

VERSÃO 2.0 - Com features de agrupamento por nome e dispersão por cidade
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import io

# ============================================================================
# CONFIGURAÇÃO E IMPORTS
# ============================================================================

# Adicionar pasta backend ao path
BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

# Importar o algoritmo do backend
try:
    from alocacao.algorithm import (
        alocar_estudantes,
        calcular_capacidades_por_sexo,
        SCORE_PRIMEIRA_ESCOLA,
        SCORE_MESMA_REGIAO,
        SCORE_OUTRA_REGIAO,
    )
    BACKEND_DISPONIVEL = True
except ImportError:
    BACKEND_DISPONIVEL = False
    # Valores padrão para compatibilidade
    SCORE_PRIMEIRA_ESCOLA = -1000.0
    SCORE_MESMA_REGIAO = -500.0
    SCORE_OUTRA_REGIAO = 3.0

# Configuração da página
st.set_page_config(
    page_title="Alocação de Alunos - Griffe Hub",
    page_icon="✈️",
    layout="wide"
)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def calcular_idade(data_nascimento):
    """Calcula idade a partir da data de nascimento."""
    if pd.isna(data_nascimento):
        return 0
    
    hoje = datetime.now()
    
    if isinstance(data_nascimento, str):
        try:
            data_nasc = pd.to_datetime(data_nascimento, format='%d/%m/%Y', errors='coerce')
            if pd.isna(data_nasc):
                return 0
        except Exception:
            return 0
    else:
        data_nasc = data_nascimento
    
    idade = hoje.year - data_nasc.year
    if (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day):
        idade -= 1
    
    return idade


def extrair_numero_grupo(grupo_str):
    """Extrai o número do grupo (ex: 'GRUPO 01' -> 1)."""
    if pd.isna(grupo_str):
        return 0
    
    import re
    grupo_str = str(grupo_str).upper().strip()
    numeros = re.findall(r'(\d+)', grupo_str)
    
    return int(numeros[0]) if numeros and numeros[0].isdigit() else 0


def classificar_score(score: float) -> str:
    """Retorna classificação textual do score."""
    if score == SCORE_PRIMEIRA_ESCOLA:
        return "✅ Primeira escola (região principal)"
    elif score == SCORE_MESMA_REGIAO:
        return "✅ Mesma região (coesão mantida)"
    elif score == SCORE_OUTRA_REGIAO:
        return "⚠️ Outra região (quebra)"
    elif score >= 999999.0:
        return "❌ Não alocado"
    else:
        return "ℹ️ Indefinido"


def processar_planilha_alunos(df: pd.DataFrame) -> pd.DataFrame:
    """Processa e valida planilha de alunos."""
    # Padronizar nomes de colunas
    mapeamento = {
        'nome': 'Nome',
        'nome completo': 'Nome',
        'estudante': 'Nome',
        'aluno': 'Nome',
        'data de nascimento': 'Data_Nascimento',
        'data nascimento': 'Data_Nascimento',
        'sexo': 'Sexo',
        'genero': 'Sexo',
        'gênero': 'Sexo',
        'grupo': 'Grupo',
        'turma': 'Grupo',
        'cidade': 'Cidade',
        'municipio': 'Cidade',
        'município': 'Cidade',
        'restrição-i1': 'Restricao_I1',
        'restricao-i1': 'Restricao_I1',
        'restrição i1': 'Restricao_I1',
        'restricao i1': 'Restricao_I1',
        'restrição intake 1': 'Restricao_I1',
        'restricao intake 1': 'Restricao_I1',
    }
    
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns=mapeamento, inplace=True)
    
    # Validar colunas obrigatórias
    colunas_obrigatorias = ['Nome', 'Sexo', 'Grupo']
    if not all(col in df.columns for col in colunas_obrigatorias):
        raise ValueError(f"Colunas obrigatórias faltando: {colunas_obrigatorias}")
    
    # Processar campos
    if 'Data_Nascimento' in df.columns:
        df['Idade'] = df['Data_Nascimento'].apply(calcular_idade)
    else:
        df['Idade'] = 16  # Idade padrão
    
    df['Numero_Grupo'] = df['Grupo'].apply(extrair_numero_grupo)
    df['Sexo_Padrao'] = df['Sexo'].astype(str).str[0].str.upper()
    
    # Processar coluna de restrição de Intake 1
    if 'Restricao_I1' in df.columns:
        # Converter para string e normalizar
        df['Restricao_I1'] = df['Restricao_I1'].astype(str).str.strip().str.upper()
        # Considerar SIM, S, YES, Y, TRUE, 1 como restrição
        df['Tem_Restricao_I1'] = df['Restricao_I1'].isin(['SIM', 'S', 'YES', 'Y', 'TRUE', '1', 'X'])
    else:
        # Se coluna não existir, ninguém tem restrição
        df['Tem_Restricao_I1'] = False
    
    return df


def processar_planilha_escolas(df: pd.DataFrame) -> pd.DataFrame:
    """Processa e valida planilha de escolas."""
    # Padronizar nomes de colunas
    mapeamento = {
        'escola': 'Escola',
        'nome': 'Escola',
        'nome da escola': 'Escola',
        'região': 'Regiao',
        'regiao': 'Regiao',
        'area': 'Regiao',
        'jan': 'JAN',
        'intake 1': 'JAN',
        'jul': 'JUL',
        'intake 2': 'JUL',
        'f_1': 'F_1',
        'm_1': 'M_1',
        'f_2': 'F_2',
        'm_2': 'M_2',
        'f': 'F',
        'm': 'M',
        'nível mínimo': 'Nivel_Minimo'
    }
    
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns=mapeamento, inplace=True)
    
    # Validar colunas obrigatórias
    colunas_obrigatorias = ['Escola', 'JAN', 'JUL', 'Regiao']
    if not all(col in df.columns for col in colunas_obrigatorias):
        raise ValueError(f"Colunas obrigatórias faltando: {colunas_obrigatorias}")
    
    # Processar campos
    df['Numero_Regiao'] = df['Regiao'].apply(extrair_numero_grupo)
    
    if 'Nivel_Minimo' not in df.columns:
        df['Nivel_Minimo'] = 'B1'
    
    return df


# ============================================================================
# INICIALIZAÇÃO DO SESSION STATE
# ============================================================================

def inicializar_session_state():
    """Inicializa variáveis do session_state."""
    if 'df_alunos' not in st.session_state:
        st.session_state.df_alunos = None
    
    if 'df_escolas' not in st.session_state:
        st.session_state.df_escolas = None
    
    if 'resultado_alocacao' not in st.session_state:
        st.session_state.resultado_alocacao = None
    
    if 'config' not in st.session_state:
        st.session_state.config = {
            'alunos_intake1': 0,
            'ordem_grupos': [],
            'agrupar_por_nome': False,
            'dispersar_por_cidade': False,
        }


inicializar_session_state()

# ============================================================================
# INTERFACE - SIDEBAR (UPLOAD)
# ============================================================================

def renderizar_sidebar():
    """Renderiza barra lateral com upload de arquivos."""
    st.sidebar.header("📁 Upload de Dados")
    
    # Aviso se backend não está disponível
    if not BACKEND_DISPONIVEL:
        st.sidebar.error("⚠️ Módulo backend não encontrado. Verifique a estrutura de pastas.")
        return
    
    uploaded_file = st.sidebar.file_uploader(
        "Planilha Excel (abas: ACOMPANHAMENTO e ESCOLAS)",
        type=['xlsx', 'xls'],
        key='upload_planilha'
    )
    
    if uploaded_file is None:
        return
    
    # Processar upload
    try:
        xl = pd.ExcelFile(uploaded_file)
        
        # Processar aba de alunos
        if 'ACOMPANHAMENTO' not in xl.sheet_names:
            st.sidebar.error("❌ Aba 'ACOMPANHAMENTO' não encontrada.")
            return
        
        df_alunos = xl.parse('ACOMPANHAMENTO')
        df_alunos = processar_planilha_alunos(df_alunos)
        st.session_state.df_alunos = df_alunos
        
        # Processar aba de escolas
        if 'ESCOLAS' not in xl.sheet_names:
            st.sidebar.error("❌ Aba 'ESCOLAS' não encontrada.")
            return
        
        df_escolas = xl.parse('ESCOLAS')
        df_escolas = processar_planilha_escolas(df_escolas)
        st.session_state.df_escolas = df_escolas
        
        # Sucesso - mostrar informações sobre coluna Cidade
        info_cidade = ""
        if 'Cidade' in df_alunos.columns:
            info_cidade = "\n- ✅ Coluna 'Cidade' detectada"
        
        # Informação sobre restrições
        info_restricao = ""
        if 'Tem_Restricao_I1' in df_alunos.columns:
            qtd_restricoes = df_alunos['Tem_Restricao_I1'].sum()
            if qtd_restricoes > 0:
                info_restricao = f"\n- ℹ️ {qtd_restricoes} aluno(s) com restrição I1"
        
        st.sidebar.success(
            f"✅ Dados carregados:\n"
            f"- {len(df_alunos)} alunos\n"
            f"- {len(df_escolas)} escolas{info_cidade}{info_restricao}"
        )
        
    except ValueError as e:
        st.sidebar.error(f"❌ Erro de validação: {str(e)}")
        st.session_state.df_alunos = None
        st.session_state.df_escolas = None
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao processar arquivo: {str(e)}")
        st.session_state.df_alunos = None
        st.session_state.df_escolas = None


# ============================================================================
# INTERFACE - TAB 1: VISÃO GERAL
# ============================================================================

def renderizar_visao_geral(df_alunos: pd.DataFrame, df_escolas: pd.DataFrame):
    """Renderiza aba de visão geral dos dados."""
    st.header("📊 Visão Geral dos Dados")
    
    # Calcular capacidades
    vagas_f_i1, vagas_m_i1 = calcular_capacidades_por_sexo(df_escolas, 1)
    vagas_f_i2, vagas_m_i2 = calcular_capacidades_por_sexo(df_escolas, 2)
    
    # Layout em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👨‍🎓 Alunos")
        st.metric("Total de Alunos", len(df_alunos))
        
        st.write("**Distribuição por Grupo e Sexo:**")
        grupo_counts = df_alunos.groupby('Grupo')['Sexo_Padrao'].value_counts().unstack(fill_value=0)
        st.dataframe(grupo_counts, use_container_width=True)
        
        # Informações sobre restrições
        if 'Tem_Restricao_I1' in df_alunos.columns:
            qtd_restricoes = df_alunos['Tem_Restricao_I1'].sum()
            if qtd_restricoes > 0:
                st.info(f"ℹ️ **{qtd_restricoes} aluno(s)** com restrição para Intake 1 (irão para Intake 2)")
        
        # Informações sobre Cidade
        if 'Cidade' in df_alunos.columns:
            st.write("**Distribuição por Cidade (Top 5):**")
            cidade_counts = df_alunos['Cidade'].value_counts().head(5)
            st.dataframe(cidade_counts, use_container_width=True)
    
    with col2:
        st.subheader("🏫 Escolas")
        
        st.write("**Capacidade Intake 1 (Janeiro):**")
        st.metric("Total", vagas_f_i1 + vagas_m_i1, delta=f"{vagas_f_i1} F / {vagas_m_i1} M")
        
        st.write("**Capacidade Intake 2 (Julho):**")
        st.metric("Total", vagas_f_i2 + vagas_m_i2, delta=f"{vagas_f_i2} F / {vagas_m_i2} M")
        
        # Validação de capacidade
        total_vagas = vagas_f_i1 + vagas_m_i1 + vagas_f_i2 + vagas_m_i2
        if len(df_alunos) > total_vagas:
            st.error(
                f"⚠️ **ATENÇÃO:** Há {len(df_alunos) - total_vagas} alunos "
                f"a mais do que vagas disponíveis!"
            )
        else:
            st.success(f"✅ Capacidade suficiente ({total_vagas - len(df_alunos)} vagas sobrando)")


# ============================================================================
# INTERFACE - TAB 2: CONFIGURAÇÃO
# ============================================================================

def renderizar_configuracao(df_alunos: pd.DataFrame, df_escolas: pd.DataFrame):
    """Renderiza aba de configuração da alocação."""
    st.header("⚙️ Configuração da Alocação")
    
    # Calcular capacidades
    vagas_f_i1, vagas_m_i1 = calcular_capacidades_por_sexo(df_escolas, 1)
    
    config = st.session_state.config
    total_alunos = len(df_alunos)
    
    # Layout em colunas
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎯 Distribuição de Intakes")
        
        alunos_intake1 = st.number_input(
            "Quantidade desejada no Intake 1 (Janeiro)",
            min_value=0,
            max_value=total_alunos,
            value=config.get('alunos_intake1', min(total_alunos, vagas_f_i1 + vagas_m_i1)),
            help="O algoritmo respeitará a capacidade real por sexo (F/M)."
        )
        
        st.info(
            f"💡 **Dica:** Intake 1 tem capacidade para {vagas_f_i1 + vagas_m_i1} alunos "
            f"({vagas_f_i1}F / {vagas_m_i1}M)"
        )
    
    with col2:
        st.subheader("📋 Prioridade de Grupos")
        
        grupos_disponiveis = sorted(df_alunos['Grupo'].unique())
        ordem_grupos = st.multiselect(
            "Ordem de prioridade (do maior para o menor)",
            options=grupos_disponiveis,
            default=config.get('ordem_grupos', grupos_disponiveis),
            help="Grupos no topo da lista escolhem vagas primeiro."
        )
        
        if len(ordem_grupos) < len(grupos_disponiveis):
            grupos_faltando = set(grupos_disponiveis) - set(ordem_grupos)
            st.warning(f"⚠️ Grupos não incluídos: {', '.join(grupos_faltando)}")
    
    # NOVA SEÇÃO: Opções Avançadas
    st.divider()
    st.subheader("⚙️ Opções Avançadas de Alocação")
    
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        agrupar_nomes = st.checkbox(
            "🎲 Dispersar alunos por nome (ordem aleatória)",
            value=config.get('agrupar_por_nome', False),
            help="""
            Quando ativado, embaralha aleatoriamente a ordem dos alunos 
            para evitar que pessoas com mesmo nome fiquem na mesma escola.
            
            **Problema:** Planilha em ordem alfabética faz Anas ficarem juntas
            
            **Solução:** Ordem aleatória dispersa as Anas em escolas diferentes
            
            **Útil para:** Evitar concentração de nomes comuns (Ana, João, Maria)
            """
        )
    
    with col_opt2:
        dispersar_cidades = st.checkbox(
            "🌍 Dispersar alunos por cidade",
            value=config.get('dispersar_por_cidade', False),
            help="""
            Quando ativado, distribui alunos da mesma cidade em escolas 
            diferentes (dentro da mesma região).
            
            **Exemplo:** 20 alunos de Salvador serão distribuídos em várias escolas.
            
            **Útil para:** Maximizar a diversidade geográfica em cada escola.
            """
        )
    
    # Avisos de compatibilidade
    if dispersar_cidades and 'Cidade' not in df_alunos.columns:
        st.warning("⚠️ **Dispersão por cidade** requer coluna 'Cidade' na planilha de alunos. Feature será ignorada.")
    
    if agrupar_nomes and dispersar_cidades:
        st.info("ℹ️ Ambas dispersões ativas: ordem aleatória + distribuição de cidades em escolas diferentes.")
    
    # Botão para salvar
    st.markdown("---")
    col_save, col_reset = st.columns([1, 1])
    
    with col_save:
        if st.button("💾 Salvar Configurações", type="primary", use_container_width=True):
            st.session_state.config = {
                'alunos_intake1': alunos_intake1,
                'ordem_grupos': ordem_grupos,
                'agrupar_por_nome': agrupar_nomes,
                'dispersar_por_cidade': dispersar_cidades,
            }
            st.success("✅ Configurações salvas!")
            st.rerun()
    
    with col_reset:
        if st.button("🔄 Resetar para Padrão", use_container_width=True):
            st.session_state.config = {
                'alunos_intake1': min(total_alunos, vagas_f_i1 + vagas_m_i1),
                'ordem_grupos': grupos_disponiveis,
                'agrupar_por_nome': False,
                'dispersar_por_cidade': False,
            }
            st.info("↩️ Configurações resetadas!")
            st.rerun()


# ============================================================================
# INTERFACE - TAB 3: EXECUTAR ALOCAÇÃO
# ============================================================================

def renderizar_executar(df_alunos: pd.DataFrame, df_escolas: pd.DataFrame):
    """Renderiza aba de execução da alocação."""
    st.header("🎯 Executar Alocação")
    
    if not BACKEND_DISPONIVEL:
        st.error("❌ O módulo do algoritmo não está disponível. Verifique a instalação.")
        return
    
    config = st.session_state.config
    
    # Mostrar configuração atual
    st.subheader("📋 Configuração Atual")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Target Intake 1", config['alunos_intake1'])
    with col2:
        st.metric("Grupos Prioritários", len(config['ordem_grupos']))
    with col3:
        status_nome = "✅ SIM" if config.get('agrupar_por_nome') else "❌ NÃO"
        st.metric("Dispersar por Nome", status_nome)
    with col4:
        status_cidade = "✅ SIM" if config.get('dispersar_por_cidade') else "❌ NÃO"
        st.metric("Dispersar por Cidade", status_cidade)
    
    # Informações sobre o algoritmo
    with st.expander("ℹ️ Como funciona a alocação?"):
        st.markdown("""
        ### Processo de Alocação
        
        1. **Distribuição de Intakes**: Alunos são distribuídos entre Janeiro (Intake 1) e Julho (Intake 2) 
           respeitando a prioridade dos grupos e capacidade por sexo.
        
        2. **Coesão de Grupos**: O algoritmo tenta manter alunos do mesmo grupo na mesma região:
           - Primeira escola alocada define a "região principal" do grupo
           - Demais alunos tentam ir para a região principal primeiro
           - Só aloca em outra região quando não há vagas na principal
        
        3. **Opções Avançadas** (se ativadas):
           - 🎲 **Dispersão por Nome**: Ordem aleatória evita nomes iguais juntos
           - 🌍 **Dispersão por Cidade**: Alunos da mesma cidade vão para escolas diferentes
        
        4. **Scores de Qualidade**:
           - ✅ **-1000**: Primeira escola (define região principal)
           - ✅ **-500**: Mesma região (coesão mantida)
           - ⚠️ **+3**: Outra região (quebra de coesão)
           - ❌ **+999999**: Não alocado (sem vagas)
        
        ### Prioridades do Sistema
        
        O algoritmo segue esta ordem de prioridades:
        1. **Coesão de região** (sempre prioritário)
        2. **Dispersão por nome** (se ativo) - ordem aleatória
        3. **Dispersão por cidade** (se ativo)
        4. **Ordem alfabética** (padrão quando nenhuma feature ativa)
        """)
    
    st.markdown("---")
    
    # Botão de execução
    if st.button("▶️ EXECUTAR ALOCAÇÃO", type="primary", use_container_width=True):
        with st.spinner("⏳ Processando alocação..."):
            try:
                resultado = alocar_estudantes(
                    df_alunos=df_alunos.copy(),
                    df_escolas=df_escolas.copy(),
                    config=config,
                )
                
                st.session_state.resultado_alocacao = resultado
                st.success("✅ Alocação concluída com sucesso!")
                st.balloons()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro durante a alocação: {str(e)}")
                import traceback
                with st.expander("🔍 Detalhes do erro"):
                    st.code(traceback.format_exc())


# ============================================================================
# INTERFACE - TAB 4: RESULTADOS
# ============================================================================

def renderizar_resultados():
    """Renderiza aba de resultados da alocação."""
    st.header("📋 Resultados da Alocação")
    
    if st.session_state.resultado_alocacao is None:
        st.info("👈 Execute a alocação na aba 'Executar Alocação' para ver os resultados aqui.")
        return
    
    resultado = st.session_state.resultado_alocacao
    
    # Estatísticas gerais
    st.subheader("📊 Estatísticas Gerais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    nao_alocado = len(resultado[resultado['Intake'] == 0])
    intake1 = len(resultado[resultado['Intake'] == 1])
    intake2 = len(resultado[resultado['Intake'] == 2])
    
    with col1:
        st.metric("Total Alocado", intake1 + intake2)
    with col2:
        st.metric("Intake 1 (Jan)", intake1, delta="Janeiro")
    with col3:
        st.metric("Intake 2 (Jul)", intake2, delta="Julho")
    with col4:
        st.metric("NÃO ALOCADO", nao_alocado, delta_color="inverse")
    
    # Análise de coesão
    st.markdown("---")
    st.subheader("🎯 Análise de Coesão por Grupo")
    
    alocados = resultado[resultado['Intake'] > 0].copy()
    
    if len(alocados) > 0:
        coesao_por_grupo = alocados.groupby('Grupo').agg({
            'Nome': 'count',
            'Regiao_Escola': lambda x: x.nunique(),
            'Score_Match': 'mean'
        }).rename(columns={
            'Nome': 'Total_Alunos',
            'Regiao_Escola': 'Regioes_Usadas',
            'Score_Match': 'Score_Medio'
        })
        
        coesao_por_grupo['Coesao_Percentual'] = (
            (coesao_por_grupo['Total_Alunos'] - coesao_por_grupo['Regioes_Usadas'] + 1) 
            / coesao_por_grupo['Total_Alunos'] * 100
        ).round(1)
        
        st.dataframe(coesao_por_grupo, use_container_width=True)
    
    # Análise por Cidade (se disponível)
    if 'Cidade' in resultado.columns and st.session_state.config.get('dispersar_por_cidade'):
        st.markdown("---")
        st.subheader("🌍 Análise de Dispersão por Cidade")
        
        # Top 5 cidades mais representadas
        cidades_top = alocados['Cidade'].value_counts().head(5)
        
        for cidade in cidades_top.index:
            alunos_cidade = alocados[alocados['Cidade'] == cidade]
            escolas_usadas = alunos_cidade['Escola_Alocada'].nunique()
            total_alunos_cidade = len(alunos_cidade)
            
            with st.expander(f"📍 {cidade} - {total_alunos_cidade} alunos em {escolas_usadas} escola(s)"):
                distribuicao = alunos_cidade['Escola_Alocada'].value_counts()
                st.bar_chart(distribuicao)
    
    # Tabela completa
    st.markdown("---")
    st.subheader("📝 Tabela Completa de Alocação")
    
    # Preparar DataFrame para exibição
    colunas_exibir = [
        'Nome', 'Grupo', 'Numero_Grupo', 'Sexo_Padrao',
        'Intake', 'Escola_Alocada', 'Regiao_Escola', 'Score_Match'
    ]
    
    # Adicionar Cidade se disponível
    if 'Cidade' in resultado.columns:
        colunas_exibir.insert(4, 'Cidade')
    
    colunas_disponiveis = [col for col in colunas_exibir if col in resultado.columns]
    df_display = resultado[colunas_disponiveis].copy()
    
    # Adicionar classificação do score
    df_display['Classificacao'] = df_display['Score_Match'].apply(classificar_score)
    
    # Renomear para melhor visualização
    rename_dict = {
        'Numero_Grupo': 'N° Grupo',
        'Sexo_Padrao': 'Sexo',
        'Escola_Alocada': 'Escola',
        'Regiao_Escola': 'Região',
        'Score_Match': 'Score',
        'Classificacao': 'Status'
    }
    df_display = df_display.rename(columns=rename_dict)
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # Download
    st.markdown("---")
    st.subheader("💾 Exportar Resultados")
    
    col_download, col_info = st.columns([1, 2])
    
    with col_download:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            resultado.to_excel(writer, sheet_name='Alocacao', index=False)
            
            # Sheet adicional com estatísticas
            if len(alocados) > 0:
                coesao_por_grupo.to_excel(writer, sheet_name='Estatisticas')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button(
            label="📥 Baixar Excel",
            data=output.getvalue(),
            file_name=f"alocacao_intercambio_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col_info:
        st.info(
            "📊 O arquivo Excel contém:\n"
            "- **Aba 'Alocacao'**: Resultado completo\n"
            "- **Aba 'Estatisticas'**: Análise de coesão por grupo"
        )


# ============================================================================
# INTERFACE - PÁGINA SEM DADOS
# ============================================================================

def renderizar_instrucoes():
    """Renderiza instruções quando não há dados carregados."""
    st.info("👈 Faça o upload da planilha Excel na barra lateral para começar.")
    
    with st.expander("📖 Instruções de Uso"):
        st.markdown("""
        ### Como usar este sistema:
        
        #### 1. Preparar a Planilha Excel
        
        Sua planilha deve conter **duas abas**:
        
        **Aba ACOMPANHAMENTO** (Alunos):
        - `Nome`: Nome completo do aluno
        - `Sexo`: Sexo do aluno (M/F)
        - `Grupo`: Grupo/turma do aluno
        - `Cidade` (opcional): Cidade de origem do aluno
        - `RESTRIÇÃO-I1` (opcional): "SIM" para forçar aluno ao Intake 2
        - `Data de Nascimento` (opcional): Para calcular idade
        
        **Aba ESCOLAS**:
        - `Escola`: Nome da escola
        - `Regiao`: Região da escola (ex: "Região 1", "Região 2")
        - `JAN`: Vagas totais no Intake 1 (Janeiro)
        - `JUL`: Vagas totais no Intake 2 (Julho)
        - `F_1`, `M_1`: Vagas por sexo no Intake 1 (opcional)
        - `F_2`, `M_2`: Vagas por sexo no Intake 2 (opcional)
        
        #### 2. Fazer Upload
        
        Clique em "Browse files" na barra lateral e selecione sua planilha.
        
        #### 3. Configurar Alocação
        
        Na aba "Configuração":
        - Defina quantos alunos devem ir para o Intake 1 (Janeiro)
        - Organize a ordem de prioridade dos grupos
        - **NOVO:** Configure opções avançadas:
          - 🔗 Agrupar alunos com mesmo nome
          - 🌍 Dispersar alunos por cidade
        
        #### 4. Executar
        
        Na aba "Executar Alocação", clique no botão para processar.
        
        #### 5. Analisar Resultados
        
        Na aba "Resultados", veja:
        - Estatísticas gerais
        - Análise de coesão por grupo
        - Análise de dispersão por cidade (se ativo)
        - Tabela completa de alocação
        - Opção de download em Excel
        
        ---
        
        ### Como funciona a Coesão de Grupos?
        
        O algoritmo tenta manter alunos do mesmo grupo na mesma região:
        
        1. **Primeira escola**: Define a "região principal" do grupo (Score: -1000)
        2. **Mesma região**: Outros alunos vão para a região principal (Score: -500)
        3. **Outra região**: Só quando não há vagas na principal (Score: +3)
        4. **Não alocado**: Sem vagas em nenhuma região (Score: +999999)
        
        Quanto menor o score, melhor a coesão!
        
        ---
        
        ### Novas Features (v2.0):
        
        **🎲 Dispersão por Nome:**
        - Embaralha ordem aleatoriamente
        - Útil para evitar: 5 "Anas" consecutivas na mesma escola
        - Objetivo: Dispersar nomes iguais em escolas diferentes
        - Planilha em ordem alfabética causa concentração de nomes
        
        **🌍 Dispersão por Cidade:**
        - Alunos da mesma cidade vão para escolas diferentes
        - Útil para evitar: 20 alunos de Salvador na mesma escola
        - Objetivo: Distribuir Salvador em várias escolas
        - Requer coluna "Cidade" na planilha
        """)


# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

def main():
    """Função principal da aplicação."""
    st.title("✈️ Sistema de Alocação de Estudantes - Intercâmbio")
    st.caption("v2.0 - Com dispersão por nome (ordem aleatória) e dispersão por cidade")
    st.markdown("---")
    
    # Renderizar sidebar
    renderizar_sidebar()
    
    # Verificar se há dados carregados
    if st.session_state.df_alunos is None or st.session_state.df_escolas is None:
        renderizar_instrucoes()
        return
    
    # Dados carregados - renderizar abas
    df_alunos = st.session_state.df_alunos
    df_escolas = st.session_state.df_escolas
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visão Geral",
        "⚙️ Configuração",
        "🎯 Executar Alocação",
        "📋 Resultados"
    ])
    
    with tab1:
        renderizar_visao_geral(df_alunos, df_escolas)
    
    with tab2:
        renderizar_configuracao(df_alunos, df_escolas)
    
    with tab3:
        renderizar_executar(df_alunos, df_escolas)
    
    with tab4:
        renderizar_resultados()


if __name__ == "__main__":
    main()