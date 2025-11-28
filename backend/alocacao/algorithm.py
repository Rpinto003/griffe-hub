# -*- coding: utf-8 -*-
"""
GRIFFE HUB - Alocação Simplificada de Alunos em Escolas Internacionais

OBJETIVO:
Alocar alunos em escolas mantendo grupos coesos (mesma região) sempre que possível.

REGRAS:
1. Grupos prioritários vão para Intake 1 (Janeiro), demais para Intake 2 (Julho)
2. Alunos são processados por ordem de prioridade do grupo, depois alfabeticamente
3. Cada grupo tenta ficar na mesma região (coesão)
4. Primeira escola alocada define a "região principal" do grupo
5. Se não houver vagas na região principal, busca outras regiões em ordem (1, 2, 3...)

NOVAS FEATURES:
6. DISPERSÃO POR NOME: Embaralha ordem aleatoriamente para evitar nomes iguais na mesma escola
7. DISPERSÃO POR CIDADE: Alunos da mesma cidade são distribuídos em escolas diferentes

SCORES (para análise):
- Primeira escola do grupo: -1000 (define região principal)
- Mesma região principal: -500 (coesão mantida)
- Região diferente: +3 (quebra de coesão)
- Não alocado: +999999

ENTRADAS ESPERADAS:
df_alunos: Nome, Grupo, Sexo_Padrao, Cidade (opcional)
df_escolas: Escola, Numero_Regiao, F, M, F_1, M_1, F_2, M_2, JAN, JUL
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from collections import defaultdict

# Constantes de score
SCORE_PRIMEIRA_ESCOLA = -1000.0
SCORE_MESMA_REGIAO = -500.0
SCORE_OUTRA_REGIAO = 3.0
SCORE_NAO_ALOCADO = 999999.0


def alocar_estudantes(df_alunos: pd.DataFrame, df_escolas: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Função principal: aloca alunos em escolas seguindo regras de prioridade e coesão.
    
    Args:
        df_alunos: DataFrame com colunas Nome, Grupo, Sexo_Padrao, Cidade (opcional)
        df_escolas: DataFrame com informações de escolas e capacidades
        config: Dict com:
            - 'alunos_intake1': quantidade de alunos para Intake 1
            - 'ordem_grupos': lista de grupos por prioridade
            - 'agrupar_por_nome': bool, se True agrupa alunos com mesmo nome (padrão: False)
            - 'dispersar_por_cidade': bool, se True dispersa alunos da mesma cidade (padrão: False)
    
    Returns:
        DataFrame com alocações e scores
    """
    # Validações básicas
    _validar_colunas(df_alunos, df_escolas)
    
    # Passo 1: Distribuir alunos entre Intake 1 e 2
    df_com_intake = _distribuir_intakes(
        df_alunos.copy(),
        df_escolas.copy(),
        alunos_intake1=config.get('alunos_intake1', 0),
        ordem_grupos=config.get('ordem_grupos', list(df_alunos['Grupo'].unique()))
    )
    
    # Passo 2: Alocar alunos em escolas
    return _alocar_em_escolas(
        df_com_intake, 
        df_escolas.copy(),
        agrupar_por_nome=config.get('agrupar_por_nome', False),
        dispersar_por_cidade=config.get('dispersar_por_cidade', False)
    )


def _validar_colunas(df_alunos: pd.DataFrame, df_escolas: pd.DataFrame):
    """Valida se os DataFrames têm as colunas necessárias."""
    colunas_alunos = {'Nome', 'Grupo', 'Sexo_Padrao'}
    if not colunas_alunos.issubset(set(df_alunos.columns)):
        raise ValueError(f"df_alunos deve conter: {colunas_alunos}")
    
    if 'Numero_Regiao' not in df_escolas.columns:
        raise ValueError("df_escolas deve conter: Numero_Regiao")


