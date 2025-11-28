# -*- coding: utf-8 -*-
"""
GRIFFE HUB - Extrator de Faturas OFB
Extração automatizada de dados de faturas de passagens aéreas
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from io import BytesIO

# Adicionar pasta backend ao path
BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

# Importar módulos do backend
try:
    from extrator_faturas.extractor import processar_pdf
    BACKEND_DISPONIVEL = True
except ImportError:
    BACKEND_DISPONIVEL = False
    st.warning("⚠️ Módulo backend não encontrado. Rodando em modo demonstração.")

# ============================================================================
# FUNÇÃO DE PROCESSAMENTO (MOVIMENTADA PARA O INÍCIO DO ARQUIVO)
#
# Este bloco foi movido para o topo para resolver o NameError,
# garantindo que a função seja definida antes de ser chamada no botão (linha ~110).
# ============================================================================

def processar_faturas(uploaded_files):
    """Processa todos os arquivos e gera a planilha"""
    
    # Barra de progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_dataframes = []
    
    # Container para mensagens
    messages_container = st.container()
    
    # Processar cada arquivo
    for idx, file in enumerate(uploaded_files):
        with messages_container:
            status_text.text(f"Processando {file.name}...")
        progress_bar.progress((idx) / len(uploaded_files))
        
        try:
            if BACKEND_DISPONIVEL:
                # Ler bytes do arquivo
                pdf_bytes = file.read()
                
                # Processar PDF
                df = processar_pdf(pdf_bytes, file.name)
                
                if not df.empty:
                    all_dataframes.append(df)
                    with messages_container:
                        st.success(f"✅ {file.name}: {len(df)} passageiros extraídos")
                else:
                    with messages_container:
                        st.warning(f"⚠️ {file.name}: Nenhum dado extraído")
            else:
                # Modo demonstração
                with messages_container:
                    st.info(f"📄 {file.name}: Modo demonstração ativado")
                import time
                time.sleep(1)
                
        except Exception as e:
            with messages_container:
                st.error(f"❌ Erro ao processar {file.name}: {str(e)}")
    
    progress_bar.progress(1.0)
    status_text.text("✅ Processamento concluído!")
    
    if all_dataframes or not BACKEND_DISPONIVEL:
        if BACKEND_DISPONIVEL:
            # Combinar todos os DataFrames
            df_final = pd.concat(all_dataframes, ignore_index=True)
        else:
            # Usar dados de exemplo no modo demo
            df_final = pd.DataFrame({
                'ORDEM': range(1, 51),
                'ARQUIVO': ['exemplo.pdf'] * 50,
                'Nº FATURA': ['17849'] * 50,
                'EMISSÃO-FATURA': ['11/08/2025'] * 50,
                'COMPANHIA AEREA': ['AC/AIR CANADA'] * 50,
                'ETICKET': [f'2681 30{5670+i}' for i in range(50)],
                'LOCALIZADOR': ['A5FJVX'] * 50,
                'PAX': [f'PASSAGEIRO {i+1}' for i in range(50)],
                'VOO1-PARTIDA': ['GRU'] * 50,
                'VOO1-DESTINO': ['YYZ'] * 50,
                'TARIFA': [12055.71] * 50,
                'TAXA': [349.55] * 50,
                'SUB-TOTAL': [12405.26] * 50
            })
        
        # Mostrar estatísticas
        st.markdown("---")
        st.header("📊 Resultados")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Passageiros", len(df_final))
        with col2:
            st.metric("Arquivos Processados", len(uploaded_files))
        with col3:
            faturas = df_final['Nº FATURA'].nunique() if 'Nº FATURA' in df_final.columns else 0
            st.metric("Faturas Únicas", faturas)
        with col4:
            valor_total = df_final['SUB-TOTAL'].sum() if 'SUB-TOTAL' in df_final.columns else 0
            st.metric("Valor Total", f"R$ {valor_total:,.2f}")
        
        # Visualização dos dados
        st.markdown("### 📋 Preview dos Dados")
        
        # Colunas para visualização
        colunas_preview = ['ORDEM', 'ARQUIVO', 'Nº FATURA', 'EMISSÃO-FATURA', 'PAX', 
                          'ETICKET', 'LOCALIZADOR']
        
        # Adicionar colunas de voo se existirem
        if 'VOO1-PARTIDA' in df_final.columns:
            colunas_preview.extend(['VOO1-PARTIDA', 'VOO1-DESTINO'])
        
        # Adicionar colunas de valores
        colunas_preview.extend(['TARIFA', 'TAXA', 'SUB-TOTAL'])
        
        # Filtrar apenas colunas existentes
        colunas_preview = [c for c in colunas_preview if c in df_final.columns]
        
        df_preview = df_final[colunas_preview].copy()
        
        # Formatar valores monetários
        for col in ['TARIFA', 'TAXA', 'SUB-TOTAL']:
            if col in df_preview.columns:
                df_preview[col] = df_preview[col].apply(
                    lambda x: f"R$ {x:,.2f}" if pd.notna(x) else ""
                )
        
        st.dataframe(df_preview, use_container_width=True, height=400)
        
        # Baixar Excel
        st.markdown("### 💾 Download")
        
        # Criar arquivo Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Passageiros')
            
            # Formatação do Excel
            workbook = writer.book
            worksheet = writer.sheets['Passageiros']
            
            # Formato para moeda
            money_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
            
            # Aplicar formato nas colunas de valores
            for col_name in ['TARIFA', 'TAXA', 'SUB-TOTAL', 'TARIFA_USD', 'TAXA_USD', 'FEE_USD', 'TOTAL_USD', 'CAMBIO']:
                if col_name in df_final.columns:
                    col_idx = df_final.columns.get_loc(col_name)
                    worksheet.set_column(col_idx, col_idx, 15, money_format)
            
            # Ajustar largura das colunas
            if 'ORDEM' in df_final.columns:
                worksheet.set_column(0, 0, 8)
            if 'ARQUIVO' in df_final.columns:
                col_idx = df_final.columns.get_loc('ARQUIVO')
                worksheet.set_column(col_idx, col_idx, 25)
            if 'PAX' in df_final.columns:
                col_idx = df_final.columns.get_loc('PAX')
                worksheet.set_column(col_idx, col_idx, 30)
        
        output.seek(0)
        
        # Botão de download
        st.download_button(
            label="📥 Baixar Planilha Excel",
            data=output,
            file_name="faturas_passagens_extraidas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
        
        # Informações adicionais
        with st.expander("📈 Estatísticas Detalhadas"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Por Arquivo:**")
                if 'ARQUIVO' in df_final.columns:
                    stats_arquivo = df_final.groupby('ARQUIVO').agg({
                        'PAX': 'count',
                        'SUB-TOTAL': 'sum'
                    }).rename(columns={'PAX': 'Passageiros', 'SUB-TOTAL': 'Valor Total'})
                    stats_arquivo['Valor Total'] = stats_arquivo['Valor Total'].apply(
                        lambda x: f"R$ {x:,.2f}"
                    )
                    st.dataframe(stats_arquivo, use_container_width=True)
            
            with col2:
                st.markdown("**Por Companhia:**")
                if 'COMPANHIA AEREA' in df_final.columns:
                    stats_cia = df_final.groupby('COMPANHIA AEREA').agg({
                        'PAX': 'count',
                        'SUB-TOTAL': 'sum'
                    }).rename(columns={'PAX': 'Passageiros', 'SUB-TOTAL': 'Valor Total'})
                    stats_cia['Valor Total'] = stats_cia['Valor Total'].apply(
                        lambda x: f"R$ {x:,.2f}"
                    )
                    st.dataframe(stats_cia, use_container_width=True)
    
    else:
        st.error("❌ Nenhum dado foi extraído dos arquivos selecionados.")


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Extrator de Faturas - Griffe Hub",
    page_icon="✈️",
    layout="wide"
)

# ============================================================================
# HEADER
# ============================================================================

st.title("✈️ Extrator de Faturas OFB")
st.markdown("Sistema de Extração Automatizada de Passagens Aéreas")
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🏠 Navegação")
    if st.button("← Voltar ao Hub", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    st.markdown("---")
    
    st.markdown("### ℹ️ Como Usar")
    st.markdown("""
    1. **Selecione o(s) arquivo(s) PDF** da fatura
    2. Clique em **"Processar Faturas"**
    3. Visualize os resultados
    4. **Baixe a planilha Excel**
    
    ---
    
    ### 📋 Informações Extraídas:
    - Número e data da fatura
    - Dados dos passageiros
    - E-tickets e localizadores
    - Informações de voos
    - Tarifas, taxas e valores
    
    ---
    
    ### 💡 Dicas:
    - Você pode processar múltiplos PDFs de uma vez
    - A ordem dos passageiros é mantida
    - Duplicatas são removidas automaticamente
    """)
    
    st.markdown("---")
    st.markdown("**Status:** ✅ Online")

# ============================================================================
# UPLOAD DE ARQUIVOS
# ============================================================================

st.header("📁 Upload de Arquivos")

uploaded_files = st.file_uploader(
    "Selecione um ou mais arquivos PDF de faturas",
    type=['pdf'],
    accept_multiple_files=True,
    help="Você pode selecionar múltiplos arquivos PDF de uma vez"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")
    
    # Mostrar lista de arquivos
    with st.expander("📄 Arquivos Selecionados", expanded=True):
        for i, file in enumerate(uploaded_files, 1):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{i}.** {file.name}")
            with col2:
                st.write(f"{file.size / 1024:.1f} KB")
            with col3:
                st.write("📄 PDF")
    
    # Botão para processar
    st.markdown("---")
    if st.button("🚀 Processar Faturas", type="primary", use_container_width=True):
        processar_faturas(uploaded_files)
else:
    st.info("👆 Faça upload de um ou mais arquivos PDF para começar")
    
    # Área de exemplo
    st.markdown("### 📝 Exemplo de Dados Extraídos")
    exemplo_df = pd.DataFrame({
        'ORDEM': [1, 2, 3],
        'Nº FATURA': ['17849', '17849', '17849'],
        'EMISSÃO-FATURA': ['11/08/2025', '11/08/2025', '11/08/2025'],
        'PAX': ['SILVA/JOAO', 'SANTOS/MARIA', 'OLIVEIRA/PEDRO'],
        'ETICKET': ['2681 305677', '2681 305679', '2681 305681'],
        'LOCALIZADOR': ['A5FJVX', 'A5EQFF', 'A5EQFF'],
        'VOO1-PARTIDA': ['GRU', 'GRU', 'GRU'],
        'VOO1-DESTINO': ['YYZ', 'YYZ', 'YYZ'],
        'TARIFA': [12055.71, 12896.03, 12896.03],
        'TAXA': [349.55, 349.55, 349.55],
        'SUB-TOTAL': [12405.26, 13245.58, 13245.58]
    })
    
    st.dataframe(exemplo_df, use_container_width=True, hide_index=True)