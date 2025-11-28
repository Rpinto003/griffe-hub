# -*- coding: utf-8 -*-
"""
Griffe Hub - Extrator de Faturas OFB
Módulo para extração de dados de PDFs de faturas
"""

import re
import pdfplumber
import pandas as pd
from io import BytesIO
from typing import List, Tuple, Optional, Dict
import logging # Adicionado logging

# ============================================================================
# FUNÇÕES DE UTILITY INSERIDAS AQUI PARA RESOLVER O IMPORTERROR
# ============================================================================

def setup_logger(name: str) -> logging.Logger:
    """Configura um logger básico (Simulação de backend.shared.utils.setup_logger)"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def limpar_espacos(s: str) -> str:
    """Remove múltiplos espaços e substitui quebras de linha por um espaço (Simulação de backend.shared.utils.limpar_espacos)"""
    return re.sub(r'\s+', ' ', s).strip()

logger = setup_logger(__name__)

# Constantes
MAX_VOOS = 8
MONEY_PT = r'(?:\d{1,3}(?:\.\d{3})*,\d{2})'
TIME_HM = r'(?:\d{2}:\d{2})'

# Expressões regulares para parsing
HEADER_RE = r'EMISS[ÃA]O/REF\s+HIST[ÓO]RICO\s*/\s*DESCRI[ÇC][ÃA]O DOS SERVI[ÇC]OS\s+CONTA\s+VALOR\s*\(R\$?\)'
RESUMO_INICIO_RE = r'RESUMO\s*:\s*TOTAL DA FATURA\s*N[ºO]\s*\d+'
PAGINACAO_RE = r'^\s*P[áa]gina\s+\d+\s*$'
CONTINUACAO_RE = r'^\s*Continua[çc][ãa]o\s+da\s+FATURA\b.*$'
ETICKET_LINE_RE_FLEXIBLE = r'(?:^|\s)(\d{3,4})\s+(\d{5,7})\s*-\s*Loc\.\s*([A-Z0-9]+)\b'
CIA_RAW_RE = r'^[A-Z]{2}\s*/\s*.+$'
CIA_SANITIZE_RE = r'^([A-Z]{2}\s*/\s*[^(]+(?:\([^)]+\))?)\b'
PAX_LINE_RE_FLEXIBLE = r'(?:^|\s)Pax:\s*([^\n]+)'

LEG_RE = re.compile(
    r'([A-Z]{3})\s*/\s*([A-Z]{3})\s+([A-Z0-9]{1,2}\s*\d{3,4})\s+(\d{2}/\d{2}/\d{2})\s+(' + TIME_HM + r')\s+(' + TIME_HM + r')'
)

def norm_money_ptbr(s: Optional[str]) -> Optional[float]:
    """Normaliza valores monetários BR (1.234,56)"""
    if not s: 
        return None
    try:
        return float(s.replace('.', '').replace(',', '.'))
    except:
        return None

def norm_money_mixed(s: Optional[str]) -> Optional[float]:
    """Normaliza valores monetários mistos"""
    if not s: 
        return None
    try:
        s = s.strip()
        if "," in s and "." in s:
            return float(s.replace(",", ""))
        if "," in s and "." not in s:
            return float(s.replace(",", "."))
        return float(s)
    except:
        return None

def pdf_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extrai texto de PDF a partir de bytes"""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def topo_antes_cabecalho(texto_total: str) -> str:
    """Retorna o texto antes do cabeçalho da tabela"""
    m = re.search(HEADER_RE, texto_total, re.IGNORECASE)
    return texto_total[:m.start()] if m else texto_total

def numero_fatura(texto_total: str, topo: str) -> Optional[str]:
    """Extrai número da fatura"""
    # Padrão: "17849 11/08/2025 R$ 480.999,37 17849"
    m = re.search(r'(\d{4,})\s+\d{2}/\d{2}/\d{4}\s+R\$\s+[\d\.,]+\s+\1', texto_total[:2000])
    if m:
        return m.group(1).strip()
    
    m = re.search(r'N[º°]?\s+(?:DE\s+)?ORDEM[^\d]*(\d{4,})', texto_total[:2000], re.IGNORECASE)
    if m: 
        return m.group(1).strip()
    
    m = re.search(r'(?:N[º°]?\s*FATURA)\s*(?:\n|\s)*(\d{3,})', topo, re.IGNORECASE)
    if m: 
        return m.group(1).strip()
    
    m2 = re.search(r'\bFATURA\D+(\d{3,})\b', topo, re.IGNORECASE)
    return m2.group(1).strip() if m2 else None

