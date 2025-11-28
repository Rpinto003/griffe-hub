# -*- coding: utf-8 -*-
"""
GRIFFE HUB - Sistema Centralizado de Aplicações
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar pasta backend ao path  
BACKEND_PATH = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

st.set_page_config(
    page_title="Griffe Hub",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cabeçalho
st.title("🏢 Griffe Hub")
st.markdown("Sistema Centralizado de Aplicações da Griffe Turismo")
st.markdown("---")

# Aplicações
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛂 Sistema de Passaportes")
    st.markdown("Processamento automatizado de solicitações de passaportes")
    if st.button("Abrir", key="pass", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Passaportes.py")

with col2:
    st.markdown("### ✈️ Extrator de Faturas")
    st.markdown("Extração automática de dados de faturas OFB")
    if st.button("Abrir", key="fatur", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Extrator_Faturas.py")

col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🎓 Alocação de Alunos")
    st.markdown("Algoritmo de Matching para Intercâmbio (Intake/Escola)")
    if st.button("Abrir", key="aloc", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Alocacao_Alunos.py")

with col4:
    st.markdown("### 📋 Revisor de Matrículas")
    st.markdown("Sistema de revisão de formulários de matrícula")
    if st.button("Abrir", key="revisor", use_container_width=True, type="primary"):
        st.switch_page("pages/4_Revisor_Matriculas.py")