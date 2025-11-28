# -*- coding: utf-8 -*-
"""
GRIFFE HUB - Revisor de Matrículas v2.5
Sistema de revisão de formulários de matrícula
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Adicionar pasta backend ao path
# Tentar múltiplos caminhos para compatibilidade local e Streamlit Cloud
POSSIBLE_BACKEND_PATHS = [
    Path(__file__).parent.parent.parent / "backend",  # Local
    Path(__file__).parent.parent / "backend",          # Streamlit Cloud
    Path("/mount/src/griffe-hub/backend"),             # Streamlit Cloud absoluto
]

BACKEND_PATH = None
for path in POSSIBLE_BACKEND_PATHS:
    if path.exists():
        BACKEND_PATH = path
        break

if BACKEND_PATH is None:
    st.error("""
    ❌ **Pasta backend não encontrada**
    
    Caminhos testados:
    """)
    for path in POSSIBLE_BACKEND_PATHS:
        st.code(str(path))
    st.stop()

sys.path.insert(0, str(BACKEND_PATH))

try:
    from revisor_matriculas import (
        ExcelReader,
        FORM_MATRICULA_SECTIONS,
        FORM_INICIAL_SECTIONS,
        FORM_MEDICO_SECTIONS,
        UNIFIED_SECTIONS,
        get_field_label
    )
except ImportError as e:
    st.error(f"""
    ❌ **Erro ao importar módulos do backend**
    
    **Detalhes do erro:** {str(e)}
    
    **Caminho do backend usado:** `{BACKEND_PATH}`
    
    **Arquivos no backend:**
    """)
    
    if BACKEND_PATH.exists():
        try:
            files = list(BACKEND_PATH.rglob("*.py"))
            for f in files:
                st.code(str(f.relative_to(BACKEND_PATH)))
        except Exception as ex:
            st.error(f"Erro ao listar arquivos: {ex}")
    
    st.markdown("""
    **Possíveis soluções:**
    1. Verifique se a pasta `backend/revisor_matriculas` existe no repositório
    2. Confirme que os arquivos Python estão na pasta correta
    3. Verifique se há um arquivo `__init__.py` em `backend/revisor_matriculas/`
    4. No Streamlit Cloud, verifique se todos os arquivos foram commitados no Git
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

# Inicializar contador para chaves únicas
if 'button_counter' not in st.session_state:
    st.session_state.button_counter = 0

# ============================================================================
# MAPEAMENTO HIERÁRQUICO COMPLETO - TODOS OS CAMPOS
# ============================================================================