def emissao_fatura(texto_total: str, topo: str) -> Optional[str]:
    """Extrai data de emissão da fatura"""
    m = re.search(r'\d{4,}\s+(\d{2}/\d{2}/\d{4})\s+R\$', texto_total[:2000])
    if m: 
        return m.group(1)
    
    m = re.search(r'(?:EMISS[ÃA]O|EMISSAO)[^\d]*(\d{2}/\d{2}/\d{4})', texto_total[:2000], re.IGNORECASE)
    if m: 
        return m.group(1)
    
    m = re.search(r'\bEMISS[ÃA]O\b\s*(?:\n|\s)*(\d{2}/\d{2}/\d{4})', topo, re.IGNORECASE)
    return m.group(1) if m else None

def recorta_corpo(texto: str) -> str:
    """Remove cabeçalhos e rodapés, mantendo apenas o corpo"""
    m_ini = re.search(HEADER_RE, texto, re.IGNORECASE)
    m_fim = re.search(RESUMO_INICIO_RE, texto, re.IGNORECASE)
    if m_ini and m_fim and m_fim.start() > m_ini.end():
        texto = texto[m_ini.end():m_fim.start()]
    
    out = []
    for ln in texto.splitlines():
        if re.search(HEADER_RE, ln, re.IGNORECASE):
            continue
        if re.search(PAGINACAO_RE, ln, re.IGNORECASE):
            continue
        if re.search(CONTINUACAO_RE, ln, re.IGNORECASE):
            continue
        out.append(ln)
    return "\n".join(out).strip()

def pontos_pax(texto: str) -> List[re.Match]:
    """Encontra todas as ocorrências de 'Pax:'"""
    matches = list(re.finditer(PAX_LINE_RE_FLEXIBLE, texto, re.MULTILINE | re.IGNORECASE))
    matches.sort(key=lambda x: x.start())
    return matches

def extrai_cia_acima(texto: str, start_idx: int) -> Optional[str]:
    """Extrai companhia aérea olhando linhas acima"""
    cabeca = texto[:start_idx].splitlines()
    for back in range(1, 20):
        if len(cabeca) - back < 0: 
            break
        raw = cabeca[-back].strip()
        if re.match(CIA_RAW_RE, raw):
            m = re.match(CIA_SANITIZE_RE, raw)
            cia = m.group(1) if m else raw
            cia = re.split(r'\b(TARIFA|TAXA|FEE|SUB\-?TOTAL)\b', cia, flags=re.IGNORECASE)[0]
            return limpar_espacos(cia)
    return None

def limpa_pax_nome(s: str) -> str:
    """Limpa nome do passageiro"""
    s = re.split(r'\b(TARIFA|TAXA|SUB\-?TOTAL|FEE)\b', s, flags=re.IGNORECASE)[0]
    s = re.sub(r"[^A-ZÁÉÍÓÚÂÊÔÃÕÇ/\s\-'']", "", s, flags=re.IGNORECASE)
    return limpar_espacos(s).strip("-").strip()

def parse_legs(trecho: str) -> list:
    """Extrai informações de voos"""
    legs = []
    for m in LEG_RE.finditer(trecho):
        legs.append((
            m.group(1), m.group(2),
            re.sub(r"\s+"," ",m.group(3)).upper(),
            m.group(4), m.group(5), m.group(6),
        ))
        if len(legs) >= MAX_VOOS:
            break
    return legs

