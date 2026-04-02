# -*- coding: utf-8 -*-
"""
Griffe Hub - DocFill
Módulo backend para preenchimento automático de PDFs com dados de planilha.

Dependências:
    pip install pymupdf openpyxl pandas pillow
"""

import re
import logging
import zipfile
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from PIL import Image, ImageDraw

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise ImportError(
        "PyMuPDF não encontrado. Execute: pip install pymupdf"
    ) from e


# ============================================================================
# LOGGER  (mesmo padrão de setup_logger dos outros módulos do hub)
# ============================================================================

def setup_logger(name: str) -> logging.Logger:
    """Configura logger padrão do Griffe Hub."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logger(__name__)

# ============================================================================
# CONSTANTES
# ============================================================================

# Largura fixa do canvas de mapeamento visual (em pixels)
CANVAS_WIDTH: int = 720

# Cores para distinguir campos mapeados (R, G, B)
CORES_CAMPOS: List[Tuple[int, int, int]] = [
    (79,  70,  229),   # indigo
    (22,  163, 74),    # verde
    (249, 115, 22),    # laranja
    (236, 72,  153),   # rosa
    (6,   182, 212),   # ciano
    (168, 85,  247),   # roxo
    (239, 68,  68),    # vermelho
    (234, 179, 8),     # amarelo
]


# ============================================================================
# PLANILHA
# ============================================================================

def extrair_planilha(
    sheet_bytes: bytes,
    filename: str,
) -> Tuple[List[str], List[List[str]]]:
    """
    Lê planilha Excel (.xlsx / .xls) ou CSV e devolve
    (headers, rows) — tudo como strings.

    Args:
        sheet_bytes: Bytes do arquivo carregado via st.file_uploader
        filename:    Nome original do arquivo (usado para detectar formato)

    Returns:
        headers: Lista com os nomes das colunas (1ª linha)
        rows:    Lista de listas; cada sublista é uma linha de dados
    """
    fname = filename.lower()
    if fname.endswith(".csv"):
        df = pd.read_csv(BytesIO(sheet_bytes), dtype=str).fillna("")
    else:
        df = pd.read_excel(BytesIO(sheet_bytes), dtype=str).fillna("")

    headers = [str(h).strip() for h in df.columns.tolist()]
    rows = [list(row) for _, row in df.iterrows()]

    logger.info("Planilha '%s': %d colunas, %d linhas", filename, len(headers), len(rows))
    return headers, rows


# ============================================================================
# RENDERIZAÇÃO DE PÁGINAS
# ============================================================================

def get_total_pages(pdf_bytes: bytes) -> int:
    """Retorna o número de páginas do PDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    n = len(doc)
    doc.close()
    return n


def _zoom_para_pagina(doc: fitz.Document, page_idx: int) -> float:
    """Calcula o zoom necessário para encaixar a página em CANVAS_WIDTH."""
    page = doc[page_idx]
    return CANVAS_WIDTH / page.rect.width