def _distribuir_intakes(
    df_alunos: pd.DataFrame, 
    df_escolas: pd.DataFrame, 
    alunos_intake1: int, 
    ordem_grupos: List[str]
) -> pd.DataFrame:
    """
    Distribui alunos entre Intake 1 (Janeiro) e Intake 2 (Julho).
    
    Lógica:
    1. Calcula capacidade total por sexo em cada intake
    2. Ordena alunos por prioridade de grupo e nome
    3. RESPEITA RESTRIÇÕES: Alunos com Tem_Restricao_I1=True vão para Intake 2
    4. Aloca até atingir limite do Intake 1, depois vai para Intake 2
    """
    # Calcular capacidades por sexo em cada intake
    vagas_f1, vagas_m1 = _calcular_capacidade_por_sexo(df_escolas, intake=1)
    vagas_f2, vagas_m2 = _calcular_capacidade_por_sexo(df_escolas, intake=2)
    
    # Preparar DataFrame ordenado por prioridade
    df = df_alunos.copy()
    df['Ordem_Grupo'] = df['Grupo'].map({g: i for i, g in enumerate(ordem_grupos)})
    df['Ordem_Grupo'] = df['Ordem_Grupo'].fillna(len(ordem_grupos) + 1)
    df = df.sort_values(['Ordem_Grupo', 'Nome']).reset_index(drop=True)
    
    # Verificar se coluna de restrição existe
    tem_restricao = 'Tem_Restricao_I1' in df.columns
    
    # Distribuir entre intakes
    vagas_i1 = {'F': int(vagas_f1), 'M': int(vagas_m1)}
    vagas_i2 = {'F': int(vagas_f2), 'M': int(vagas_m2)}
    alvo_i1 = int(alunos_intake1)
    
    intakes = []
    contador_i1 = 0
    
    for _, aluno in df.iterrows():
        sexo = str(aluno['Sexo_Padrao']).upper()[0]
        
        # Verificar se aluno tem restrição para Intake 1
        tem_restricao_aluno = tem_restricao and aluno.get('Tem_Restricao_I1', False)
        
        if tem_restricao_aluno:
            # Aluno com restrição: DEVE ir para Intake 2
            if vagas_i2.get(sexo, 0) > 0:
                intakes.append(2)
                vagas_i2[sexo] -= 1
            else:
                # Sem vagas no Intake 2, não aloca
                intakes.append(0)
        else:
            # Tenta Intake 1 primeiro (se ainda não atingiu o alvo e tem vaga)
            if contador_i1 < alvo_i1 and vagas_i1.get(sexo, 0) > 0:
                intakes.append(1)
                vagas_i1[sexo] -= 1
                contador_i1 += 1
            # Senão, vai para Intake 2
            elif vagas_i2.get(sexo, 0) > 0:
                intakes.append(2)
                vagas_i2[sexo] -= 1
            # Sem vagas
            else:
                intakes.append(0)
    
    df['Intake'] = intakes
    return df