def parse_usd(block: str) -> Dict[str, Optional[float]]:
    """Extrai valores em USD"""
    out = {"tarifa": None, "taxa": None, "fee": None, "total": None}
    for m in re.finditer(r'(Tarifa|Taxa|Fee|Total)\s*:\s*USD\s*([\d\.,]+)', block, re.IGNORECASE):
        out[m.group(1).lower()] = norm_money_mixed(m.group(2))
    if out["total"] is None:
        soma = sum(v for v in [out["tarifa"], out["taxa"], out["fee"]] if v is not None)
        out["total"] = soma if soma else None
    return out

def parse_brl(block: str) -> Dict[str, Optional[float]]:
    """Extrai valores em BRL"""
    r = {"tarifa": None, "taxa": None, "sub": None}
    t1 = re.search(r'^\s*TARIFA\s*\n\s*(' + MONEY_PT + r')\+', block, re.MULTILINE)
    x1 = re.search(r'^\s*TAXA\s*\n\s*(' + MONEY_PT + r')\+', block, re.MULTILINE)
    s1 = re.search(r'^\s*SUB\-?TOTAL\s*\n\s*(' + MONEY_PT + r')\=', block, re.MULTILINE)
    if not t1: t1 = re.search(r'\bTARIFA\s+(' + MONEY_PT + r')\+', block)
    if not x1: x1 = re.search(r'\bTAXA\s+(' + MONEY_PT + r')\+', block)
    if not s1: s1 = re.search(r'\bSUB\-?TOTAL\s+(' + MONEY_PT + r')\=', block)
    r["tarifa"] = norm_money_ptbr(t1.group(1)) if t1 else None
    r["taxa"]   = norm_money_ptbr(x1.group(1)) if x1 else None
    r["sub"]    = norm_money_ptbr(s1.group(1)) if s1 else None
    return r

def extrai_eticket_proximo(texto: str, anchor_idx: int, busca_para_baixo: bool=True) -> Tuple[Optional[str], Optional[str]]:
    """Busca e-ticket e localizador próximo ao índice anchor"""
    linhas = texto.splitlines(True)
    cumul = 0
    posmap = []
    for i, ln in enumerate(linhas):
        posmap.append((i, cumul, cumul+len(ln)))
        cumul += len(ln)

    linha_anchor = 0
    for i, a, b in posmap:
        if a <= anchor_idx < b:
            linha_anchor = i
            break

    # Buscar para cima
    for back in range(1, 80):
        j = linha_anchor - back
        if j < 0: break
        ln = linhas[j]
        m = re.search(ETICKET_LINE_RE_FLEXIBLE, ln, re.IGNORECASE)
        if m:
            return (f"{m.group(1)} {m.group(2)}", m.group(3))

    # Buscar para baixo
    if busca_para_baixo:
        for fwd in range(1, 40):
            j = linha_anchor + fwd
            if j >= len(linhas): break
            ln = linhas[j]
            m = re.search(ETICKET_LINE_RE_FLEXIBLE, ln, re.IGNORECASE)
            if m:
                return (f"{m.group(1)} {m.group(2)}", m.group(3))

    return (None, None)