def renderizar_pagina(
    pdf_bytes: bytes,
    page_idx: int,
) -> Tuple[Image.Image, float]:
    """
    Renderiza uma página do PDF como imagem PIL sem decorações.

    Returns:
        img:  Imagem PIL da página
        zoom: Fator de escala usado (pixels por ponto PDF)
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zoom = _zoom_para_pagina(doc, page_idx)
    mat = fitz.Matrix(zoom, zoom)
    pix = doc[page_idx].get_pixmap(matrix=mat, alpha=False)
    # Converter para PNG antes de criar o PIL Image.
    # Image.frombytes com dados raw do PyMuPDF cria uma imagem com decoder "raw"
    # que é incompatível com st_canvas (Streamlit image_to_url).
    # Passar por PNG garante uma imagem completamente carregada em memória.
    png_bytes = pix.tobytes("png")
    doc.close()
    img = Image.open(BytesIO(png_bytes))
    img.load()  # forçar leitura completa na memória antes de retornar
    return img, zoom


def renderizar_pagina_com_campos(
    pdf_bytes: bytes,
    page_idx: int,
    campos: List[Dict],
) -> Tuple[Image.Image, float]:
    """
    Renderiza uma página do PDF com os campos já mapeados
    desenhados como retângulos coloridos e anotados.

    Args:
        pdf_bytes: Bytes do PDF template
        page_idx:  Índice da página (0-based)
        campos:    Lista de dicionários de campo gerados por esta página

    Returns:
        img:  Imagem PIL pronta para ser usada como fundo do st_canvas
        zoom: Fator de escala (para uso na conversão de coordenadas)
    """
    img, zoom = renderizar_pagina(pdf_bytes, page_idx)
    img = img.convert("RGBA")

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Tentar fonte com tamanho; fallback para fonte bitmap padrão
    try:
        from PIL import ImageFont
        font = ImageFont.load_default(size=11)
    except (TypeError, AttributeError):
        from PIL import ImageFont
        font = ImageFont.load_default()

    campos_pagina = [c for c in campos if c.get("pageNum") == page_idx]
    for i, campo in enumerate(campos_pagina):
        cor = CORES_CAMPOS[i % len(CORES_CAMPOS)]
        l  = int(campo["canvas_left"])
        t  = int(campo["canvas_top"])
        rw = int(campo["canvas_width"])
        rh = int(campo["canvas_height"])

        # Retângulo semitransparente
        draw.rectangle(
            [l, t, l + rw, t + rh],
            fill=(*cor, 45),
            outline=(*cor, 230),
            width=2,
        )
        # Label no canto superior esquerdo do retângulo
        label = f" [{campo['colName']}] "
        draw.text((l + 3, t + 2), label, fill=(*cor, 255), font=font)

    img = Image.alpha_composite(img, overlay).convert("RGB")
    return img, zoom


# ============================================================================
# PREENCHIMENTO DE PDF
# ============================================================================

def preencher_pdf(
    pdf_bytes: bytes,
    campos: List[Dict],
    row: List[str],
    headers: List[str],
) -> bytes:
    """
    Preenche um PDF template com os valores de UMA linha da planilha.

    Os campos contêm coordenadas pré-convertidas para o sistema de
    coordenadas do PyMuPDF (origem topo-esquerdo, eixo Y para baixo).

    Args:
        pdf_bytes: Bytes do PDF template (não é modificado)
        campos:    Lista de campos mapeados (gerada pela página Streamlit)
        row:       Linha de dados da planilha (lista de strings)
        headers:   Nomes das colunas (para logging)

    Returns:
        Bytes do PDF preenchido
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for campo in campos:
        page_idx = campo.get("pageNum", 0)
        if page_idx >= len(doc):
            logger.warning("Página %d não existe no PDF (%d páginas)", page_idx, len(doc))
            continue

        col_idx = campo.get("colIndex", 0)
        valor = str(row[col_idx]) if col_idx < len(row) else ""
        if not valor.strip():
            continue

        font_size = campo.get("fontSize", 10)

        # Coordenadas já em pontos PDF (pré-calculadas na tela)
        pdf_x = campo["pdf_x"]
        pdf_y = campo["pdf_y"]

        page = doc[page_idx]
        page.insert_text(
            fitz.Point(pdf_x, pdf_y),
            valor,
            fontsize=font_size,
            color=(0, 0, 0),
        )

        logger.debug(
            "Campo '%s' → '%s' na pág. %d (%.1f, %.1f)",
            headers[col_idx] if col_idx < len(headers) else col_idx,
            valor[:30],
            page_idx + 1,
            pdf_x,
            pdf_y,
        )

    buf = BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def gerar_zip(
    pdf_bytes: bytes,
    campos: List[Dict],
    rows: List[List[str]],
    headers: List[str],
    progress_callback=None,
) -> Tuple[bytes, int, int]:
    """
    Gera um arquivo ZIP com um PDF preenchido por linha da planilha.

    Args:
        pdf_bytes:         Bytes do PDF template
        campos:            Lista de campos mapeados
        rows:              Todas as linhas de dados
        headers:           Nomes das colunas
        progress_callback: Função opcional f(idx, total, nome) para atualizar progresso

    Returns:
        (zip_bytes, total_ok, total_erros)
    """
    buf = BytesIO()
    total_ok = 0
    total_erros = 0

    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i, row in enumerate(rows):
            nome_base = _sanitize(str(row[0])) if row else f"documento_{i + 1}"

            if progress_callback:
                progress_callback(i, len(rows), nome_base)

            try:
                pdf_filled = preencher_pdf(pdf_bytes, campos, row, headers)
                zf.writestr(f"{nome_base}.pdf", pdf_filled)
                total_ok += 1
            except Exception as exc:
                logger.error("Erro no registro %d (%s): %s", i + 1, nome_base, exc)
                total_erros += 1

    logger.info("Geração concluída: %d OK, %d erros", total_ok, total_erros)
    return buf.getvalue(), total_ok, total_erros


# ============================================================================
# UTILIDADES
# ============================================================================

def _sanitize(s: str) -> str:
    """Remove caracteres inválidos para nomes de arquivo."""
    return re.sub(r'[\/\\?%*:|"<>]', "_", s)[:80].strip()
