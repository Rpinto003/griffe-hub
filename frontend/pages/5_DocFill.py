# -*- coding: utf-8 -*-
"""
GRIFFE HUB - DocFill
Preenchimento automático de PDFs com dados de planilha.

Fluxo em 3 etapas:
  1. Upload do PDF template + planilha de dados
  2. Mapeamento visual: clique em uma coluna e depois clique no PDF para posicioná-la
  3. Geração em lote: um PDF preenchido por linha → download .zip
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from io import BytesIO

# ---------------------------------------------------------------------------
# Adicionar pasta backend ao path  (mesmo padrão dos outros módulos do hub)
# ---------------------------------------------------------------------------
BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

# ---------------------------------------------------------------------------
# Importar módulo backend
# ---------------------------------------------------------------------------
try:
    from docfill.filler import (
        CANVAS_WIDTH,
        extrair_planilha,
        gerar_zip,
        get_total_pages,
        preencher_pdf,
        renderizar_pagina_com_campos,
    )
    BACKEND_DISPONIVEL = True
except ImportError as _err:
    BACKEND_DISPONIVEL = False
    _BACKEND_ERRO = str(_err)

# ---------------------------------------------------------------------------
# Importar componente de captura de clique na imagem
# ---------------------------------------------------------------------------
try:
    from streamlit_image_coordinates import streamlit_image_coordinates
    COORDS_DISPONIVEL = True
except ImportError:
    COORDS_DISPONIVEL = False


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA  (deve ser a primeira chamada Streamlit)
# ============================================================================

st.set_page_config(
    page_title="DocFill - Griffe Hub",
    page_icon="📝",
    layout="wide",
)


# ============================================================================
# SESSION STATE
# ============================================================================

_DEFAULTS = {
    "df_step":        1,       # etapa atual: 1, 2 ou 3
    "df_pdf_bytes":   None,    # bytes do PDF template
    "df_pdf_name":    "",      # nome do arquivo PDF
    "df_n_pages":     0,       # total de páginas do PDF
    "df_headers":     [],      # lista de colunas da planilha
    "df_rows":        [],      # lista de listas com os dados
    "df_sheet_name":  "",      # nome do arquivo de planilha
    "df_campos":      [],      # campos mapeados
    "df_page_idx":    0,       # página sendo visualizada (0-based)
    "df_img_key":     0,       # incrementado para forçar reset do componente de imagem
    "df_active_col":  None,    # índice da coluna aguardando posicionamento
    "df_font_size":   10,      # tamanho de fonte padrão
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🏠 Navegação")
    if st.button("← Voltar ao Hub", use_container_width=True):
        st.switch_page("streamlit_app.py")

    st.markdown("---")

    # Indicador de progresso por etapa
    st.markdown("### 📍 Progresso")
    _etapas = [
        ("📁", "Upload de Arquivos"),
        ("🗺️", "Mapeamento Visual"),
        ("⚡", "Geração de PDFs"),
    ]
    for _i, (_ico, _nome) in enumerate(_etapas, start=1):
        _atual = st.session_state.df_step == _i
        _feito = st.session_state.df_step > _i
        if _feito:
            st.markdown(f"✅ {_ico} {_nome}")
        elif _atual:
            st.markdown(f"**▶️ {_ico} {_nome}**")
        else:
            st.markdown(f"⬜ {_ico} {_nome}")

    st.markdown("---")

    # Lista rápida de campos mapeados com opção de remoção
    if st.session_state.df_campos:
        _n = len(st.session_state.df_campos)
        st.markdown(f"### 📋 Campos mapeados ({_n})")
        for _i, _c in enumerate(st.session_state.df_campos):
            _c1, _c2 = st.columns([5, 1])
            with _c1:
                st.caption(f"Pág. {_c['pageNum']+1} · **{_c['colName']}** · {_c['fontSize']}pt")
            with _c2:
                if st.button("✕", key=f"sidebar_del_{_i}", help="Remover"):
                    st.session_state.df_campos.pop(_i)
                    st.session_state.df_img_key += 1
                    st.rerun()
        if st.button("🗑️ Limpar todos", use_container_width=True):
            st.session_state.df_campos = []
            st.session_state.df_img_key += 1
            st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ Como Usar")
    st.markdown("""
    1. **Suba** o PDF template e a planilha
    2. **Clique** no nome de uma coluna
    3. **Clique no PDF** para posicioná-la
    4. Repita para todas as colunas
    5. Clique em **"Gerar PDFs"**

    ---

    ### 💡 Dicas:
    - Funciona com múltiplas páginas
    - Cada linha da planilha vira um PDF
    - O ZIP é baixado automaticamente
    """)

    st.markdown("---")
    st.markdown("**Status:** ✅ Online")


# ============================================================================
# HEADER
# ============================================================================

st.title("📝 DocFill")
st.markdown("Preenchimento Automático de PDFs com Dados da Planilha")
st.markdown("---")


# ============================================================================
# VERIFICAÇÃO DE DEPENDÊNCIAS
# ============================================================================

if not BACKEND_DISPONIVEL:
    st.error(
        f"❌ Módulo backend não disponível: `{_BACKEND_ERRO}`\n\n"
        "Execute no ambiente do hub:\n"
        "```\npip install pymupdf openpyxl pandas pillow\n```"
    )
    st.stop()

if not COORDS_DISPONIVEL:
    st.error(
        "❌ Componente de imagem não encontrado.\n\n"
        "Execute no ambiente do hub:\n"
        "```\npip install streamlit-image-coordinates\n```"
    )
    st.stop()


# ============================================================================
# ETAPA 1 — UPLOAD DE ARQUIVOS
# ============================================================================

if st.session_state.df_step == 1:

    st.header("📁 Etapa 1: Upload de Arquivos")

    col_pdf, col_sheet = st.columns(2)

    with col_pdf:
        st.subheader("📄 Documento PDF Template")
        st.caption("O arquivo que será preenchido automaticamente com os dados")

        uploaded_pdf = st.file_uploader(
            "Selecione o arquivo PDF",
            type=["pdf"],
            key="uploader_pdf",
        )

        if uploaded_pdf is not None:
            try:
                pdf_bytes = uploaded_pdf.read()
                n_pages   = get_total_pages(pdf_bytes)
                st.session_state.df_pdf_bytes = pdf_bytes
                st.session_state.df_pdf_name  = uploaded_pdf.name
                st.session_state.df_n_pages   = n_pages
                st.success(
                    f"✅ **{uploaded_pdf.name}** carregado  "
                    f"({n_pages} página{'s' if n_pages != 1 else ''})"
                )
            except Exception as e:
                st.error(f"❌ Erro ao ler PDF: {e}")

        elif st.session_state.df_pdf_bytes:
            st.info(
                f"📄 Usando arquivo anterior: **{st.session_state.df_pdf_name}** "
                f"({st.session_state.df_n_pages} página(s))"
            )

    with col_sheet:
        st.subheader("📊 Planilha de Dados")
        st.caption("Excel (.xlsx / .xls) ou CSV — cabeçalho obrigatório na 1ª linha")

        uploaded_sheet = st.file_uploader(
            "Selecione a planilha",
            type=["xlsx", "xls", "csv"],
            key="uploader_sheet",
        )

        if uploaded_sheet is not None:
            try:
                headers, rows = extrair_planilha(
                    uploaded_sheet.read(), uploaded_sheet.name
                )
                st.session_state.df_headers    = headers
                st.session_state.df_rows       = rows
                st.session_state.df_sheet_name = uploaded_sheet.name
                st.success(
                    f"✅ **{uploaded_sheet.name}** carregado  "
                    f"({len(rows)} registro{'s' if len(rows) != 1 else ''}, "
                    f"{len(headers)} coluna{'s' if len(headers) != 1 else ''})"
                )
            except Exception as e:
                st.error(f"❌ Erro ao ler planilha: {e}")

        elif st.session_state.df_headers:
            st.info(
                f"📊 Usando arquivo anterior: **{st.session_state.df_sheet_name}** "
                f"({len(st.session_state.df_rows)} registros)"
            )

    # Prévia da planilha
    if st.session_state.df_headers:
        st.markdown("---")
        st.markdown("### 📋 Prévia da Planilha")
        df_preview = pd.DataFrame(
            st.session_state.df_rows[:8],
            columns=st.session_state.df_headers,
        )
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        _extra = len(st.session_state.df_rows) - 8
        if _extra > 0:
            st.caption(f"… e mais {_extra} registro(s) não exibidos")

    st.markdown("---")
    _can_continue = (
        st.session_state.df_pdf_bytes is not None
        and len(st.session_state.df_headers) > 0
    )

    if st.button(
        "Continuar para Mapeamento →",
        type="primary",
        disabled=not _can_continue,
    ):
        st.session_state.df_campos     = []
        st.session_state.df_img_key    = 0
        st.session_state.df_page_idx   = 0
        st.session_state.df_active_col = None
        st.session_state.df_step       = 2
        st.rerun()


# ============================================================================
# ETAPA 2 — MAPEAMENTO VISUAL
# ============================================================================

elif st.session_state.df_step == 2:

    st.header("🗺️ Etapa 2: Mapeamento Visual dos Campos")

    # Instrução dinâmica baseada no estado
    _active = st.session_state.df_active_col
    if _active is not None:
        _nome_col = st.session_state.df_headers[_active]
        st.info(f"📍 Clique no PDF para posicionar **\"{_nome_col}\"** — ou clique no botão da coluna novamente para cancelar")
    else:
        st.caption("👉 Clique em uma **coluna** à direita para ativá-la, depois clique no PDF para posicioná-la")

    # ── CONTROLES DE PÁGINA E FONTE ─────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 3])

    with ctrl1:
        if st.session_state.df_n_pages > 1:
            _page_num = st.number_input(
                "Página do PDF",
                min_value=1,
                max_value=st.session_state.df_n_pages,
                value=st.session_state.df_page_idx + 1,
                step=1,
                key="page_selector",
            )
            if int(_page_num) - 1 != st.session_state.df_page_idx:
                st.session_state.df_page_idx = int(_page_num) - 1
                st.session_state.df_img_key += 1
                st.rerun()
        else:
            st.caption("📄 1 página")

    with ctrl2:
        _font_size = st.number_input(
            "Fonte (pt)", min_value=6, max_value=72,
            value=st.session_state.df_font_size, step=1,
            key="font_size_input",
        )
        st.session_state.df_font_size = int(_font_size)

    with ctrl3:
        _n_campos = len(st.session_state.df_campos)
        if _n_campos:
            st.metric("Campos posicionados", _n_campos)

    st.markdown("---")

    # ── LAYOUT PRINCIPAL ─────────────────────────────────────────────────────
    col_img, col_right = st.columns([3, 1])

    with col_img:
        # Renderizar página com campos já confirmados desenhados sobre ela
        try:
            _bg_img, _zoom = renderizar_pagina_com_campos(
                st.session_state.df_pdf_bytes,
                st.session_state.df_page_idx,
                st.session_state.df_campos,
            )
        except Exception as _render_err:
            st.error(f"Erro ao renderizar PDF: {_render_err}")
            st.stop()

        # Exibe imagem com captura de clique
        _click = streamlit_image_coordinates(
            _bg_img,
            key=f"pdf_img_{st.session_state.df_img_key}",
        )

        # Processar clique se houver coluna ativa
        if _click is not None and st.session_state.df_active_col is not None:
            _cx = _click["x"]
            _cy = _click["y"]
            _col_idx  = st.session_state.df_active_col
            _col_nome = st.session_state.df_headers[_col_idx]
            _fs       = st.session_state.df_font_size

            # Converter coordenadas de pixel para pontos PDF
            _pdf_x = _cx / _zoom
            _pdf_y = (_cy + _fs * 1.1) / _zoom

            _novo_campo = {
                "colIndex":      _col_idx,
                "colName":       _col_nome,
                "pageNum":       st.session_state.df_page_idx,
                # Coordenadas canvas (para desenhar o retângulo na visualização)
                "canvas_left":   max(0, _cx - 2),
                "canvas_top":    max(0, _cy - _fs),
                "canvas_width":  140,
                "canvas_height": int(_fs * 2),
                # Coordenadas PDF (para inserção do texto via PyMuPDF)
                "pdf_x":         _pdf_x,
                "pdf_y":         _pdf_y,
                "fontSize":      _fs,
            }
            st.session_state.df_campos.append(_novo_campo)
            st.session_state.df_active_col = None   # desativar coluna após posicionar
            st.session_state.df_img_key   += 1       # resetar componente de imagem
            st.rerun()

    # ── PAINEL DIREITO: COLUNAS + CAMPOS ────────────────────────────────────
    with col_right:
        st.markdown("#### 📋 Colunas")
        st.caption("Clique para ativar, depois clique no PDF")

        for _i, _h in enumerate(st.session_state.df_headers):
            _placed   = sum(1 for c in st.session_state.df_campos if c["colIndex"] == _i)
            _is_active = st.session_state.df_active_col == _i

            if _is_active:
                _label = f"✏️ {_h}"
                _btype = "primary"
            elif _placed:
                _label = f"✅ {_h} ({_placed}x)"
                _btype = "secondary"
            else:
                _label = f"＋ {_h}"
                _btype = "secondary"

            if st.button(_label, key=f"col_btn_{_i}", use_container_width=True, type=_btype):
                # Toggle: clique na coluna ativa → desativar; clique em outra → ativar
                st.session_state.df_active_col = None if _is_active else _i
                st.rerun()

        # Lista de campos posicionados
        if st.session_state.df_campos:
            st.markdown("---")
            st.markdown("#### Posicionados")
            for _i, _c in enumerate(st.session_state.df_campos):
                with st.container(border=True):
                    st.markdown(f"**{_c['colName']}**")
                    st.caption(
                        f"Pág. {_c['pageNum']+1} · {_c['fontSize']}pt\n"
                        f"x:{_c['pdf_x']:.0f} y:{_c['pdf_y']:.0f}"
                    )
                    if st.button("🗑️ Remover", key=f"rm_campo_{_i}", use_container_width=True):
                        st.session_state.df_campos.pop(_i)
                        st.session_state.df_img_key += 1
                        st.rerun()

    # ── NAVEGAÇÃO ────────────────────────────────────────────────────────────
    st.markdown("---")
    _nav1, _nav2, _nav3 = st.columns([1, 1, 4])

    with _nav1:
        if st.button("← Voltar"):
            st.session_state.df_step = 1
            st.rerun()

    with _nav2:
        if st.button(
            "Gerar PDFs →",
            type="primary",
            disabled=len(st.session_state.df_campos) == 0,
        ):
            st.session_state.df_step = 3
            st.rerun()


# ============================================================================
# ETAPA 3 — GERAÇÃO DOS DOCUMENTOS
# ============================================================================

elif st.session_state.df_step == 3:

    st.header("⚡ Etapa 3: Geração dos Documentos")

    _n_rows   = len(st.session_state.df_rows)
    _n_campos = len(st.session_state.df_campos)

    _r1, _r2, _r3 = st.columns(3)
    with _r1:
        st.metric("Documentos a gerar", _n_rows)
    with _r2:
        st.metric("Campos mapeados", _n_campos)
    with _r3:
        st.metric("Páginas no template", st.session_state.df_n_pages)

    with st.expander("📋 Ver mapeamento completo", expanded=False):
        for _c in st.session_state.df_campos:
            st.markdown(
                f"- **{_c['colName']}** → "
                f"Página {_c['pageNum']+1}, "
                f"pos. ({_c['pdf_x']:.0f}, {_c['pdf_y']:.0f}), "
                f"fonte {_c['fontSize']}pt"
            )

    st.markdown("---")

    if st.button("🚀 Gerar todos os PDFs", type="primary", use_container_width=True):

        _progress = st.progress(0)
        _status   = st.empty()

        def _cb(idx: int, total: int, nome: str):
            _progress.progress((idx + 1) / total)
            _status.text(f"Gerando: {nome} ({idx + 1}/{total})…")

        try:
            _zip_bytes, _ok, _erros = gerar_zip(
                pdf_bytes         = st.session_state.df_pdf_bytes,
                campos            = st.session_state.df_campos,
                rows              = st.session_state.df_rows,
                headers           = st.session_state.df_headers,
                progress_callback = _cb,
            )

            _progress.progress(1.0)
            _status.text("✅ Geração concluída!")

            if _erros:
                st.warning(
                    f"⚠️ {_ok} documento(s) gerado(s), {_erros} erro(s). "
                    "Consulte os logs para detalhes."
                )
            else:
                st.success(f"✅ {_ok} documento(s) gerado(s) com sucesso!")

            st.markdown("### 💾 Download")
            st.download_button(
                label="📥 Baixar todos os PDFs (.zip)",
                data=_zip_bytes,
                file_name="documentos_preenchidos.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
            )

            with st.expander("📊 Estatísticas", expanded=False):
                st.markdown(f"""
                | Métrica | Valor |
                |---|---|
                | Documentos gerados | {_ok} |
                | Erros | {_erros} |
                | Campos por documento | {_n_campos} |
                | Template | {st.session_state.df_pdf_name} |
                | Planilha | {st.session_state.df_sheet_name} |
                """)

        except Exception as _gen_err:
            st.error(f"❌ Erro durante a geração: {_gen_err}")

    st.markdown("---")
    _n1, _n2 = st.columns(2)

    with _n1:
        if st.button("← Editar Mapeamento", use_container_width=True):
            st.session_state.df_step = 2
            st.rerun()

    with _n2:
        if st.button("↩️ Novo Documento (recomeçar)", use_container_width=True):
            for _k in list(st.session_state.keys()):
                if _k.startswith("df_"):
                    del st.session_state[_k]
            st.rerun()
