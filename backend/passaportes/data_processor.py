# -*- coding: utf-8 -*-
"""
Griffe Hub - Processador de Dados de Passaportes
"""

import pandas as pd
from typing import Dict, List
from backend.shared.utils import setup_logger, normalizar_nome

logger = setup_logger(__name__)

class ProcessadorDados:
    """Classe para processar e normalizar dados de passaportes"""
    
    def __init__(self):
        self.mapeamento_colunas = {
            'nome': ['nome', 'nome_completo', 'name', 'solicitante'],
            'cpf': ['cpf', 'documento', 'doc'],
            'rg': ['rg', 'identidade'],
            'data_nascimento': ['data_nascimento', 'nascimento', 'dt_nasc'],
            'naturalidade': ['naturalidade', 'cidade_natal'],
            'uf_naturalidade': ['uf_naturalidade', 'estado_natal'],
            'nome_mae': ['nome_mae', 'mae', 'mother'],
            'nome_pai': ['nome_pai', 'pai', 'father'],
            'sexo': ['sexo', 'genero', 'gender'],
            'email': ['email', 'e-mail', 'mail'],
            'telefone': ['telefone', 'tel', 'phone', 'celular'],
            'cep': ['cep', 'codigo_postal'],
            'endereco': ['endereco', 'rua', 'logradouro', 'address'],
            'numero': ['numero', 'num', 'number'],
            'complemento': ['complemento', 'compl'],
            'bairro': ['bairro', 'neighborhood'],
            'cidade': ['cidade', 'municipio', 'city'],
            'uf': ['uf', 'estado', 'state'],
        }
    
    def identificar_coluna(self, colunas_df: List[str], campo: str) -> str:
        """
        Identifica qual coluna do DataFrame corresponde ao campo desejado
        
        Args:
            colunas_df: Lista de colunas do DataFrame
            campo: Campo procurado
        
        Returns:
            Nome da coluna encontrada ou None
        """
        colunas_lower = [c.lower().strip() for c in colunas_df]
        
        if campo in self.mapeamento_colunas:
            for variacao in self.mapeamento_colunas[campo]:
                if variacao.lower() in colunas_lower:
                    idx = colunas_lower.index(variacao.lower())
                    return colunas_df[idx]
        
        return None
    
    def normalizar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza DataFrame de passaportes
        
        Args:
            df: DataFrame original
        
        Returns:
            DataFrame normalizado
        """
        logger.info(f"Iniciando normalização de {len(df)} registros")
        
        df_norm = pd.DataFrame()
        
        # Mapear todas as colunas
        for campo in self.mapeamento_colunas.keys():
            coluna_origem = self.identificar_coluna(df.columns.tolist(), campo)
            if coluna_origem:
                df_norm[campo] = df[coluna_origem]
                logger.debug(f"Campo '{campo}' mapeado de '{coluna_origem}'")
            else:
                df_norm[campo] = None
                logger.debug(f"Campo '{campo}' não encontrado")
        
        # Normalizar nomes
        if 'nome' in df_norm.columns:
            df_norm['nome'] = df_norm['nome'].apply(
                lambda x: normalizar_nome(str(x)) if pd.notna(x) else x
            )
        
        if 'nome_mae' in df_norm.columns:
            df_norm['nome_mae'] = df_norm['nome_mae'].apply(
                lambda x: normalizar_nome(str(x)) if pd.notna(x) else x
            )
        
        if 'nome_pai' in df_norm.columns:
            df_norm['nome_pai'] = df_norm['nome_pai'].apply(
                lambda x: normalizar_nome(str(x)) if pd.notna(x) else x
            )
        
        # Normalizar CPF (remover pontuação)
        if 'cpf' in df_norm.columns:
            df_norm['cpf'] = df_norm['cpf'].apply(
                lambda x: str(x).replace('.', '').replace('-', '').strip() if pd.notna(x) else x
            )
        
        # Normalizar telefone
        if 'telefone' in df_norm.columns:
            df_norm['telefone'] = df_norm['telefone'].apply(
                lambda x: str(x).replace('(', '').replace(')', '').replace('-', '').replace(' ', '').strip() 
                if pd.notna(x) else x
            )
        
        # Normalizar CEP
        if 'cep' in df_norm.columns:
            df_norm['cep'] = df_norm['cep'].apply(
                lambda x: str(x).replace('-', '').strip() if pd.notna(x) else x
            )
        
        logger.info(f"Normalização concluída: {len(df_norm)} registros")
        
        return df_norm
    
    def validar_registro(self, registro: Dict) -> Dict[str, bool]:
        """
        Valida campos obrigatórios de um registro
        
        Args:
            registro: Dicionário com dados do registro
        
        Returns:
            Dicionário com resultado da validação de cada campo
        """
        validacoes = {}
        
        campos_obrigatorios = ['nome', 'cpf', 'data_nascimento', 'nome_mae']
        
        for campo in campos_obrigatorios:
            valor = registro.get(campo)
            validacoes[campo] = pd.notna(valor) and str(valor).strip() != ''
        
        return validacoes
