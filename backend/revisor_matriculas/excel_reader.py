# -*- coding: utf-8 -*-
"""
Backend - Leitor de Excel para Revisão de Matrículas
"""

import pandas as pd
from typing import Dict, List, Optional

class ExcelReader:
    """Classe para ler e processar dados da planilha de matrículas"""
    
    def __init__(self, excel_file_path: str):
        """
        Inicializa o leitor de Excel
        
        Args:
            excel_file_path: Caminho para o arquivo Excel
        """
        self.excel_file = excel_file_path
        self.df_matricula = None
        self.df_inicial = None
        self.df_medico = None
        self.students = []
        
    def load_data(self) -> bool:
        """
        Carrega os dados das 3 sheets principais
        
        Returns:
            True se carregou com sucesso, False caso contrário
        """
        try:
            self.df_matricula = pd.read_excel(self.excel_file, sheet_name='Form_Matrícula')
            self.df_inicial = pd.read_excel(self.excel_file, sheet_name='Form_Inicial')
            self.df_medico = pd.read_excel(self.excel_file, sheet_name='Form_Médico')
            
            # Criar lista de estudantes únicos
            self._build_student_list()
            
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def _build_student_list(self):
        """Cria lista de estudantes únicos baseado em NOME COMPLETO e EMAIL"""
        students_set = set()
        
        # Coletar de todas as sheets
        for df in [self.df_matricula, self.df_inicial, self.df_medico]:
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    nome = row.get('NOME COMPLETO', '')
                    email = row.get('EMAIL', '')
                    
                    if pd.notna(nome) and nome:
                        students_set.add((str(nome).strip(), str(email).strip() if pd.notna(email) else ''))
        
        # Ordenar por nome
        self.students = sorted(list(students_set), key=lambda x: x[0])
    
    def get_students(self) -> List[Dict[str, str]]:
        """
        Retorna lista de estudantes
        
        Returns:
            Lista de dicionários com nome e email de cada estudante
        """
        return [{'nome': nome, 'email': email} for nome, email in self.students]
    
    def get_student_data(self, nome: str, email: str) -> Dict:
        """
        Busca dados de um estudante específico em todas as sheets
        
        Args:
            nome: Nome completo do estudante
            email: Email do estudante
            
        Returns:
            Dicionário com os dados do estudante organizados por formulário
        """
        data = {
            'matricula': {},
            'inicial': {},
            'medico': {}
        }
        
        # Buscar em Form_Matrícula
        if self.df_matricula is not None:
            mask = (self.df_matricula['NOME COMPLETO'].str.strip() == nome.strip())
            if email:
                mask = mask & (self.df_matricula['EMAIL'].str.strip() == email.strip())
            
            matches = self.df_matricula[mask]
            if len(matches) > 0:
                data['matricula'] = matches.iloc[0].to_dict()
        
        # Buscar em Form_Inicial
        if self.df_inicial is not None:
            mask = (self.df_inicial['NOME COMPLETO'].str.strip() == nome.strip())
            if email:
                mask = mask & (self.df_inicial['EMAIL'].str.strip() == email.strip())
            
            matches = self.df_inicial[mask]
            if len(matches) > 0:
                data['inicial'] = matches.iloc[0].to_dict()
        
        # Buscar em Form_Médico
        if self.df_medico is not None:
            mask = (self.df_medico['NOME COMPLETO'].str.strip() == nome.strip())
            if email:
                mask = mask & (self.df_medico['EMAIL'].str.strip() == email.strip())
            
            matches = self.df_medico[mask]
            if len(matches) > 0:
                data['medico'] = matches.iloc[0].to_dict()
        
        return data