# -*- coding: utf-8 -*-
"""
GRIFFE HUB - Revisor de Matrículas
Sistema de revisão de formulários de matrícula
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Adicionar pasta backend ao path
BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

try:
    from revisor_matriculas import (
        ExcelReader,
        FORM_MATRICULA_SECTIONS,
        FORM_INICIAL_SECTIONS,
        FORM_MEDICO_SECTIONS,
        get_field_label
    )
except ImportError as e:
    st.error(f"""
    ❌ **Erro ao importar módulos do backend**
    
    **Detalhes do erro:** {str(e)}
    
    **Caminho do backend esperado:** `{BACKEND_PATH}`
    
    **Possíveis soluções:**
    1. Verifique se a pasta `backend/revisor_matriculas` existe
    2. Confirme que os arquivos Python estão na pasta correta
    3. Verifique se há um arquivo `__init__.py` em `backend/revisor_matriculas/`
    
    **Estrutura esperada:**
    ```
    projeto/
    ├── backend/
    │   └── revisor_matriculas/
    │       ├── __init__.py
    │       ├── excel_reader.py
    │       └── field_mapping.py
    └── frontend/
        └── pages/
            └── 4_Revisor_Matriculas.py
    ```
    """)
    st.stop()

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Revisor de Matrículas - Griffe Hub",
    page_icon="📋",
    layout="wide"
)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def format_value(value):
    """Formata valor para exibição"""
    if pd.isna(value):
        return ""
    
    # Se for timestamp, converte para string
    if isinstance(value, pd.Timestamp):
        return value.strftime("%d/%m/%Y")
    
    return str(value)

def render_field(label, value, key):
    """Renderiza um campo com botão de copiar"""
    formatted_value = format_value(value)
    
    # Verificar se é um link (começa com http ou https)
    is_link = formatted_value and (
        formatted_value.startswith('http://') or 
        formatted_value.startswith('https://')
    )
    
    # Se for campo de anexo, usar layout diferente
    if label.upper().startswith('ANEXO'):
        st.markdown(f"**📎 {label.replace('ANEXO:', '').strip()}**")
        
        if is_link:
            # Renderizar como link clicável
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f'<div style="background-color: #d4edda; padding: 10px; '
                    f'border-radius: 5px; margin-bottom: 10px;">'
                    f'<a href="{formatted_value}" target="_blank" style="color: #155724; text-decoration: none;">'
                    f'🔗 Abrir Documento</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("📋", key=f"copy_{key}", use_container_width=True, 
                            help="Copiar link"):
                    st.code(formatted_value, language=None)
        elif formatted_value:
            st.markdown(
                f'<div style="background-color: #f0f2f6; padding: 10px; '
                f'border-radius: 5px; margin-bottom: 10px;">{formatted_value}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="background-color: #fff3cd; padding: 10px; '
                f'border-radius: 5px; margin-bottom: 10px; color: #856404;">'
                f'<em>Documento não anexado</em></div>',
                unsafe_allow_html=True
            )
    else:
        # Renderização normal para campos que não são anexos
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{label}**")
            
            if formatted_value:
                # Se for link em campo normal, também renderizar como link
                if is_link:
                    st.markdown(
                        f'<div style="background-color: #d4edda; padding: 10px; '
                        f'border-radius: 5px; margin-bottom: 10px;">'
                        f'<a href="{formatted_value}" target="_blank" style="color: #155724;">'
                        f'🔗 {formatted_value}</a>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="background-color: #f0f2f6; padding: 10px; '
                        f'border-radius: 5px; margin-bottom: 10px;">{formatted_value}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    f'<div style="background-color: #fff3cd; padding: 10px; '
                    f'border-radius: 5px; margin-bottom: 10px; color: #856404;">'
                    f'<em>Não preenchido</em></div>',
                    unsafe_allow_html=True
                )
        
        with col2:
            if formatted_value:
                if st.button("📋", key=f"copy_{key}", use_container_width=True, 
                            help="Clique para copiar"):
                    st.code(formatted_value, language=None)

def render_section(section_title, fields, data, form_type):
    """Renderiza uma seção do formulário"""
    st.markdown(f"### {section_title}")
    st.markdown("---")
    
    for field in fields:
        value = data.get(field, "")
        key = f"{form_type}_{field}_{section_title}"
        
        # Remover emojis do label
        label = get_field_label(field)
        
        render_field(label, value, key)
    
    st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.title("📋 Revisor de Matrículas")
st.markdown("Sistema de Revisão de Formulários de Matrícula - Visualização e Cópia de Dados")
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
    1. **Faça upload** da planilha Excel com os dados
    2. **Selecione um aluno** na lista
    3. **Visualize** os dados dos formulários
    4. **Copie** os campos necessários para revisão
    
    ---
    
    ### 📝 Formulários Disponíveis:
    - **Form Matrícula**: Dados gerais e preferências
    - **Form Inicial**: Dados pessoais e documentos
    - **Form Médico**: Informações de saúde
    
    ---
    
    ### 💡 Dicas:
    - Use o botão **"📋 Copiar"** para copiar valores
    - Campos vazios aparecem destacados
    - Os dados são organizados por seção
    """)
    
    st.markdown("---")
    st.markdown("**Status:** ✅ Online")

