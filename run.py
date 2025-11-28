#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de inicialização do Griffe Hub
Execute: python run.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Inicia a aplicação Streamlit"""
    
    # Verificar se está no diretório correto
    if not Path("frontend/streamlit_app.py").exists():
        print("❌ Erro: Execute este script a partir da raiz do projeto Griffe_Hub")
        sys.exit(1)
    
    print("🚀 Iniciando Griffe Hub...")
    print("📍 Acesse: http://localhost:8501")
    print("⏹️  Para parar: Ctrl+C\n")
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "frontend/streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando Griffe Hub...")
        sys.exit(0)

if __name__ == "__main__":
    main()