def _alocar_em_escolas(
    df_alunos: pd.DataFrame, 
    df_escolas: pd.DataFrame,
    agrupar_por_nome: bool = False,
    dispersar_por_cidade: bool = False
) -> pd.DataFrame:
    """
    Aloca alunos em escolas mantendo coesão de grupo quando possível.
    
    Lógica:
    1. Processa Intake 1, depois Intake 2
    2. Para cada grupo (por ordem de prioridade):
       - Opcionalmente agrupa alunos com mesmo nome
       - Opcionalmente dispersa alunos da mesma cidade
       - Tenta alocar na menor região disponível
       - Primeira alocação define "região principal" do grupo
       - Demais alunos tentam ir para região principal primeiro
       - Se não houver vaga, busca outras regiões
    """
    # Preparar resultado
    df_result = df_alunos.copy()
    df_result['Escola_Alocada'] = ''
    df_result['Regiao_Escola'] = 0
    df_result['Score_Match'] = 0.0
    df_result['Match_Tier'] = ''
    
    # Verificar se coluna Cidade existe
    tem_cidade = 'Cidade' in df_result.columns
    
    # Regiões em ordem crescente
    regioes = sorted(df_escolas['Numero_Regiao'].dropna().astype(int).unique())
    
    # Rastrear região principal de cada grupo
    regiao_principal: Dict[str, int] = {}
    
    # Processar cada intake
    for intake in [1, 2]:
        # Preparar capacidades disponíveis para este intake
        capacidades = _preparar_capacidades(df_escolas, intake)
        
        # Rastrear alocações por cidade e escola (para dispersão)
        cidade_escola_count = defaultdict(lambda: defaultdict(int))
        
        # Filtrar alunos deste intake e ordenar
        df_intake = df_result[df_result['Intake'] == intake].copy()
        df_intake = df_intake.sort_values(['Ordem_Grupo', 'Nome'])
        
        # Processar cada grupo
        for grupo, alunos_grupo in df_intake.groupby('Grupo', sort=False):
            # Aplicar ordenação especial se necessário
            alunos_grupo = _ordenar_alunos_grupo(
                alunos_grupo, 
                dispersar_por_nome=agrupar_por_nome,
                dispersar_por_cidade=dispersar_por_cidade and tem_cidade
            )
            
            # Para cada aluno do grupo
            for idx, aluno in alunos_grupo.iterrows():
                sexo = str(aluno['Sexo_Padrao']).upper()[0]
                cidade = str(aluno.get('Cidade', '')) if tem_cidade else ''
                
                # Definir ordem de regiões a tentar
                if grupo in regiao_principal:
                    # Tenta região principal primeiro, depois as outras
                    reg_principal = regiao_principal[grupo]
                    ordem_regioes = [reg_principal] + [r for r in regioes if r != reg_principal]
                else:
                    # Primeira alocação do grupo: tenta regiões em ordem crescente
                    ordem_regioes = regioes[:]
                
                # Tentar alocar em alguma região
                alocado = False
                for regiao in ordem_regioes:
                    escola_alocada = _tentar_alocar_em_regiao(
                        regiao, sexo, capacidades, df_escolas,
                        cidade=cidade if dispersar_por_cidade and tem_cidade else None,
                        cidade_escola_count=cidade_escola_count if dispersar_por_cidade and tem_cidade else None
                    )
                    
                    if escola_alocada:
                        # Sucesso! Registrar alocação
                        df_result.loc[idx, 'Escola_Alocada'] = escola_alocada
                        df_result.loc[idx, 'Regiao_Escola'] = regiao
                        
                        # Atualizar contador de cidade-escola
                        if dispersar_por_cidade and tem_cidade and cidade:
                            cidade_escola_count[cidade][escola_alocada] += 1
                        
                        # Calcular score e tier
                        if grupo not in regiao_principal:
                            # Primeira escola do grupo - define região principal
                            regiao_principal[grupo] = regiao
                            df_result.loc[idx, 'Match_Tier'] = 'primeira_escola'
                            df_result.loc[idx, 'Score_Match'] = SCORE_PRIMEIRA_ESCOLA
                        elif regiao == regiao_principal[grupo]:
                            # Mesma região principal - coesão mantida
                            df_result.loc[idx, 'Match_Tier'] = 'mesma_regiao'
                            df_result.loc[idx, 'Score_Match'] = SCORE_MESMA_REGIAO
                        else:
                            # Região diferente - quebra de coesão
                            df_result.loc[idx, 'Match_Tier'] = 'outra_regiao'
                            df_result.loc[idx, 'Score_Match'] = SCORE_OUTRA_REGIAO
                        
                        # Consumir vaga
                        capacidades[escola_alocada][sexo] -= 1
                        alocado = True
                        break
                
                if not alocado:
                    # Não conseguiu alocar
                    df_result.loc[idx, 'Match_Tier'] = 'nao_alocado'
                    df_result.loc[idx, 'Score_Match'] = SCORE_NAO_ALOCADO
    
    return df_result


def _ordenar_alunos_grupo(
    alunos_grupo: pd.DataFrame,
    dispersar_por_nome: bool = False,
    dispersar_por_cidade: bool = False
) -> pd.DataFrame:
    """
    Aplica ordenação especial aos alunos de um grupo.
    
    Args:
        alunos_grupo: DataFrame com alunos do grupo
        dispersar_por_nome: Se True, embaralha ordem aleatoriamente para dispersar nomes iguais
        dispersar_por_cidade: Se True, ordena para maximizar dispersão de cidades
    
    Returns:
        DataFrame reordenado
    """
    if not dispersar_por_nome and not dispersar_por_cidade:
        # Ordem alfabética padrão
        return alunos_grupo.sort_values('Nome')
    
    df = alunos_grupo.copy()
    
    if dispersar_por_nome:
        # Embaralha completamente a ordem para dispersar nomes iguais
        # Cada aluno recebe um número aleatório único
        np.random.seed(42)  # Para reprodutibilidade
        df['_ordem_aleatoria'] = np.random.random(len(df))
        df = df.sort_values('_ordem_aleatoria')
        df = df.drop(columns=['_ordem_aleatoria'])
    
    if dispersar_por_cidade:
        # Ordena para intercalar cidades diferentes
        # Cidades com mais alunos ficam mais espaçadas
        if 'Cidade' in df.columns:
            cidade_count = df['Cidade'].value_counts().to_dict()
            df['_ordem_cidade'] = df.groupby('Cidade').cumcount()
            df['_tamanho_cidade'] = df['Cidade'].map(cidade_count)
            # Ordena por: posição dentro da cidade, tamanho da cidade (desc), cidade
            df = df.sort_values(['_ordem_cidade', '_tamanho_cidade', 'Cidade'], ascending=[True, False, True])
            df = df.drop(columns=['_ordem_cidade', '_tamanho_cidade'])
    
    return df


