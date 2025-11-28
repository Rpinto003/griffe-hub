# -*- coding: utf-8 -*-
"""
GRIFFE HUB - Sistema de Passaportes
Processamento automatizado de solicitações de passaportes
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Adicionar pasta backend ao path
BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

# Importar módulos do backend
try:
    from passaportes.data_processor import ProcessadorDados
    from passaportes.automation import AutomacaoPassaporte
    BACKEND_DISPONIVEL = True
except ImportError:
    BACKEND_DISPONIVEL = False
    st.warning("⚠️ Módulo backend não encontrado. Rodando em modo demonstração.")

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Passaportes - Griffe Hub",
    page_icon="🛂",
    layout="wide"
)

# ============================================================================
# HEADER
# ============================================================================

st.title("🛂 Sistema de Processamento de Passaportes")
st.markdown("Automatização completa do processo de solicitação de passaportes")
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🏠 Navegação")
    if st.button("← Voltar ao Hub", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    st.markdown("---")
    
    st.markdown("### 📊 Etapas")
    etapa = st.radio(
        "Selecione a etapa:",
        ["📤 Upload & Normalização", "🤖 Preenchimento", "📊 Relatório"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("### ℹ️ Informações")
    st.info("""
    **Status do Sistema:**
    - ✅ Upload: Online
    - ✅ Automação: Online
    - ✅ Relatórios: Online
    """)

# ============================================================================
# INICIALIZAÇÃO DE SESSION STATE
# ============================================================================

if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'df_original' not in st.session_state:
    st.session_state.df_original = None
if 'df_normalizado' not in st.session_state:
    st.session_state.df_normalizado = None
if 'indice_atual' not in st.session_state:
    st.session_state.indice_atual = 0
if 'status_registros' not in st.session_state:
    st.session_state.status_registros = {}

# ============================================================================
# ETAPA 1: UPLOAD & NORMALIZAÇÃO
# ============================================================================

if etapa == "📤 Upload & Normalização":
    st.header("📤 Upload da Planilha")
    
    st.markdown("""
    **Instruções:**
    1. Faça upload da planilha Excel com os dados dos solicitantes
    2. Revise os dados carregados
    3. Clique em "Normalizar Dados" para preparar para processamento
    """)
    
    uploaded_file = st.file_uploader(
        "Escolha o arquivo Excel",
        type=['xlsx', 'xls'],
        help="Formatos aceitos: .xlsx, .xls"
    )
    
    if uploaded_file:
        try:
            # Carregar dados
            df = pd.read_excel(uploaded_file)
            st.session_state.df_original = df
            st.session_state.dados_carregados = True
            
            # Mostrar informações
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Registros", len(df))
            with col2:
                st.metric("Total de Colunas", len(df.columns))
            with col3:
                st.metric("Tamanho", f"{uploaded_file.size / 1024:.1f} KB")
            
            st.markdown("### 📋 Colunas Identificadas")
            st.write(", ".join(df.columns.tolist()))
            
            st.markdown("### 👀 Preview dos Dados")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Botão normalizar
            st.markdown("---")
            if st.button("🔄 Normalizar Dados", type="primary", use_container_width=True):
                with st.spinner("Normalizando dados..."):
                    if BACKEND_DISPONIVEL:
                        try:
                            processador = ProcessadorDados()
                            df_norm = processador.normalizar(df)
                            st.session_state.df_normalizado = df_norm
                            st.success(f"✅ {len(df_norm)} registros normalizados com sucesso!")
                            
                            st.markdown("### ✨ Dados Normalizados")
                            st.dataframe(df_norm.head(10), use_container_width=True)
                            
                            # Inicializar status dos registros
                            st.session_state.status_registros = {
                                i: 'pendente' for i in range(len(df_norm))
                            }
                        except Exception as e:
                            st.error(f"Erro ao normalizar: {str(e)}")
                    else:
                        # Modo demonstração
                        st.session_state.df_normalizado = df
                        st.success(f"✅ {len(df)} registros processados (modo demo)")
                        st.info("💡 Instale o módulo backend para funcionalidade completa")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
    
    else:
        st.info("👆 Faça upload de uma planilha para começar")

# ============================================================================
# ETAPA 2: PREENCHIMENTO AUTOMÁTICO
# ============================================================================

elif etapa == "🤖 Preenchimento":
    st.header("🤖 Preenchimento Automático")
    
    if not st.session_state.dados_carregados or st.session_state.df_normalizado is None:
        st.warning("⚠️ Nenhum dado carregado. Volte para a etapa de Upload.")
        if st.button("← Ir para Upload"):
            st.rerun()
    else:
        df = st.session_state.df_normalizado
        total = len(df)
        atual = st.session_state.indice_atual
        
        # Verificar se há registros pendentes
        pendentes = [i for i, status in st.session_state.status_registros.items() 
                     if status == 'pendente']
        
        if not pendentes:
            st.success("🎉 Todos os registros foram processados!")
            if st.button("🔄 Reiniciar Processamento"):
                st.session_state.status_registros = {i: 'pendente' for i in range(total)}
                st.session_state.indice_atual = 0
                st.rerun()
        else:
            # Atualizar índice para próximo pendente
            if atual not in pendentes:
                st.session_state.indice_atual = pendentes[0]
                atual = pendentes[0]
            
            # Progresso
            concluidos = sum(1 for s in st.session_state.status_registros.values() 
                           if s == 'concluido')
            progresso = concluidos / total
            
            st.progress(progresso, text=f"Progresso: {concluidos}/{total} registros processados")
            
            # Informações do registro atual
            st.markdown(f"### 📋 Registro {atual + 1} de {total}")
            
            registro = df.iloc[atual].to_dict()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📄 Dados do Solicitante")
                
                # Mostrar dados em formato de tabela
                dados_display = pd.DataFrame([
                    {"Campo": k, "Valor": v} for k, v in registro.items()
                ])
                st.dataframe(dados_display, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### ⚙️ Ações")
                
                if st.button("🚀 Preencher Formulário", type="primary", use_container_width=True):
                    with st.spinner("Executando automação..."):
                        if BACKEND_DISPONIVEL:
                            try:
                                automacao = AutomacaoPassaporte()
                                resultado = automacao.preencher_formulario(registro)
                                
                                if resultado['sucesso']:
                                    st.success("✅ Formulário preenchido com sucesso!")
                                    for campo, status in resultado['campos'].items():
                                        icone = "✅" if status else "❌"
                                        st.write(f"{icone} {campo}")
                                else:
                                    st.error(f"❌ Erro: {resultado.get('erro', 'Erro desconhecido')}")
                            except Exception as e:
                                st.error(f"❌ Erro na automação: {str(e)}")
                        else:
                            st.info("✨ Modo demonstração - Formulário seria preenchido aqui")
                            import time
                            time.sleep(2)
                            st.success("✅ Simulação concluída!")
                
                st.markdown("---")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("✅ Concluído", use_container_width=True):
                        st.session_state.status_registros[atual] = 'concluido'
                        st.rerun()
                
                with col_b:
                    if st.button("⏭️ Pular", use_container_width=True):
                        st.session_state.status_registros[atual] = 'pulado'
                        st.rerun()
            
            # Navegação
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Anterior", disabled=(atual == 0)):
                    if atual > 0:
                        st.session_state.indice_atual = atual - 1
                        st.rerun()
            
            with col3:
                if st.button("➡️ Próximo", disabled=(atual >= total - 1)):
                    if atual < total - 1:
                        st.session_state.indice_atual = atual + 1
                        st.rerun()

# ============================================================================
# ETAPA 3: RELATÓRIO
# ============================================================================

elif etapa == "📊 Relatório":
    st.header("📊 Relatório de Processamento")
    
    if not st.session_state.dados_carregados:
        st.warning("⚠️ Nenhum dado disponível para relatório.")
    else:
        # Calcular estatísticas
        total = len(st.session_state.status_registros)
        concluidos = sum(1 for s in st.session_state.status_registros.values() 
                        if s == 'concluido')
        pulados = sum(1 for s in st.session_state.status_registros.values() 
                     if s == 'pulado')
        pendentes = sum(1 for s in st.session_state.status_registros.values() 
                       if s == 'pendente')
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("✅ Concluídos", concluidos)
        with col3:
            st.metric("⏭️ Pulados", pulados)
        with col4:
            st.metric("⏳ Pendentes", pendentes)
        
        # Gráfico de progresso
        if total > 0:
            progress_data = pd.DataFrame({
                'Status': ['Concluídos', 'Pulados', 'Pendentes'],
                'Quantidade': [concluidos, pulados, pendentes],
                'Percentual': [
                    f"{concluidos/total*100:.1f}%",
                    f"{pulados/total*100:.1f}%",
                    f"{pendentes/total*100:.1f}%"
                ]
            })
            
            st.markdown("### 📈 Distribuição de Status")
            st.dataframe(progress_data, use_container_width=True, hide_index=True)
        
        # Tabela detalhada
        if st.session_state.df_normalizado is not None:
            st.markdown("### 📋 Detalhamento dos Registros")
            
            df_relatorio = st.session_state.df_normalizado.copy()
            df_relatorio['Status'] = df_relatorio.index.map(
                lambda i: st.session_state.status_registros.get(i, 'pendente')
            )
            
            # Filtro de status
            filtro_status = st.multiselect(
                "Filtrar por status:",
                ['concluido', 'pulado', 'pendente'],
                default=['concluido', 'pulado', 'pendente']
            )
            
            df_filtrado = df_relatorio[df_relatorio['Status'].isin(filtro_status)]
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Download
            st.markdown("### 💾 Exportar Dados")
            
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="relatorio_passaportes.csv",
                mime="text/csv",
                use_container_width=True
            )
