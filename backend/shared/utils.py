# -*- coding: utf-8 -*-
"""
Griffe Hub - Utilitários Compartilhados
"""

import logging
import re
from typing import Optional
from pathlib import Path
from backend.config import LOG_FILE, LOG_LEVEL

def setup_logger(name: str) -> logging.Logger:
    """
    Configura logger para um módulo
    
    Args:
        name: Nome do logger (geralmente __name__)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Handler para arquivo
    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def limpar_espacos(texto: Optional[str]) -> Optional[str]:
    """Remove espaços múltiplos de uma string"""
    if not texto:
        return texto
    return re.sub(r"\s+", " ", texto).strip()

def normalizar_nome(nome: str) -> str:
    """
    Normaliza nome de pessoa (remove caracteres especiais, mantém formato)
    
    Args:
        nome: Nome a ser normalizado
    
    Returns:
        Nome normalizado
    """
    if not nome:
        return ""
    
    # Remove caracteres especiais mantendo letras, espaços, / e -
    nome = re.sub(r"[^A-ZÁÉÍÓÚÂÊÔÃÕÇ/\s\-']", "", nome, flags=re.IGNORECASE)
    
    # Remove espaços múltiplos
    nome = limpar_espacos(nome)
    
    # Remove traços no início/fim
    nome = nome.strip("-").strip()
    
    return nome.upper()

def validar_arquivo_pdf(arquivo_path: Path) -> bool:
    """
    Valida se o arquivo é um PDF válido
    
    Args:
        arquivo_path: Caminho do arquivo
    
    Returns:
        True se válido, False caso contrário
    """
    if not arquivo_path.exists():
        return False
    
    if arquivo_path.suffix.lower() != '.pdf':
        return False
    
    if arquivo_path.stat().st_size == 0:
        return False
    
    return True

def formatar_moeda_brl(valor: float) -> str:
    """
    Formata valor como moeda brasileira
    
    Args:
        valor: Valor numérico
    
    Returns:
        String formatada como R$ X.XXX,XX
    """
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def normalizar_valor_moeda(valor_str: Optional[str]) -> Optional[float]:
    """
    Converte string de moeda brasileira para float
    
    Args:
        valor_str: String no formato "1.234,56"
    
    Returns:
        Valor float ou None se inválido
    """
    if not valor_str:
        return None
    
    try:
        # Remove pontos e substitui vírgula por ponto
        valor_limpo = valor_str.replace('.', '').replace(',', '.')
        return float(valor_limpo)
    except (ValueError, AttributeError):
        return None