# ============================================================================
# UPLOAD DE ARQUIVO
# ============================================================================

st.header("📁 Upload da Planilha")

uploaded_file = st.file_uploader(
    "Selecione a planilha Excel com os dados de matrícula",
    type=['xlsx', 'xls'],
    help="Arquivo deve conter as sheets: Form_Matrícula, Form_Inicial, Form_Médico"
)

if uploaded_file:
    
    # Salvar arquivo temporariamente
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Carregar dados
        with st.spinner("Carregando dados da planilha..."):
            reader = ExcelReader(tmp_path)
            if reader.load_data():
                st.success(f"✅ Planilha carregada com sucesso! {len(reader.get_students())} estudantes encontrados.")
                
                # Armazenar no session_state
                st.session_state['reader'] = reader
                st.session_state['students'] = reader.get_students()
            else:
                st.error("❌ Erro ao carregar planilha. Verifique se as sheets estão corretas.")
    
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
    
    finally:
        # Limpar arquivo temporário
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# ============================================================================
# SELEÇÃO DE ALUNO E VISUALIZAÇÃO
# ============================================================================

if 'students' in st.session_state and st.session_state['students']:
    
    st.markdown("---")
    st.header("👤 Seleção de Aluno")
    
    # Criar lista de opções para o selectbox
    student_options = [
        f"{s['nome']} ({s['email']})" if s['email'] else s['nome']
        for s in st.session_state['students']
    ]
    
    selected_index = st.selectbox(
        "Selecione um aluno para visualizar os dados:",
        range(len(student_options)),
        format_func=lambda i: student_options[i]
    )
    
    if selected_index is not None:
        selected_student = st.session_state['students'][selected_index]
        nome = selected_student['nome']
        email = selected_student['email']
        
        st.markdown("---")
        
        # Buscar dados do aluno
        reader = st.session_state['reader']
        student_data = reader.get_student_data(nome, email)
        
        # Criar tabs para os diferentes formulários
        tab1, tab2, tab3 = st.tabs([
            "📝 Form Matrícula", 
            "📄 Form Inicial", 
            "🏥 Form Médico"
        ])
        
        # ===== TAB 1: FORM MATRÍCULA =====
        with tab1:
            st.header("📝 Formulário de Matrícula")
            
            if student_data['matricula']:
                # Informações principais
                st.markdown("### 📌 Informações Principais")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    grupo = student_data['matricula'].get('GRUPO', 'N/A')
                    st.metric("Grupo", grupo)
                
                with col2:
                    programa = student_data['matricula'].get('PROGRAMA', 'N/A')
                    st.metric("Programa", programa)
                
                with col3:
                    status = student_data['matricula'].get('STATUS', 'N/A')
                    st.metric("Status", status)
                
                st.markdown("---")
                
                # Renderizar seções
                for section_title, fields in FORM_MATRICULA_SECTIONS.items():
                    with st.expander(section_title, expanded=False):
                        render_section(
                            section_title, 
                            fields, 
                            student_data['matricula'],
                            'matricula'
                        )
            else:
                st.warning("⚠️ Nenhum dado encontrado para este aluno no Form Matrícula")
        
        # ===== TAB 2: FORM INICIAL =====
        with tab2:
            st.header("📄 Formulário Inicial")
            
            if student_data['inicial']:
                # Informações principais
                st.markdown("### 📌 Informações Principais")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    programa = student_data['inicial'].get('PROGRAMA', 'N/A')
                    st.metric("Programa", programa)
                
                with col2:
                    status = student_data['inicial'].get('STATUS', 'N/A')
                    st.metric("Status", status)
                
                with col3:
                    cpf = student_data['inicial'].get('NUMERO DO CPF DO ESTUDANTE', 'N/A')
                    st.metric("CPF", cpf)
                
                st.markdown("---")
                
                # Renderizar seções
                for section_title, fields in FORM_INICIAL_SECTIONS.items():
                    with st.expander(section_title, expanded=False):
                        render_section(
                            section_title, 
                            fields, 
                            student_data['inicial'],
                            'inicial'
                        )
            else:
                st.warning("⚠️ Nenhum dado encontrado para este aluno no Form Inicial")
        
        # ===== TAB 3: FORM MÉDICO =====
        with tab3:
            st.header("🏥 Formulário Médico")
            
            if student_data['medico']:
                # Informações principais
                st.markdown("### 📌 Informações Principais")
                col1, col2 = st.columns(2)
                
                with col1:
                    status = student_data['medico'].get('STATUS', 'N/A')
                    st.metric("Status", status)
                
                with col2:
                    problema_saude = student_data['medico'].get('VOCE TEM ALGUM PROBLEMA DE SAUDE?', 'N/A')
                    st.metric("Problema de Saúde", problema_saude)
                
                st.markdown("---")
                
                # Renderizar seções
                for section_title, fields in FORM_MEDICO_SECTIONS.items():
                    with st.expander(section_title, expanded=False):
                        render_section(
                            section_title, 
                            fields, 
                            student_data['medico'],
                            'medico'
                        )
            else:
                st.warning("⚠️ Nenhum dado encontrado para este aluno no Form Médico")

else:
    st.info("👆 Faça upload de uma planilha para começar")