HIERARCHICAL_GROUPS = {
    "1️⃣ INFORMAÇÕES DO ALUNO": {
        "Dados Básicos": [
            ("NOME DO ESTUDANTE", "Matrícula"),
            ("SOBRENOME COMPLETO DO ESTUDANTE", "Matrícula"),
            ("DATA DE NASCIMENTO DO ESTUDANTE", "Matrícula"),
            ("SEXO DO ESTUDANTE", "Matrícula"),
            ("PAIS DE NASCIMENTO DO ESTUDANTE", "Matrícula"),
            ("CIDADE  DE NASCIMENTO DO ESTUDANTE", "Inicial"),
            ("ESTADO DE NASCIMENTO DO ESTUDANTE", "Inicial"),
            ("EMAIL DO ESTUDANTE", "Matrícula"),
            ("NUMERO DE TELEFONE DO ESTUDANTE (COM WHATSAPP)", "Inicial"),
            ("RACA/COR DO ESTUDANTE", "Inicial"),
            ("ESTADO CIVIL DO ESTUDANTE", "Inicial"),
            ("TAMANHO DE CAMISA QUE O ESTUDANTE VESTE?", "Matrícula"),
            ("TAMANHO DE JAQUETA QUE O ESTUDANTE VESTE?", "Inicial"),
            ("USA OCULOS?", "Matrícula"),
        ],
        "Documentos": [
            ("NUMERO DO CPF DO ESTUDANTE", "Inicial"),
            ("NUMERO DO RG DO ESTUDANTE", "Inicial"),
            ("DATA DE EMISSAO DO RG DO ESTUDANTE", "Inicial"),
            ("ORGAO EMISSOR + UF DO RG DO ESTUDANTE", "Inicial"),
        ],
        "Passaporte": [
            ("O ESTUDANTE POSSUI PASSAPORTE?", "Matrícula"),
            ("SE SIM, O PASSAPORTE DO ESTUDANTE ESTA VALIDO?", "Matrícula"),
            ("SE O ESTUDANTE TEM PASSAPORTE INFORME O NUMERO", "Matrícula"),
            ("SE O ESTUDANTE TEM PASSAPORTE INFORME A DATA DE VALIDADE", "Matrícula"),
            ("O ESTUDANTE POSSUI ALGUM VISTO?", "Matrícula"),
            ("VOCE JA VIAJOU PARA FORA DO PAIS?", "Matrícula"),
            ("SE SIM, ONDE VOCE JA VIAJOU?", "Matrícula"),
            ("VOCE TEM DUPLA NACIONALIDADE?", "Matrícula"),
        ],
        "Endereço": [
            ("CEP DO ENDERECO DE RESIDENCIA DO ESTUDANTE", "Inicial"),
            ("ENDERECO COMPLETO DE RESIDENCIA DO ESTUDANTE", "Inicial"),
        ],
    },
    "2️⃣ INFORMAÇÕES DA FAMÍLIA": {
        "Mãe": [
            ("NOME COMPLETO DA MAE", "Matrícula"),
            ("NUMERO DE TELEFONE DA MAE (COM WHATSAPP)", "Matrícula"),
            ("EMAIL DA MAE", "Matrícula"),
            ("NUMERO DO CPF DA MAE", "Matrícula"),
            ("PROFISSAO DA MAE", "Matrícula"),
            ("SUA MAE SE ENCAIXA EM ALGUMA DESSAS DESCRICOES?", "Matrícula"),
            ("DATA DE NASCIMENTO DA SUA MAE", "Matrícula"),
            ("ENDERECO DE RESIDENCIA DA SUA MAE", "Matrícula"),
        ],
        "Pai": [
            ("NOME COMPLETO DO PAI", "Matrícula"),
            ("NUMERO DE TELEFONE DO PAI (COM WHATSAPP)", "Matrícula"),
            ("EMAIL DO PAI", "Matrícula"),
            ("NUMERO DO CPF DO PAI", "Matrícula"),
            ("PROFISSAO DO PAI", "Matrícula"),
            ("SEU PAI SE ENCAIXA EM ALGUMA DESSAS DESCRICOES?", "Matrícula"),
            ("DATA DE NASCIMENTO DO SEU PAI", "Matrícula"),
            ("ENDERECO DE RESIDENCIA DO SEU PAI", "Matrícula"),
        ],
        "Irmãos": [
            ("VOCE TEM IRMAOS?", "Matrícula"),
            ("INFORME OS NOMES COMPLETOS DE CADA IRMAO, DATA DE NASCIMENTO SUAS RESPECTIVAS IDADES", "Matrícula"),
            ("IRMAO(A) 1 - RELACAO:", "Matrícula"),
            ("IRMAO(A) 1 - NOME COMPLETO:", "Matrícula"),
            ("IRMAO(A) 1 - DATA DE NASCIMENTO:", "Matrícula"),
            ("IRMAO(A) 1 - FALA INGLES?", "Matrícula"),
            ("IRMAO(A) 2 - RELACAO:", "Matrícula"),
            ("IRMAO(A) 2 - NOME COMPLETO:", "Matrícula"),
            ("IRMAO(A) 2 - DATA DE NASCIMENTO:", "Matrícula"),
            ("IRMAO(A) 2 - FALA INGLES?", "Matrícula"),
            ("CASO TENHA MAIS IRMAOS, INFORME RELACAO, OS NOMES COMPLETOS, DATA DE NASCIMENTO, E SE FALAM INGLES", "Matrícula"),
            ("SEUS IRMAOS MORAM COM VOCE NA MESMA CASA?", "Matrícula"),
        ],
        "Composição Familiar": [
            ("MEMBROS DA FAMILIA QUE MORAM COM VOCE:", "Matrícula"),
            ("MEMBRO 1 - RELACAO:", "Matrícula"),
            ("MEMBRO 1 - CASO TENHA PREENCHIDO OUTROS, FAVOR ESPECIFICAR ABAIXO:", "Matrícula"),
            ("MEMBRO 1 - NOME COMPLETO:", "Matrícula"),
            ("MEMBRO 1 - DATA DE NASCIMENTO:", "Matrícula"),
            ("MEMBRO 2 - RELACAO:", "Matrícula"),
            ("MEMBRO 2 - CASO TENHA PREENCHIDO OUTROS, FAVOR ESPECIFICAR ABAIXO:", "Matrícula"),
            ("MEMBRO 2 - NOME COMPLETO:", "Matrícula"),
            ("MEMBRO 2 - DATA DE NASCIMENTO:", "Matrícula"),
            ("CASO TENHA MAIS PESSOAS QUE MORAM COM VOCE, INFORME A RELACAO, OS NOMES COMPLETOS, DATA DE NASCIMENTO:", "Matrícula"),
            ("SEUS PAIS MORAM JUNTOS?", "Matrícula"),
            ("QUAL O STATUS DOS SEUS PAIS?", "Matrícula"),
            ("SEUS PAIS APOIAM O INTERCAMBIO?", "Matrícula"),
            ("CASO O RESPONSAVEL DO ESTUDANTE SEJA OUTRO MEMBRO DA FAMILIA OU APENAS UM DOS PAIS,  TEM A GUARDA DEFINITIVA OU ALVARA EM DOCUMENTO?", "Matrícula"),
        ],
    },
    "3️⃣ INFORMAÇÕES ACADÊMICAS": {
        "Idioma": [
            ("EM QUE IDIOMA VOCE SE COMUNICA DENTRO DE CASA?", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL O IDIOMA FALADO EM CASA:", "Matrícula"),
            ("VOCE FALA ALGUM OUTRO IDIOMA ALEM DO PORTUGUES?", "Matrícula"),
            ("CASO TENHA PREENCHIDO SIM ACIMA, ESPECIFIQUE QUAL O IDIOMA E O NIVEL DE FLUENCIA:", "Matrícula"),
            ("VOCE ESTUDA INGLES HA QUANTO TEMPO?", "Matrícula"),
            ("COMO VOCE AVALIA SEU NIVEL DE INGLES NO GERAL?", "Matrícula"),
        ],
        "Histórico Acadêmico": [
            ("VOCE GOSTA DE IR PARA ESCOLA?", "Matrícula"),
            ("SUAS TRES MATERIAS FAVORITAS", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL SUA MATERIA FAVORITA:", "Matrícula"),
            ("MARQUE OS PRINCIPAIS CURSOS QUE DESEJA FAZER NO INTERCAMBIO", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL OUTROS CURSOS QUE DESEJA FAZER NO INTERCAMBIO:", "Matrícula"),
            ("MARQUE OS CURSOS ELETIVOS QUE DESEJA FAZER", "Matrícula"),
            ("QUAL E O SEU PRINCIPAL MOTIVO PARA FAZER O INTERCAMBIO E ESCOLHER ESSES CURSOS?", "Matrícula"),
            ("CONTE QUAIS SAO SEUS PLANOS PARA O FUTURO", "Matrícula"),
        ],
        "Esportes": [
            ("VOCE PRATICA OU GOSTA DE ESPORTES?", "Matrícula"),
            ("QUAIS ESPORTES VOCE GOSTA OU PRATICA?", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL ESPORTE VOCE PRATICA OU GOSTA:", "Matrícula"),
            ("GOSTARIA DE PARTICIPAR DE ALGUM TIME ESCOLAR DURANTE O INTERCAMBIO?", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL O TIME ESCOLAR GOSTARIA DE PARTICIPAR:", "Matrícula"),
            ("QUAIS ATIVIDADES EXTRA CURRICULARES TE INTERESSAM?", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL ATIVIDADE EXTRACURRICULAR VOCE PARTICIPA OU GOSTA:", "Matrícula"),
        ],
        "Música e Artes": [
            ("VOCE GOSTA DE MUSICA E TEATRO?", "Matrícula"),
            ("VOCE TOCA ALGUM INSTRUMENTO MUSICAL?", "Matrícula"),
            ("SE SIM, QUAL INSTRUMENTO MUSICAL VOCE TOCA?", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL INSTRUMENTO VOCE TOCA:", "Matrícula"),
            ("VOCE CANTA OU GOSTA DE CANTAR?", "Matrícula"),
            ("VOCE GOSTARIA DE PARTICIPAR DE ALGUM GRUPO ARTISTICO DURANTE O INTERCAMBIO?", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL GRUPO ARTISTICO VOCE GOSTARIA DE PARTICIPAR:", "Matrícula"),
        ],
    },
    "4️⃣ HOMESTAY E ESTILO DE VIDA": {
        "Hobbies": [
            ("QUAIS SAO SEUS HOBBIES E INTERESSES", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAIS SEUS HOBBIES E INTERESSES:", "Matrícula"),
            ("DESCREVA UM POUCO MAIS SOBRE SEUS HOBBIES E O QUE GOSTA DE FAZER NO TEMPO LIVRE", "Matrícula"),
            ("O QUE VOCE GOSTA DE FAZER QUANDO SAI COM SEUS AMIGOS?", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL ATIVIDADE VOCE GOSTA DE FAZER COM SEUS AMIGOS:", "Matrícula"),
        ],
        "Alimentação": [
            ("PRECISA DE DIETA ESPECIAL? (ZERO LACTOSE, SEM OVOS, SEM GLUTEN, VEGANA, VEGETARIANA)", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTRA ACIMA, ESPECIFIQUE QUAL DIETA ESPECIAL VOCE SEGUE:", "Matrícula"),
            ("SE SEGUE ALGUMA DIETA ESPECIAL, EXPLIQUE O MOTIVO", "Matrícula"),
            ("ALIMENTOS QUE VOCE GOSTA DE COMER", "Matrícula"),
            ("CASO TENHA PREENCHIDO OUTROS ACIMA, ESPECIFIQUE QUAL ALIMENTO VOCE GOSTA:", "Matrícula"),
            ("CASO TENHA ALGUM, CITE ALIMENTOS QUE VOCE NAO GOSTA", "Matrícula"),
            ("VOCE TEM ALERGIA ALIMENTAR?", "Matrícula"),
            ("CASO TENHA ALGUMA ALERGIA ASSINALADA, FAVOR DAR MAIS INFORMACOES", "Matrícula"),
        ],
        "Preferências de Homestay": [
            ("VOCE PREFERE MORAR EM:", "Matrícula"),
            ("VOCE PREFERE UMA FAMILIA COM:", "Matrícula"),
            ("VOCE SE SENTE CONFORTAVEL EM MORAR COM OUTRO ESTUDANTE INTERNACIONAL?", "Matrícula"),
            ("VOCE GOSTA DE ANIMAIS DE ESTIMACAO?", "Matrícula"),
            ("VOCE FUMA?", "Matrícula"),
            ("VOCE SE SENTE BEM EM MORAR COM UMA FAMILIA QUE FUMA?", "Matrícula"),
        ],
        "Personalidade": [
            ("DESCREVA SUA PERSONALIDADE", "Matrícula"),
            ("QUAL O ESTILO DE FAMILIA QUE PREFERE", "Matrícula"),
            ("VOCE TEM ALGUMA TRADICAO FAMILIAR FAVORITA? SE SIM, QUAL?", "Matrícula"),
        ],
        "Rotina": [
            ("VOCE ARRUMA SEU QUARTO E SUA CAMA?", "Matrícula"),
            ("QUE HORAS COSTUMA FAZER A LICAO DE CASA?", "Matrícula"),
            ("QUANTO TEMPO POR DIA COSTUMA FICAR EM REDES SOCIAIS E NAVEGANDO NA INTERNET?", "Matrícula"),
            ("VOCE GOSTA DE ACORDAR CEDO?", "Matrícula"),
            ("QUE HORAS VOCE COSTUMA ACORDAR DURANTE A SEMANA?", "Matrícula"),
            ("QUE HORAS VOCE COSTUMA ACORDAR NO FINAL DE SEMANA?", "Matrícula"),
            ("QUANDO VOCE ACORDA, VOCE GOSTA DE:", "Matrícula"),
            ("QUE HORAS VOCE COSTUMA DORMIR DURANTE A SEMANA?", "Matrícula"),
            ("QUE HORAS VOCE COSTUMA DORMIR NO FINAL DE SEMANA?", "Matrícula"),
            ("DESCREVA SUA ROTINA DURANTE A SEMANA E NO FIM DE SEMANA", "Matrícula"),
            ("VOCE REALIZA ALGUMA TAREFA DOMESTICA? SE SIM, DESCREVA", "Matrícula"),
        ],
        "Religião": [
            ("RELIGIAO DO ESTUDANTE", "Matrícula"),
            ("COM QUE FREQUENCIA VOCE FREQUENTA SERVICOS RELIGIOSOS?", "Matrícula"),
            ("VOCE GOSTARIA DE FREQUENTAR SERVICOS RELIGIOSOS DURANTE O INTERCAMBIO?", "Matrícula"),
        ],
        "Expectativas": [
            ("VOCE JA FICOU MUITO TEMPO LONGE DA SUA FAMILIA? SE SIM, CONTE COMO FOI ESSA EXPERIENCIA", "Matrícula"),
            ("VOCE TEM MEDO DE FICAR TANTO TEMPO LONGE DE SUA FAMILIA? CONTE QUAIS SAO SEUS MEDOS E PREOCUPACOES", "Matrícula"),
            ("VOCE TEM ALGUMA PREOCUPACAO SOBRE MORAR NO EXTERIOR?", "Matrícula"),
            ("SE SIM, DESCREVA SUAS PREOCUPACOES", "Matrícula"),
            ("O QUE VOCE ESPERA DO INTERCAMBIO?", "Matrícula"),
            ("O QUE VOCE GOSTARIA DE COMPARTILHAR DA SUA CULTURA NESSE INTERCAMBIO?", "Matrícula"),
        ],
        "Informações Adicionais": [
            ("VOCE TEM ALGUM HISTORICO DE COMPORTAMENTO CRIMINAL?", "Matrícula"),
            ("VOCE TEM HISTORICO DE CONDUTA SEXUAL INADEQUADA?", "Matrícula"),
            ("HA ALGO MAIS QUE VOCE GOSTARIA QUE SOUBESSEMOS SOBRE VOCE?", "Matrícula"),
        ],
    },
    "5️⃣ INFORMAÇÕES MÉDICAS": {
        "Condições de Saúde Geral": [
            ("VOCE TEM ALGUM PROBLEMA DE SAUDE?", "Médico"),
            ("SE SIM, DESCREVA SUA(S) CONDICAO(OES) DE SAUDE:", "Médico"),
            ("VOCE POSSUI ALGUM LAUDO MEDICO SOBRE SUA CONDICAO DE SAUDE?", "Médico"),
            ("SE O ESTUDANTE POSSUI ALGUMA DOENCA CRONICA OU CONDICAO DE SAUDE FISICA OU MENTAL RELEVANTE, ESPECIFIQUE ABAIXO", "Inicial"),
        ],
        "Histórico de Saúde": [
            ("CONDICOES DE SAUDE (ATUAIS OU PASSADAS)", "Médico"),
            ("CASO TENHA PREENCHIDO OUTRA CONDICAO RELEVANTE ACIMA, ESPECIFIQUE QUAL CONDICAO VOCE TEM OU TEVE:", "Médico"),
        ],
        "Alergias": [
            ("VOCE TEM ALGUM TIPO DE ALERGIA?", "Médico"),
            ("CASO TENHA ALGUMA ALERGIA ASSINALADA, FAVOR DAR MAIS INFORMACOES", "Médico"),
            ("SE O ESTUDANTE POSSUI ALGUM TIPO DE ALERGIA, ESPECIFIQUE ABAIXO", "Médico"),
            ("SE O ESTUDANTE POSSUI ALGUM TIPO DE ALERGIA, ESPECIFIQUE ABAIXO", "Inicial"),
        ],
        "Atividade Física": [
            ("VOCE TEM ALGUMA RESTRICAO A ATIVIDADE FISICA?", "Médico"),
            ("SE SIM, ESPECIFIQUE SUAS RESTRICOES PARA ATIVIDADE FISICA:", "Médico"),
        ],
        "Sono e Dor": [
            ("VOCE TEM ALGUM DISTURBIO DO SONO?", "Médico"),
            ("CASO TENHA PREENCHIDO QUE POSSUI ALGUM DISTURBIO DO SONO, ESPECIFIQUE:", "Médico"),
            ("VOCE SOFRE DE ENXAQUECAS OU DORES DE CABECA FREQUENTES?", "Médico"),
            ("CASO TENHA PREENCHIDO QUE POSSUI ALGUM ENXAQUECAS OU DORES DE CABECA FREQUENTES, ESPECIFIQUE:", "Médico"),
            ("(APENAS PARA MULHERES) VOCE SENTE COLICAS MENSTRUAIS INTENSAS?", "Médico"),
            ("CASO TENHA PREENCHIDO QUE SENTE COLICAS MENTRUAIS INTENSAS, ESPECIFIQUE:", "Médico"),
        ],
        "Acompanhamento Profissional": [
            ("VOCE FAZ OU FEZ ALGUM ACOMPANHAMENTO COM ALGUM PROFISSIONAL DA SAUDE?", "Médico"),
            ("SE SIM, PORQUE VOCE PRECISA DESSE ACOMPANHAMENTO?", "Médico"),
        ],
        "Vacinação": [
            ("VOCE FOI VACINADO CONTRA O COVID?", "Médico"),
            ("TIPO DE VACINA COVID-19:", "Médico"),
            ("CASO TENHA PREENCHIDO OUTRA VACINA DE COVID-19, ESPECIFIQUE:", "Médico"),
            ("VOCE RECEBEU AS SEGUINTES VACINAS?", "Médico"),
            ("CASO TENHA PREENCHIDO OUTRA VACINA, ESPECIFIQUE:", "Médico"),
        ],
        "Saúde Mental": [
            ("VOCE JA FOI DIAGNOSTICADO OU TRATADO POR ALGUMA CONDICAO DE SAUDE MENTAL?", "Médico"),
            ("CASO TENHA PREENCHIDO OUTRAS CONDICOES DE SAUDE MENTAL, ESPECIFIQUE:", "Médico"),
            ("SE SIM, MARQUE AS CONDICOES QUE SE APLICAM:", "Médico"),
            ("CASO TENHA ALGUMA CONDICAO DE SAUDE MENTAL, DESCREVA SEU TRATAMENTO DE SAUDE MENTAL E STATUS ATUAL:", "Médico"),
        ],
        "Aprendizagem": [
            ("VOCE TEM UM DIAGNOSTICO DE DIFICULDADE DE APRENDIZAGEM OU CONDICAO NEURODIVERGENTE (EX.: TDAH, DISLEXIA, AUTISMO)?", "Médico"),
            ("CASO TENHA ALGUMA DIFICULDADE DE APRENDIZAGEM OU CONDICAO NEURODIVERGENTE, ESPECIFIQUE E DESCREVA QUAISQUER ACOMODACOES OU SUPORTE NECESSARIO:", "Médico"),
        ],
        "Desafios Sociais": [
            ("VOCE TEM ALGUM DESAFIO SOCIAL OU COMPORTAMENTAL (EX.: TRANSTORNO DO ESPECTRO AUTISTA, TRANSTORNO DE CONDUTA)?", "Médico"),
            ("CASO TENHA ALGUM DESAFIO SOCIAL OU COMPORTAMENTAL, DESCREVA SEUS DESAFIOS E QUALQUER SUPORTE NECESSARIO:", "Médico"),
        ],
        "Medicamentos": [
            ("VOCE FAZ USO DE ALGUM MEDICAMENTO DE FORMA CONTINUA (TODOS OS DIAS)?", "Médico"),
            ("SE SIM, LISTE O MEDICAMENTO, DOSAGEM E FREQUENCIA:", "Médico"),
            ("MEDICAMENTO QUE USA EM CASO DE DOR DE CABECA", "Médico"),
            ("MEDICAMENTO QUE USA EM CASO DE FEBRE", "Médico"),
            ("MEDICAMENTO QUE USA EM CASO DE NAUSEA/VOMITOS", "Médico"),
            ("MEDICAMENTO QUE USA EM CASO DE TOSSE PERSISTENTE", "Médico"),
            ("MEDICAMENTO QUE USA EM CASO DE DIARREIA", "Médico"),
            ("MEDICAMENTO QUE USA EM CASO DE DOR MUSCULAR", "Médico"),
            ("MEDICAMENTO QUE USO EM CASO DE DESCONFORTO ABDOMINAL", "Médico"),
            ("(APENAS PARA MULHERES) MEDICAMENTO QUE USO PARA COLICA MENSTRUAL", "Médico"),
            ("VOCE PRECISARA TOMAR MEDICAMENTO DURANTE O HORARIO ESCOLAR?", "Médico"),
            ("CASO PRECISE TOMAR MEDICAMENTO NO HORARIO ESCOLAR, VOCE PRECISA DE AJUDA PARA ADMINISTRAR SEU MEDICAMENTO?", "Médico"),
            ("SE SIM, DESCREVA O HORARIO DA MEDICACAO E O TIPO DE AJUDA NECESSARIA:", "Médico"),
        ],
        "Outras Informações": [
            ("HA ALGUMA OUTRA INFORMACAO DE SAUDE QUE VOCE GOSTARIA DE COMPARTILHAR?", "Médico"),
        ],
    },
    "6️⃣ ANEXOS": {
        "Formulário Inicial": [
            ("ANEXO: FOTO FRENTE E VERSO DO RG E CPF DO ESTUDANTE", "Inicial"),
            ("ANEXO: FOTO FRENTE E VERSO DO RG E CPF DA MAE DO ESTUDANTE", "Inicial"),
            ("ANEXO: FOTO FRENTE E VERSO DO RG E CPF DO PAI DO ESTUDANTE", "Inicial"),
            ("ANEXO: COMPROVANTE DE ENDERECO DO ESTUDANTE", "Inicial"),
            ("ANEXO: EM CASO DE SEUS PAIS FALECIDOS, ANEXAR A CERTIDAO DE OBITO", "Inicial"),
            ("ANEXO: CASO O RESPONSAVEL DO ESTUDANTE SEJA OUTRO MEMBRO DA FAMILIA OU UM DOS PAIS E O MESMO TENHA GUARDA OU ALVARA ANEXAR O DOCUMENTO", "Inicial"),
            ("ANEXO: EM CASO DO ESTUDANTE JA POSSUIR PASSAPORTE ANEXAR PAGINA DA FOTO COM O NUMERO DO PASSAPORTE", "Inicial"),
        ],
        "Formulário de Matrícula": [
            ("ANEXO: FOTO DO ROSTO DO ESTUDANTE (ESTILO 3X4)", "Matrícula"),
            ("ANEXO: COMPROVANTE DE RESIDENCIA DA SUA MAE", "Matrícula"),
            ("ANEXO: COMPROVANTE DE RESIDENCIA DO SEU PAI", "Matrícula"),
            ("ANEXO: ANEXE AQUI SEU RELATORIO MEDICO QUE COMPROVE SUA NECESSIDADE DE DIETA ESPECIAL ( PARA OS ALUNOS QUE TEM RESTRICOES ALIMETARES OU ALERGIA COMPROVADO PELO MEDICO) .", "Matrícula"),
            ("ANEXO: EM CASO DO ESTUDANTE JA POSSUIR PASSAPORTE ANEXAR PAGINA DA FOTO COM O NUMERO DO PASSAPORTE", "Matrícula"),
            ("ANEXO: HISTORICO ESCOLAR DO ANO DE 2023", "Matrícula"),
            ("ANEXO: HISTORICO/BOLETIM ESCOLAR DO ANO DE 2024", "Matrícula"),
            ("ANEXO: BOLETIM ATUALIZADO DE 2025", "Matrícula"),
            ("ANEXO: TERMO DE PARTICIPACAO/COMPROMISSO GRIFFE", "Matrícula"),
            ("ANEXO: CARTA PARA FAMILIA ANFITRIA EM INGLES", "Matrícula"),
            ("ANEXO: ALBUM DE FOTOS DO ESTUDANTE", "Matrícula"),
        ],
        "Formulário Médico": [
            ("ANEXO: ANEXE AQUI SEU RELATORIO DE SAUDE (RELATORIO MEDICO QUE COMPROVE SUA CONDICAO DE SAUDE)  OBS: NESSE RELATORIO DEVE CONTER SEU DIAGNOSTICO COM CID, TIPO DE ACOMPANHAMENTO, O QUE EXACERBA SUA CONDICAO DE SAUDE E MEDICAMENTOS USADOS DE FORMA CONTINUA E EM CRISES.", "Médico"),
            ("ANEXO: ANEXE AQUI SEU RELATORIO MEDICO QUE COMPROVE SUA ALERGIA.", "Médico"),
            ("ANEXO: COMPROVANTE DE VACINACAO COVID-19", "Médico"),
            ("ANEXO: HISTORICO DE VACINACAO  (ANEXE AQUI SEU CARTAO DE VACINA, FRENTE E VERSO, DECLARACAO DE VACINA QUE VOCE JA TENHA TOMADO EMITIDO PELO CONECT SUS)", "Médico"),
            ("ANEXO: ANEXE AQUI SUA RECEITA DE MEDICAMENTOS", "Médico"),
        ],
    },
}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def format_value(value):
    """Formata valor para exibição"""
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%B %d, %Y")  # January 1, 2010
    return str(value)


def normalize_text(text):
    """Normaliza texto para busca (remove acentos)"""
    if not text:
        return ""
    text = str(text).lower()
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def render_field_compact(label, value, source=""):
    """Renderiza um campo de forma compacta com badge de fonte"""
    formatted_value = format_value(value)
    
    is_link = formatted_value and (
        formatted_value.startswith('http://') or 
        formatted_value.startswith('https://')
    )
    
    # Badge com a fonte do dado
    source_badge = ""
    if source:
        color_map = {
            "Matrícula": "#0066cc",
            "Inicial": "#00a86b", 
            "Médico": "#dc3545"
        }
        color = color_map.get(source, "#6c757d")
        source_badge = f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px; margin-left: 8px;">{source}</span>'
    
    st.markdown(f"**{label}**{source_badge}", unsafe_allow_html=True)
    
    if formatted_value:
        if is_link:
            st.markdown(
                f'<div style="background-color: #d4edda; padding: 8px; '
                f'border-radius: 5px; margin-bottom: 8px; margin-top: 4px; color: #155724;">'
                f'<a href="{formatted_value}" target="_blank" style="color: #155724; text-decoration: none;">'
                f'🔗 Abrir Documento</a>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="background-color: #f8f9fa; padding: 8px; '
                f'border-radius: 5px; margin-bottom: 8px; margin-top: 4px; '
                f'border-left: 3px solid #dee2e6; color: #000000;">{formatted_value}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f'<div style="background-color: #fff3cd; padding: 8px; '
            f'border-radius: 5px; margin-bottom: 8px; margin-top: 4px; color: #856404;">'
            f'<em>Não preenchido</em></div>',
            unsafe_allow_html=True
        )


def render_field(label, value, key):
    """Renderiza um campo com botão de copiar"""
    formatted_value = format_value(value)
    
    is_link = formatted_value and (
        formatted_value.startswith('http://') or 
        formatted_value.startswith('https://')
    )
    
    if label.upper().startswith('ANEXO'):
        st.markdown(f"**📎 {label.replace('ANEXO:', '').strip()}**")
        
        if is_link:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f'<div style="background-color: #d4edda; padding: 10px; '
                    f'border-radius: 5px; margin-bottom: 10px; color: #155724;">'
                    f'<a href="{formatted_value}" target="_blank" style="color: #155724; text-decoration: none;">'
                    f'🔗 Abrir Documento</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col2:
                st.session_state.button_counter += 1
                if st.button("📋", key=f"copy_{st.session_state.button_counter}", 
                           use_container_width=True, help="Copiar link"):
                    st.code(formatted_value, language=None)
        elif formatted_value:
            st.markdown(
                f'<div style="background-color: #f0f2f6; color: #000000; padding: 10px; '
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
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{label}**")
            
            if formatted_value:
                if is_link:
                    st.markdown(
                        f'<div style="background-color: #d4edda; padding: 10px; '
                        f'border-radius: 5px; margin-bottom: 10px; color: #155724;">'
                        f'<a href="{formatted_value}" target="_blank" style="color: #155724;">'
                        f'🔗 {formatted_value}</a>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="background-color: #f0f2f6; padding: 10px; '
                        f'border-radius: 5px; margin-bottom: 10px; color: #000000;">{formatted_value}</div>',
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
                st.session_state.button_counter += 1
                if st.button("📋", key=f"copy_{st.session_state.button_counter}", 
                           use_container_width=True, help="Clique para copiar"):
                    st.code(formatted_value, language=None)


def render_section(section_title, fields, data, form_type):
    """Renderiza uma seção do formulário"""
    st.markdown(f"### {section_title}")
    st.markdown("---")
    
    for field in fields:
        value = data.get(field, "")
        key = f"{form_type}_{field}_{section_title}_{st.session_state.button_counter}"
        
        label = get_field_label(field)
        render_field(label, value, key)
    
    st.markdown("<br>", unsafe_allow_html=True)


def create_hierarchical_view(student_data):
    """Cria visualização hierárquica com grupos e subseções"""
    
    # Botões globais
    col1, col2, col_space = st.columns([1, 1, 3])
    with col1:
        if st.button("📂 Expandir Tudo", use_container_width=True, type="primary"):
            for grupo in HIERARCHICAL_GROUPS.keys():
                st.session_state[f"expand_{grupo}"] = True
            st.rerun()
    with col2:
        if st.button("📁 Colapsar Tudo", use_container_width=True):
            for grupo in HIERARCHICAL_GROUPS.keys():
                st.session_state[f"expand_{grupo}"] = False
            st.rerun()
    
    st.markdown("---")
    
    # Renderizar cada grupo
    for grupo_nome, subsecoes in HIERARCHICAL_GROUPS.items():
        # Contar campos preenchidos no grupo
        total_fields = 0
        filled_fields = 0
        
        for subsecao_nome, campos in subsecoes.items():
            for field_name, source in campos:
                total_fields += 1
                source_key = {'Matrícula': 'matricula', 'Inicial': 'inicial', 'Médico': 'medico'}.get(source, '')
                value = student_data.get(source_key, {}).get(field_name, "")
                if format_value(value):
                    filled_fields += 1
        
        # Calcular porcentagem
        percent = round((filled_fields / total_fields) * 100, 1) if total_fields > 0 else 0
        
        # Determinar cor
        if percent >= 80:
            indicator = "✅"
            color = "#28a745"
        elif percent >= 50:
            indicator = "🟡"
            color = "#ffc107"
        elif percent > 0:
            indicator = "🟠"
            color = "#fd7e14"
        else:
            indicator = "⚪"
            color = "#6c757d"
        
        # Header do grupo
        col_title, col_stats, col_btn = st.columns([5, 2, 2])
        
        with col_title:
            st.markdown(f"## {grupo_nome}")
        
        with col_stats:
            st.markdown(f"""
            <div style="text-align: right; padding-top: 8px;">
                <span style="color: {color}; font-size: 1.2rem;">{indicator}</span>
                <span style="font-weight: 600; font-size: 1.1rem; color: {color};">{percent}%</span>
                <span style="color: #666; font-size: 0.9rem;"> ({filled_fields}/{total_fields})</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_btn:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📂", key=f"open_{grupo_nome}", use_container_width=True, help="Abrir"):
                    st.session_state[f"expand_{grupo_nome}"] = True
                    st.rerun()
            with col_b:
                if st.button("📁", key=f"close_{grupo_nome}", use_container_width=True, help="Fechar"):
                    st.session_state[f"expand_{grupo_nome}"] = False
                    st.rerun()
        
        st.markdown("---")
        
        # Renderizar subseções do grupo
        is_expanded = st.session_state.get(f"expand_{grupo_nome}", False)
        
        for subsecao_nome, campos in subsecoes.items():
            with st.expander(f"📌 {subsecao_nome}", expanded=is_expanded):
                for field_name, source in campos:
                    source_key = {'Matrícula': 'matricula', 'Inicial': 'inicial', 'Médico': 'medico'}.get(source, '')
                    value = student_data.get(source_key, {}).get(field_name, "")
                    label = get_field_label(field_name)
                    render_field_compact(label, value, source)
        
        st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# HEADER
# ============================================================================

st.title("📋 Revisor de Matrículas")
st.markdown("Sistema de Revisão de Formulários de Matrícula")
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
    1. **Upload** da planilha Excel
    2. **Busque** digitando o nome
    3. **Selecione** o aluno
    4. **Use** os botões 📂/📁
    
    ---
    
    ### ✨ v2.5:
    - Busca incremental
    - 6 grupos organizados
    - Botões expandir/colapsar
    - TODOS os campos mapeados
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
    help="Arquivo deve conter: Form_Matrícula, Form_Inicial, Form_Médico"
)

if uploaded_file:
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        with st.spinner("Carregando dados da planilha..."):
            # Verificar sheets disponíveis
            xls = pd.ExcelFile(tmp_path)
            available_sheets = xls.sheet_names
            st.info(f"📊 Sheets encontradas: {', '.join(available_sheets)}")
            
            reader = ExcelReader(tmp_path)
            if reader.load_data():
                st.success(f"✅ Planilha carregada! {len(reader.get_students())} estudantes encontrados.")
                st.session_state['reader'] = reader
                st.session_state['students'] = reader.get_students()
            else:
                st.error("❌ Erro ao carregar planilha. Verifique se as sheets estão corretas.")
                st.info(f"**Sheets esperadas:** Form_Inicial, Form_Matrícula, Form_Médico")
                st.info(f"**Sheets encontradas:** {', '.join(available_sheets)}")
    except Exception as e:
        st.error(f"❌ Erro ao processar planilha: {str(e)}")
        st.exception(e)

# ============================================================================
# SELEÇÃO DE ALUNO E VISUALIZAÇÃO
# ============================================================================

if 'students' in st.session_state and st.session_state['students']:
    st.markdown("---")
    st.header("🔍 Busca de Aluno")
    
    col_search, col_clear = st.columns([5, 1])
    
    with col_search:
        search_term = st.text_input(
            "Digite parte do nome ou email:",
            key="search_input",
            placeholder="Ex: João Silva"
        )
    
    with col_clear:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state['search_input'] = ""
            st.rerun()
    
    # Filtrar estudantes
    filtered_students = [
        s for s in st.session_state['students']
        if not search_term or 
        normalize_text(search_term) in normalize_text(s['nome']) or
        normalize_text(search_term) in normalize_text(s.get('email', ''))
    ]
    
    st.caption(f"📊 {len(filtered_students)} de {len(st.session_state['students'])} estudantes")
    
    if filtered_students:
        student_options = [
            f"{s['nome']} ({s['email']})" if s.get('email') else s['nome']
            for s in filtered_students
        ]
        
        selected_index = st.selectbox(
            "Selecione um aluno:",
            range(len(student_options)),
            format_func=lambda i: student_options[i]
        )
        
        if selected_index is not None:
            selected_student = filtered_students[selected_index]
            nome = selected_student['nome']
            email = selected_student.get('email', '')
            
            st.markdown("---")
            
            reader = st.session_state['reader']
            student_data = reader.get_student_data(nome, email)
            
            # Informações principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                grupo = student_data['matricula'].get('GRUPO', 
                       student_data['inicial'].get('GRUPO', 'N/A'))
                st.metric("Grupo", grupo)
            
            with col2:
                programa = student_data['matricula'].get('PROGRAMA', 
                          student_data['inicial'].get('PROGRAMA', 'N/A'))
                st.metric("Programa", programa)
            
            with col3:
                status = student_data['matricula'].get('STATUS', 
                        student_data['inicial'].get('STATUS',
                        student_data['medico'].get('STATUS', 'N/A')))
                st.metric("Status", status)
            
            st.markdown("---")
            
            # Criar tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔍 Visão Hierárquica",
                "📝 Form Matrícula", 
                "📄 Form Inicial", 
                "🏥 Form Médico"
            ])
            
            with tab1:
                st.info("💡 Use os botões 📂 Abrir / 📁 Fechar para controlar os grupos")
                create_hierarchical_view(student_data)
            
            with tab2:
                st.header("📝 Formulário de Matrícula")
                if student_data['matricula']:
                    for section_title, fields in FORM_MATRICULA_SECTIONS.items():
                        with st.expander(section_title, expanded=False):
                            render_section(section_title, fields, student_data['matricula'], 'matricula')
                else:
                    st.warning("⚠️ Nenhum dado encontrado")
            
            with tab3:
                st.header("📄 Formulário Inicial")
                if student_data['inicial']:
                    for section_title, fields in FORM_INICIAL_SECTIONS.items():
                        with st.expander(section_title, expanded=False):
                            render_section(section_title, fields, student_data['inicial'], 'inicial')
                else:
                    st.warning("⚠️ Nenhum dado encontrado")
            
            with tab4:
                st.header("🏥 Formulário Médico")
                if student_data['medico']:
                    for section_title, fields in FORM_MEDICO_SECTIONS.items():
                        with st.expander(section_title, expanded=False):
                            render_section(section_title, fields, student_data['medico'], 'medico')
                else:
                    st.warning("⚠️ Nenhum dado encontrado")
    else:
        st.warning("⚠️ Nenhum estudante encontrado.")

st.markdown("---")
st.caption("📋 Revisor de Matrículas v2.5 | Griffe Turismo")