def parse_bloco_por_pax(texto_limpo: str, pax_match: re.Match, proximo_pax_idx: int, 
                        nf: str, em_fat: str, ordem: int) -> dict:
    """Parse completo do bloco de um passageiro"""
    start_idx = pax_match.start()
    end_idx = proximo_pax_idx if proximo_pax_idx != -1 else len(texto_limpo)

    block = texto_limpo[start_idx:end_idx]
    block = re.sub(r'^(?:\s*(?:TARIFA|TAXA|SUB\-?TOTAL)\s*(?:\n\s*' + MONEY_PT + r'[\+\=])?[\s\S]{0,60}\n)+', 
                   '', block, flags=re.MULTILINE)

    pax = limpa_pax_nome(pax_match.group(1))
    eticket, localizador = extrai_eticket_proximo(texto_limpo, start_idx, busca_para_baixo=True)
    cia = extrai_cia_acima(texto_limpo, start_idx)

    mclass = re.search(r'Classe de reserva:\s*([^\n]+)', block, re.IGNORECASE)
    classe = limpar_espacos(mclass.group(1)) if mclass else None
    usd = parse_usd(block)
    camb = re.search(r'Cambio:\s*BRL\s*([\d\.,]+)', block, re.IGNORECASE)
    cambio = norm_money_mixed(camb.group(1)) if camb else None
    brl = parse_brl(block)

    trecho_voos = block
    if mclass:
        trecho_voos = block[0:mclass.start()]
    legs = parse_legs(trecho_voos)

    row = {
        "ORDEM": ordem,
        "Nº FATURA": nf, 
        "EMISSÃO-FATURA": em_fat, 
        "COMPANHIA AEREA": cia,
        "ETICKET": eticket, 
        "LOCALIZADOR": localizador, 
        "PAX": pax,
        "CLASSEDERESERVA": classe,
        "TARIFA_USD": usd["tarifa"], 
        "TAXA_USD": usd["taxa"], 
        "FEE_USD": usd["fee"], 
        "TOTAL_USD": usd["total"],
        "CAMBIO": cambio, 
        "TARIFA": brl["tarifa"], 
        "TAXA": brl["taxa"], 
        "SUB-TOTAL": brl["sub"],
    }
    
    for i, (o,d,n,dt,hp,hd) in enumerate(legs, start=1):
        row[f"VOO{i}-PARTIDA"]=o
        row[f"VOO{i}-DESTINO"]=d
        row[f"VOO{i}-NÚMERO"]=n
        row[f"VOO{i}-DATA"]=dt
        row[f"VOO{i}-HORARIOPARTIDA"]=hp
        row[f"VOO{i}-HORARIODESTINO"]=hd
    
    return row

def processar_pdf(pdf_bytes: bytes, nome_arquivo: str) -> pd.DataFrame:
    """
    Processa um PDF de fatura e retorna DataFrame com dados extraídos
    
    Args:
        pdf_bytes: Bytes do arquivo PDF
        nome_arquivo: Nome do arquivo para referência
    
    Returns:
        DataFrame com dados extraídos
    """
    try:
        logger.info(f"Processando {nome_arquivo}")
        
        # Extrair texto
        full_txt = pdf_text_from_bytes(pdf_bytes)
        topo = topo_antes_cabecalho(full_txt)
        nf = numero_fatura(full_txt, topo) or ""
        em_fat = emissao_fatura(full_txt, topo) or ""
        
        logger.info(f"Fatura: {nf}, Emissão: {em_fat}")
        
        # Recortar corpo
        corpo = recorta_corpo(full_txt)
        if not corpo:
            logger.warning(f"Corpo vazio em {nome_arquivo}")
            return pd.DataFrame()
        
        # Processar passageiros
        pax_matches = pontos_pax(corpo)
        logger.info(f"Encontrados {len(pax_matches)} passageiros")
        
        rows = []
        for idx, m in enumerate(pax_matches, start=1):
            prox = pax_matches[idx].start() if idx < len(pax_matches) else -1
            row = parse_bloco_por_pax(corpo, m, prox, nf, em_fat, idx)
            row["ARQUIVO"] = nome_arquivo
            rows.append(row)
        
        if not rows:
            logger.warning(f"Nenhum passageiro extraído de {nome_arquivo}")
            return pd.DataFrame()
        
        # Criar DataFrame
        df = pd.DataFrame(rows)
        
        # Organizar colunas
        cols = ["ORDEM", "ARQUIVO", "Nº FATURA", "EMISSÃO-FATURA", "COMPANHIA AEREA", 
                "ETICKET", "LOCALIZADOR", "PAX"]
        for i in range(1, MAX_VOOS+1):
            cols += [f"VOO{i}-PARTIDA", f"VOO{i}-DESTINO", f"VOO{i}-NÚMERO", 
                    f"VOO{i}-DATA", f"VOO{i}-HORARIOPARTIDA", f"VOO{i}-HORARIODESTINO"]
        cols += ["CLASSEDERESERVA", "TARIFA_USD", "TAXA_USD", "FEE_USD", "TOTAL_USD", 
                "CAMBIO", "TARIFA", "TAXA", "SUB-TOTAL"]
        
        for c in cols:
            if c not in df.columns: 
                df[c] = None
        
        df = df[cols]
        
        logger.info(f"Extração concluída: {len(df)} registros")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao processar {nome_arquivo}: {str(e)}")
        raise