def _tentar_alocar_em_regiao(
    regiao: int, 
    sexo: str, 
    capacidades: Dict, 
    df_escolas: pd.DataFrame,
    cidade: str = None,
    cidade_escola_count: Dict = None
) -> str:
    """
    Tenta alocar aluno em alguma escola da região.
    
    Se dispersar_por_cidade estiver ativo, prioriza escolas com menos alunos da mesma cidade.
    
    Args:
        regiao: Número da região
        sexo: 'F' ou 'M'
        capacidades: Dict com vagas disponíveis
        df_escolas: DataFrame com escolas
        cidade: Cidade do aluno (opcional, para dispersão)
        cidade_escola_count: Dict contando alunos por cidade e escola (opcional)
    
    Returns:
        Nome da escola se conseguiu alocar, string vazio caso contrário
    """
    # Escolas da região na ordem da planilha
    escolas_regiao = df_escolas[df_escolas['Numero_Regiao'] == regiao]['Escola'].tolist()
    
    # Filtrar escolas com vaga disponível
    escolas_com_vaga = [e for e in escolas_regiao if capacidades.get(e, {}).get(sexo, 0) > 0]
    
    if not escolas_com_vaga:
        return ''
    
    # Se dispersão por cidade estiver ativa e cidade for informada
    if cidade and cidade_escola_count is not None:
        # Ordenar escolas pela quantidade de alunos da mesma cidade (crescente)
        escolas_com_vaga.sort(key=lambda e: cidade_escola_count[cidade][e])
    
    # Retorna primeira escola disponível (ou a com menos alunos da cidade)
    return escolas_com_vaga[0]


def _preparar_capacidades(df_escolas: pd.DataFrame, intake: int) -> Dict:
    """
    Prepara dicionário com capacidades disponíveis por escola e sexo.
    
    Returns:
        Dict[escola] = {'F': vagas_fem, 'M': vagas_masc, 'Regiao': numero}
    """
    if intake == 1:
        col_f, col_m = 'F_1', 'M_1'
    else:
        col_f, col_m = 'F_2', 'M_2'
    
    capacidades = {}
    for _, escola in df_escolas.iterrows():
        nome = escola['Escola']
        
        # Usar colunas específicas do intake ou fallback para F/M gerais
        vagas_f = pd.to_numeric(escola.get(col_f, escola.get('F', 0)), errors='coerce')
        vagas_m = pd.to_numeric(escola.get(col_m, escola.get('M', 0)), errors='coerce')
        
        capacidades[nome] = {
            'F': int(vagas_f or 0),
            'M': int(vagas_m or 0),
            'Regiao': int(escola['Numero_Regiao'])
        }
    
    return capacidades


def _calcular_capacidade_por_sexo(df_escolas: pd.DataFrame, intake: int) -> Tuple[int, int]:
    """
    Calcula capacidade total por sexo para um intake.
    
    Returns:
        (vagas_femininas, vagas_masculinas)
    """
    if intake == 1:
        col_f, col_m, col_total = 'F_1', 'M_1', 'JAN'
    else:
        col_f, col_m, col_total = 'F_2', 'M_2', 'JUL'
    
    total_f, total_m = 0, 0
    
    for _, escola in df_escolas.iterrows():
        # Vagas totais do intake
        vagas_intake = pd.to_numeric(escola.get(col_total), errors='coerce')
        if pd.isna(vagas_intake):
            continue
        
        # Tentar usar colunas específicas do intake
        v_f = pd.to_numeric(escola.get(col_f), errors='coerce')
        v_m = pd.to_numeric(escola.get(col_m), errors='coerce')
        
        if pd.notna(v_f) and pd.notna(v_m):
            total_f += int(v_f)
            total_m += int(v_m)
        else:
            # Fallback: usar percentuais gerais
            perc_f = pd.to_numeric(escola.get('F'), errors='coerce')
            perc_m = pd.to_numeric(escola.get('M'), errors='coerce')
            
            if pd.notna(perc_f) and pd.notna(perc_m):
                total_f += int(np.round(vagas_intake * perc_f))
                total_m += int(np.round(vagas_intake * perc_m))
    
    return int(total_f), int(total_m)


# Manter compatibilidade com versão anterior
def calcular_capacidades_por_sexo(df_escolas: pd.DataFrame, intake: int) -> Tuple[int, int]:
    """Função legada - usar _calcular_capacidade_por_sexo."""
    return _calcular_capacidade_por_sexo(df_escolas, intake)