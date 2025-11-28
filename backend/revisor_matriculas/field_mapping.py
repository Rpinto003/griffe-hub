# -*- coding: utf-8 -*-
"""
Mapeamento de campos para exibição organizada
Baseado na estrutura dos formulários reais
"""

# Mapeamento de campos do formulário de matrícula (Atlantic/NSISP)
# Organizado na ordem de preenchimento dos formulários
FORM_MATRICULA_SECTIONS = {
    "Section 1 - Student Information": [
        "NOME DO ESTUDANTE",
        "SOBRENOME COMPLETO DO ESTUDANTE",
        "DATA DE NASCIMENTO DO ESTUDANTE",
        "SEXO DO ESTUDANTE",
        "PAIS DE NASCIMENTO DO ESTUDANTE",
        "EMAIL DO ESTUDANTE",
    ],
    
    "Section 2 - Passport Information": [
        "O ESTUDANTE POSSUI PASSAPORTE?",
        "SE SIM, O PASSAPORTE DO ESTUDANTE ESTA VALIDO?",
        "SE O ESTUDANTE TEM PASSAPORTE INFORME O NUMERO",
        "SE O ESTUDANTE TEM PASSAPORTE INFORME A DATA DE VALIDADE",
        "O ESTUDANTE POSSUI ALGUM VISTO?",
    ],
    
    "Section 3 - Parent One Information": [
        "NOME COMPLETO DA MAE",
        "NUMERO DE TELEFONE DA MAE (COM WHATSAPP)",
        "EMAIL DA MAE",
        "NUMERO DO CPF DA MAE",
        "PROFISSAO DA MAE",
        "DATA DE NASCIMENTO DA SUA MAE",
        "ENDERECO DE RESIDENCIA DA SUA MAE",
    ],
    
    "Section 4 - Parent Two Information": [
        "NOME COMPLETO DO PAI",
        "NUMERO DE TELEFONE DO PAI (COM WHATSAPP)",
        "EMAIL DO PAI",
        "NUMERO DO CPF DO PAI",
        "PROFISSAO DO PAI",
        "DATA DE NASCIMENTO DO SEU PAI",
        "ENDERECO DE RESIDENCIA DO SEU PAI",
    ],
    
    "Section 5 - Language and Communication": [
        "EM QUE IDIOMA VOCE SE COMUNICA DENTRO DE CASA?",
        "VOCE FALA ALGUM OUTRO IDIOMA ALEM DO PORTUGUES?",
        "VOCE ESTUDA INGLES HA QUANTO TEMPO?",
        "COMO VOCE AVALIA SEU NIVEL DE INGLES NO GERAL?",
    ],
    
    "Section 6 - Academic History": [
        "VOCE GOSTA DE IR PARA ESCOLA?",
        "SUAS TRES MATERIAS FAVORITAS",
        "MARQUE OS PRINCIPAIS CURSOS QUE DESEJA FAZER NO INTERCAMBIO",
        "MARQUE OS CURSOS ELETIVOS QUE DESEJA FAZER",
        "CONTE QUAIS SAO SEUS PLANOS PARA O FUTURO",
    ],
    
    "Section 7 - Sports and Activities": [
        "VOCE PRATICA OU GOSTA DE ESPORTES?",
        "QUAIS ESPORTES VOCE GOSTA OU PRATICA?",
        "GOSTARIA DE PARTICIPAR DE ALGUM TIME ESCOLAR DURANTE O INTERCAMBIO?",
        "QUAIS ATIVIDADES EXTRA CURRICULARES TE INTERESSAM?",
    ],
    
    "Section 8 - Music and Arts": [
        "VOCE GOSTA DE MUSICA E TEATRO?",
        "VOCE TOCA ALGUM INSTRUMENTO MUSICAL?",
        "VOCE CANTA OU GOSTA DE CANTAR?",
        "VOCE GOSTARIA DE PARTICIPAR DE ALGUM GRUPO ARTISTICO DURANTE O INTERCAMBIO?",
    ],
    
    "Section 9 - Hobbies and Interests": [
        "QUAIS SAO SEUS HOBBIES E INTERESSES",
        "DESCREVA UM POUCO MAIS SOBRE SEUS HOBBIES E O QUE GOSTA DE FAZER NO TEMPO LIVRE",
        "O QUE VOCE GOSTA DE FAZER QUANDO SAI COM SEUS AMIGOS?",
    ],
    
    "Section 10 - Diet and Nutrition": [
        "PRECISA DE DIETA ESPECIAL? (ZERO LACTOSE, SEM OVOS, SEM GLUTEN, VEGANA, VEGETARIANA)",
        "ALIMENTOS QUE VOCE GOSTA DE COMER",
        "CASO TENHA ALGUM, CITE ALIMENTOS QUE VOCE NAO GOSTA",
        "VOCE TEM ALERGIA ALIMENTAR?",
    ],
    
    "Section 11 - Homestay Preferences": [
        "VOCE PREFERE MORAR EM:",
        "VOCE PREFERE UMA FAMILIA COM:",
        "VOCE SE SENTE CONFORTAVEL EM MORAR COM OUTRO ESTUDANTE INTERNACIONAL?",
        "VOCE GOSTA DE ANIMAIS DE ESTIMACAO?",
        "VOCE FUMA?",
        "VOCE SE SENTE BEM EM MORAR COM UMA FAMILIA QUE FUMA?",
    ],
    
    "Section 12 - Personality and Lifestyle": [
        "DESCREVA SUA PERSONALIDADE",
        "QUAL O ESTILO DE FAMILIA QUE PREFERE",
        "VOCE TEM ALGUMA TRADICAO FAMILIAR FAVORITA? SE SIM, QUAL?",
    ],
    
    "Section 13 - Routine and Habits": [
        "VOCE ARRUMA SEU QUARTO E SUA CAMA?",
        "QUE HORAS COSTUMA FAZER A LICAO DE CASA?",
        "QUANTO TEMPO POR DIA COSTUMA FICAR EM REDES SOCIAIS E NAVEGANDO NA INTERNET?",
        "QUE HORAS VOCE COSTUMA DORMIR DURANTE A SEMANA?",
        "DESCREVA SUA ROTINA DURANTE A SEMANA E NO FIM DE SEMANA",
    ],
    
    "Section 14 - Religion and Spirituality": [
        "RELIGIAO DO ESTUDANTE",
        "COM QUE FREQUENCIA VOCE FREQUENTA SERVICOS RELIGIOSOS?",
        "VOCE GOSTARIA DE FREQUENTAR SERVICOS RELIGIOSOS DURANTE O INTERCAMBIO?",
    ],
    
    "Section 15 - Family Information": [
        "VOCE TEM IRMAOS?",
        "SEUS IRMAOS MORAM COM VOCE NA MESMA CASA?",
        "SEUS PAIS MORAM JUNTOS?",
        "QUAL O STATUS DOS SEUS PAIS?",
        "SEUS PAIS APOIAM O INTERCAMBIO?",
    ],
    
    "Section 16 - Documents and Attachments": [
        "ANEXO: FOTO DO ROSTO DO ESTUDANTE (ESTILO 3X4)",
        "ANEXO: COMPROVANTE DE RESIDENCIA DA SUA MAE",
        "ANEXO: COMPROVANTE DE RESIDENCIA DO SEU PAI",
        "ANEXO: ANEXE AQUI SEU RELATORIO MEDICO QUE COMPROVE SUA NECESSIDADE DE DIETA ESPECIAL ( PARA OS ALUNOS QUE TEM RESTRICOES ALIMETARES OU ALERGIA COMPROVADO PELO MEDICO) .",
        "ANEXO: EM CASO DO ESTUDANTE JA POSSUIR PASSAPORTE ANEXAR PAGINA DA FOTO COM O NUMERO DO PASSAPORTE",
        "ANEXO: HISTORICO ESCOLAR DO ANO DE 2023",
        "ANEXO: HISTORICO/BOLETIM ESCOLAR DO ANO DE 2024",
        "ANEXO: BOLETIM ATUALIZADO DE 2025",
        "ANEXO: TERMO DE PARTICIPACAO/COMPROMISSO GRIFFE",
        "ANEXO: CARTA PARA FAMILIA ANFITRIA EM INGLES",
        "ANEXO: ALBUM DE FOTOS DO ESTUDANTE",
    ],
}

FORM_INICIAL_SECTIONS = {
    "Section 1 - Student Information": [
        "NOME DO ESTUDANTE",
        "SOBRENOME COMPLETO DO ESTUDANTE",
        "NUMERO DO CPF DO ESTUDANTE",
        "NUMERO DO RG DO ESTUDANTE",
        "DATA DE EMISSAO DO RG DO ESTUDANTE",
        "ORGAO EMISSOR + UF DO RG DO ESTUDANTE",
        "DATA DE NASCIMENTO DO ESTUDANTE",
        "CIDADE  DE NASCIMENTO DO ESTUDANTE",
        "ESTADO DE NASCIMENTO DO ESTUDANTE",
        "PAIS DE NASCIMENTO DO ESTUDANTE",
        "SEXO DO ESTUDANTE",
        "RACA/COR DO ESTUDANTE",
        "NUMERO DE TELEFONE DO ESTUDANTE (COM WHATSAPP)",
        "EMAIL DO ESTUDANTE",
        "ESTADO CIVIL DO ESTUDANTE",
    ],
    
    "Section 2 - Passport Information": [
        "O ESTUDANTE POSSUI PASSAPORTE?",
        "SE SIM, O PASSAPORTE DO ESTUDANTE ESTA VALIDO?",
        "SE O ESTUDANTE TEM PASSAPORTE INFORME O NUMERO",
        "SE O ESTUDANTE TEM PASSAPORTE INFORME A DATA DE VALIDADE",
        "O ESTUDANTE POSSUI ALGUM VISTO?",
    ],
    
    "Section 3 - Parent Information": [
        "NOME COMPLETO DA MAE",
        "NUMERO DE TELEFONE DA MAE (COM WHATSAPP)",
        "EMAIL DA MAE",
        "NUMERO DO CPF DA MAE",
        "PROFISSAO DA MAE",
        "SUA MAE SE ENCAIXA EM ALGUMA DESSAS DESCRICOES?",
        "NOME COMPLETO DO PAI",
        "NUMERO DE TELEFONE DO PAI (COM WHATSAPP)",
        "EMAIL DO PAI",
        "NUMERO DO CPF DO PAI",
        "PROFISSAO DO PAI",
        "SEU PAI SE ENCAIXA EM ALGUMA DESSAS DESCRICOES?",
    ],
    
    "Section 4 - Address and Additional Info": [
        "CEP DO ENDERECO DE RESIDENCIA DO ESTUDANTE",
        "ENDERECO COMPLETO DE RESIDENCIA DO ESTUDANTE",
        "TAMANHO DE CAMISA QUE O ESTUDANTE VESTE?",
        "TAMANHO DE JAQUETA QUE O ESTUDANTE VESTE?",
        "SE O ESTUDANTE POSSUI ALGUMA DOENCA CRONICA OU CONDICAO DE SAUDE FISICA OU MENTAL RELEVANTE, ESPECIFIQUE ABAIXO",
        "SE O ESTUDANTE POSSUI ALGUM TIPO DE ALERGIA, ESPECIFIQUE ABAIXO",
        "RELIGIAO DO ESTUDANTE",
    ],
    
    "Section 5 - Documents and Attachments": [
        "ANEXO: FOTO FRENTE E VERSO DO RG E CPF DO ESTUDANTE",
        "ANEXO: FOTO FRENTE E VERSO DO RG E CPF DA MAE DO ESTUDANTE",
        "ANEXO: FOTO FRENTE E VERSO DO RG E CPF DO PAI DO ESTUDANTE",
        "ANEXO: COMPROVANTE DE ENDERECO DO ESTUDANTE",
        "ANEXO: EM CASO DE SEUS PAIS FALECIDOS, ANEXAR A CERTIDAO DE OBITO",
        "ANEXO: CASO O RESPONSAVEL DO ESTUDANTE SEJA OUTRO MEMBRO DA FAMILIA OU UM DOS PAIS E O MESMO TENHA GUARDA OU ALVARA ANEXAR O DOCUMENTO",
        "ANEXO: EM CASO DO ESTUDANTE JA POSSUIR PASSAPORTE ANEXAR PAGINA DA FOTO COM O NUMERO DO PASSAPORTE",
    ],
}

FORM_MEDICO_SECTIONS = {
    "Section 1 - Health Conditions": [
        "VOCE TEM ALGUM PROBLEMA DE SAUDE?",
        "SE SIM, DESCREVA SUA(S) CONDICAO(OES) DE SAUDE:",
        "VOCE POSSUI ALGUM LAUDO MEDICO SOBRE SUA CONDICAO DE SAUDE?",
        "CONDICOES DE SAUDE (ATUAIS OU PASSADAS)",
    ],
    
    "Section 2 - Allergies": [
        "VOCE TEM ALGUM TIPO DE ALERGIA?",
        "CASO TENHA ALGUMA ALERGIA ASSINALADA, FAVOR DAR MAIS INFORMACOES",
        "SE O ESTUDANTE POSSUI ALGUM TIPO DE ALERGIA, ESPECIFIQUE ABAIXO",
    ],
    
    "Section 3 - Physical Activity": [
        "VOCE TEM ALGUMA RESTRICAO A ATIVIDADE FISICA?",
        "SE SIM, ESPECIFIQUE SUAS RESTRICOES PARA ATIVIDADE FISICA:",
    ],
    
    "Section 4 - Sleep and Pain": [
        "VOCE TEM ALGUM DISTURBIO DO SONO?",
        "VOCE SOFRE DE ENXAQUECAS OU DORES DE CABECA FREQUENTES?",
        "(APENAS PARA MULHERES) VOCE SENTE COLICAS MENSTRUAIS INTENSAS?",
    ],
    
    "Section 5 - Health Professionals": [
        "VOCE FAZ OU FEZ ALGUM ACOMPANHAMENTO COM ALGUM PROFISSIONAL DA SAUDE?",
        "SE SIM, PORQUE VOCE PRECISA DESSE ACOMPANHAMENTO?",
    ],
    
    "Section 6 - Vaccination": [
        "VOCE FOI VACINADO CONTRA O COVID?",
        "TIPO DE VACINA COVID-19:",
        "VOCE RECEBEU AS SEGUINTES VACINAS?",
    ],
    
    "Section 7 - Mental Health": [
        "VOCE JA FOI DIAGNOSTICADO OU TRATADO POR ALGUMA CONDICAO DE SAUDE MENTAL?",
        "SE SIM, MARQUE AS CONDICOES QUE SE APLICAM:",
        "CASO TENHA ALGUMA CONDICAO DE SAUDE MENTAL, DESCREVA SEU TRATAMENTO DE SAUDE MENTAL E STATUS ATUAL:",
    ],
    
    "Section 8 - Learning and Neurodivergence": [
        "VOCE TEM UM DIAGNOSTICO DE DIFICULDADE DE APRENDIZAGEM OU CONDICAO NEURODIVERGENTE (EX.: TDAH, DISLEXIA, AUTISMO)?",
        "CASO TENHA ALGUMA DIFICULDADE DE APRENDIZAGEM OU CONDICAO NEURODIVERGENTE, ESPECIFIQUE E DESCREVA QUAISQUER ACOMODACOES OU SUPORTE NECESSARIO:",
    ],
    
    "Section 9 - Medications": [
        "VOCE FAZ USO DE ALGUM MEDICAMENTO DE FORMA CONTINUA (TODOS OS DIAS)?",
        "SE SIM, LISTE O MEDICAMENTO, DOSAGEM E FREQUENCIA:",
        "MEDICAMENTO QUE USA EM CASO DE DOR DE CABECA",
        "MEDICAMENTO QUE USA EM CASO DE FEBRE",
        "MEDICAMENTO QUE USA EM CASO DE NAUSEA/VOMITOS",
        "VOCE PRECISARA TOMAR MEDICAMENTO DURANTE O HORARIO ESCOLAR?",
    ],
    
    "Section 10 - Documents and Attachments": [
        "ANEXO: ANEXE AQUI SEU RELATORIO DE SAUDE (RELATORIO MEDICO QUE COMPROVE SUA CONDICAO DE SAUDE)  OBS: NESSE RELATORIO DEVE CONTER SEU DIAGNOSTICO COM CID, TIPO DE ACOMPANHAMENTO, O QUE EXACERBA SUA CONDICAO DE SAUDE E MEDICAMENTOS USADOS DE FORMA CONTINUA E EM CRISES.",
        "ANEXO: ANEXE AQUI SEU RELATORIO MEDICO QUE COMPROVE SUA ALERGIA.",
        "ANEXO: COMPROVANTE DE VACINACAO COVID-19",
        "ANEXO: HISTORICO DE VACINACAO  (ANEXE AQUI SEU CARTAO DE VACINA, FRENTE E VERSO, DECLARACAO DE VACINA QUE VOCE JA TENHA TOMADO EMITIDO PELO CONECT SUS)",
        "ANEXO: ANEXE AQUI SUA RECEITA DE MEDICAMENTOS",
    ],
}

def get_field_label(field_name: str) -> str:
    """
    Converte nome de campo em label amigável
    
    Args:
        field_name: Nome do campo da planilha
        
    Returns:
        Label formatada para exibição
    """
    # Remove emojis e números
    label = field_name
    label = label.replace('1️⃣', '').replace('2️⃣', '').replace('3️⃣', '')
    label = label.replace('4️⃣', '').replace('5️⃣', '').replace('6️⃣', '')
    label = label.replace('7️⃣', '').replace('8️⃣', '').replace('9️⃣', '')
    label = label.replace('🔟', '').replace('1️⃣1️⃣', '').replace('1️⃣2️⃣', '')
    label = label.replace('1️⃣3️⃣', '').replace('1️⃣4️⃣', '').replace('1️⃣5️⃣', '')
    label = label.replace('1️⃣6️⃣', '').replace('1️⃣7️⃣', '')
    
    # Capitaliza apenas primeira letra
    label = label.strip()
    if label:
        label = label[0].upper() + label[1:].lower()
    
    return label

# Mapeamento unificado de todos os campos organizados por categoria
UNIFIED_SECTIONS = {
    "📋 Informações do Estudante": {
        "fields": [
            ("NOME DO ESTUDANTE", "Inicial"),
            ("SOBRENOME COMPLETO DO ESTUDANTE", "Inicial"),
            ("DATA DE NASCIMENTO DO ESTUDANTE", "Inicial"),
            ("SEXO DO ESTUDANTE", "Inicial"),
            ("PAIS DE NASCIMENTO DO ESTUDANTE", "Inicial"),
            ("CIDADE  DE NASCIMENTO DO ESTUDANTE", "Inicial"),
            ("ESTADO DE NASCIMENTO DO ESTUDANTE", "Inicial"),
            ("EMAIL DO ESTUDANTE", "Inicial"),
            ("NUMERO DE TELEFONE DO ESTUDANTE (COM WHATSAPP)", "Inicial"),
            ("TAMANHO DE CAMISA QUE O ESTUDANTE VESTE?", "Inicial"),
            ("TAMANHO DE JAQUETA QUE O ESTUDANTE VESTE?", "Inicial"),
            ("USA OCULOS?", "Matrícula"),
        ]
    },
    
    "🆔 Documentos do Estudante": {
        "fields": [
            ("NUMERO DO CPF DO ESTUDANTE", "Inicial"),
            ("NUMERO DO RG DO ESTUDANTE", "Inicial"),
            ("DATA DE EMISSAO DO RG DO ESTUDANTE", "Inicial"),
            ("ORGAO EMISSOR + UF DO RG DO ESTUDANTE", "Inicial"),
            ("RACA/COR DO ESTUDANTE", "Inicial"),
            ("ESTADO CIVIL DO ESTUDANTE", "Inicial"),
        ]
    },
    
    "🛂 Passaporte e Viagens": {
        "fields": [
            ("O ESTUDANTE POSSUI PASSAPORTE?", "Inicial"),
            ("SE SIM, O PASSAPORTE DO ESTUDANTE ESTA VALIDO?", "Inicial"),
            ("SE O ESTUDANTE TEM PASSAPORTE INFORME O NUMERO", "Inicial"),
            ("SE O ESTUDANTE TEM PASSAPORTE INFORME A DATA DE VALIDADE", "Inicial"),
            ("O ESTUDANTE POSSUI ALGUM VISTO?", "Inicial"),
            ("VOCE JA VIAJOU PARA FORA DO PAIS?", "Matrícula"),
            ("SE SIM, ONDE VOCE JA VIAJOU?", "Matrícula"),
            ("VOCE TEM DUPLA NACIONALIDADE?", "Matrícula"),
        ]
    },
    
    "👪 Informações da Mãe": {
        "fields": [
            ("NOME COMPLETO DA MAE", "Inicial"),
            ("NUMERO DE TELEFONE DA MAE (COM WHATSAPP)", "Inicial"),
            ("EMAIL DA MAE", "Inicial"),
            ("NUMERO DO CPF DA MAE", "Inicial"),
            ("PROFISSAO DA MAE", "Inicial"),
            ("DATA DE NASCIMENTO DA SUA MAE", "Matrícula"),
            ("SUA MAE SE ENCAIXA EM ALGUMA DESSAS DESCRICOES?", "Inicial"),
            ("ENDERECO DE RESIDENCIA DA SUA MAE", "Matrícula"),
        ]
    },
    
    "👨 Informações do Pai": {
        "fields": [
            ("NOME COMPLETO DO PAI", "Inicial"),
            ("NUMERO DE TELEFONE DO PAI (COM WHATSAPP)", "Inicial"),
            ("EMAIL DO PAI", "Inicial"),
            ("NUMERO DO CPF DO PAI", "Inicial"),
            ("PROFISSAO DO PAI", "Inicial"),
            ("DATA DE NASCIMENTO DO SEU PAI", "Matrícula"),
            ("SEU PAI SE ENCAIXA EM ALGUMA DESSAS DESCRICOES?", "Inicial"),
            ("ENDERECO DE RESIDENCIA DO SEU PAI", "Matrícula"),
        ]
    },
    
    "👨‍👩‍👧‍👦 Família": {
        "fields": [
            ("VOCE TEM IRMAOS?", "Matrícula"),
            ("SEUS IRMAOS MORAM COM VOCE NA MESMA CASA?", "Matrícula"),
            ("SEUS PAIS MORAM JUNTOS?", "Matrícula"),
            ("QUAL O STATUS DOS SEUS PAIS?", "Matrícula"),
            ("SEUS PAIS APOIAM O INTERCAMBIO?", "Matrícula"),
            ("CASO O RESPONSAVEL DO ESTUDANTE SEJA OUTRO MEMBRO DA FAMILIA OU APENAS UM DOS PAIS,  TEM A GUARDA DEFINITIVA OU ALVARA EM DOCUMENTO?", "Inicial"),
        ]
    },
    
    "🏠 Endereço": {
        "fields": [
            ("CEP DO ENDERECO DE RESIDENCIA DO ESTUDANTE", "Inicial"),
            ("ENDERECO COMPLETO DE RESIDENCIA DO ESTUDANTE", "Inicial"),
        ]
    },
    
    "🗣️ Idiomas": {
        "fields": [
            ("EM QUE IDIOMA VOCE SE COMUNICA DENTRO DE CASA?", "Matrícula"),
            ("VOCE FALA ALGUM OUTRO IDIOMA ALEM DO PORTUGUES?", "Matrícula"),
            ("VOCE ESTUDA INGLES HA QUANTO TEMPO?", "Matrícula"),
            ("COMO VOCE AVALIA SEU NIVEL DE INGLES NO GERAL?", "Matrícula"),
        ]
    },
    
    "🎓 Escola e Estudos": {
        "fields": [
            ("VOCE GOSTA DE IR PARA ESCOLA?", "Matrícula"),
            ("SUAS TRES MATERIAS FAVORITAS", "Matrícula"),
            ("MARQUE OS PRINCIPAIS CURSOS QUE DESEJA FAZER NO INTERCAMBIO", "Matrícula"),
            ("MARQUE OS CURSOS ELETIVOS QUE DESEJA FAZER", "Matrícula"),
            ("CONTE QUAIS SAO SEUS PLANOS PARA O FUTURO", "Matrícula"),
            ("QUAL E O SEU PRINCIPAL MOTIVO PARA FAZER O INTERCAMBIO E ESCOLHER ESSES CURSOS?", "Matrícula"),
        ]
    },
    
    "⚽ Esportes e Atividades": {
        "fields": [
            ("VOCE PRATICA OU GOSTA DE ESPORTES?", "Matrícula"),
            ("QUAIS ESPORTES VOCE GOSTA OU PRATICA?", "Matrícula"),
            ("GOSTARIA DE PARTICIPAR DE ALGUM TIME ESCOLAR DURANTE O INTERCAMBIO?", "Matrícula"),
            ("QUAIS ATIVIDADES EXTRA CURRICULARES TE INTERESSAM?", "Matrícula"),
        ]
    },
    
    "🎵 Música e Artes": {
        "fields": [
            ("VOCE GOSTA DE MUSICA E TEATRO?", "Matrícula"),
            ("VOCE TOCA ALGUM INSTRUMENTO MUSICAL?", "Matrícula"),
            ("SE SIM, QUAL INSTRUMENTO MUSICAL VOCE TOCA?", "Matrícula"),
            ("VOCE CANTA OU GOSTA DE CANTAR?", "Matrícula"),
            ("VOCE GOSTARIA DE PARTICIPAR DE ALGUM GRUPO ARTISTICO DURANTE O INTERCAMBIO?", "Matrícula"),
        ]
    },
    
    "🎮 Hobbies e Interesses": {
        "fields": [
            ("QUAIS SAO SEUS HOBBIES E INTERESSES", "Matrícula"),
            ("DESCREVA UM POUCO MAIS SOBRE SEUS HOBBIES E O QUE GOSTA DE FAZER NO TEMPO LIVRE", "Matrícula"),
            ("O QUE VOCE GOSTA DE FAZER QUANDO SAI COM SEUS AMIGOS?", "Matrícula"),
        ]
    },
    
    "🍽️ Alimentação": {
        "fields": [
            ("PRECISA DE DIETA ESPECIAL? (ZERO LACTOSE, SEM OVOS, SEM GLUTEN, VEGANA, VEGETARIANA)", "Matrícula"),
            ("ALIMENTOS QUE VOCE GOSTA DE COMER", "Matrícula"),
            ("CASO TENHA ALGUM, CITE ALIMENTOS QUE VOCE NAO GOSTA", "Matrícula"),
            ("VOCE TEM ALERGIA ALIMENTAR?", "Matrícula"),
        ]
    },
    
    "🏡 Homestay e Preferências": {
        "fields": [
            ("VOCE PREFERE MORAR EM:", "Matrícula"),
            ("VOCE PREFERE UMA FAMILIA COM:", "Matrícula"),
            ("VOCE SE SENTE CONFORTAVEL EM MORAR COM OUTRO ESTUDANTE INTERNACIONAL?", "Matrícula"),
            ("VOCE GOSTA DE ANIMAIS DE ESTIMACAO?", "Matrícula"),
            ("VOCE FUMA?", "Matrícula"),
            ("VOCE SE SENTE BEM EM MORAR COM UMA FAMILIA QUE FUMA?", "Matrícula"),
            ("QUAL O ESTILO DE FAMILIA QUE PREFERE", "Matrícula"),
        ]
    },
    
    "😊 Personalidade e Rotina": {
        "fields": [
            ("DESCREVA SUA PERSONALIDADE", "Matrícula"),
            ("VOCE ARRUMA SEU QUARTO E SUA CAMA?", "Matrícula"),
            ("QUE HORAS COSTUMA FAZER A LICAO DE CASA?", "Matrícula"),
            ("QUANTO TEMPO POR DIA COSTUMA FICAR EM REDES SOCIAIS E NAVEGANDO NA INTERNET?", "Matrícula"),
            ("QUE HORAS VOCE COSTUMA DORMIR DURANTE A SEMANA?", "Matrícula"),
            ("DESCREVA SUA ROTINA DURANTE A SEMANA E NO FIM DE SEMANA", "Matrícula"),
            ("VOCE REALIZA ALGUMA TAREFA DOMESTICA? SE SIM, DESCREVA", "Matrícula"),
        ]
    },
    
    "⛪ Religião": {
        "fields": [
            ("RELIGIAO DO ESTUDANTE", "Inicial"),
            ("COM QUE FREQUENCIA VOCE FREQUENTA SERVICOS RELIGIOSOS?", "Matrícula"),
            ("VOCE GOSTARIA DE FREQUENTAR SERVICOS RELIGIOSOS DURANTE O INTERCAMBIO?", "Matrícula"),
        ]
    },
    
    "🏥 Saúde Geral": {
        "fields": [
            ("VOCE TEM ALGUM PROBLEMA DE SAUDE?", "Médico"),
            ("SE SIM, DESCREVA SUA(S) CONDICAO(OES) DE SAUDE:", "Médico"),
            ("VOCE POSSUI ALGUM LAUDO MEDICO SOBRE SUA CONDICAO DE SAUDE?", "Médico"),
            ("CONDICOES DE SAUDE (ATUAIS OU PASSADAS)", "Médico"),
            ("SE O ESTUDANTE POSSUI ALGUMA DOENCA CRONICA OU CONDICAO DE SAUDE FISICA OU MENTAL RELEVANTE, ESPECIFIQUE ABAIXO", "Inicial"),
        ]
    },
    
    "🤧 Alergias": {
        "fields": [
            ("VOCE TEM ALGUM TIPO DE ALERGIA?", "Médico"),
            ("CASO TENHA ALGUMA ALERGIA ASSINALADA, FAVOR DAR MAIS INFORMACOES", "Médico"),
            ("SE O ESTUDANTE POSSUI ALGUM TIPO DE ALERGIA, ESPECIFIQUE ABAIXO", "Inicial"),
        ]
    },
    
    "🏃 Atividade Física e Saúde": {
        "fields": [
            ("VOCE TEM ALGUMA RESTRICAO A ATIVIDADE FISICA?", "Médico"),
            ("SE SIM, ESPECIFIQUE SUAS RESTRICOES PARA ATIVIDADE FISICA:", "Médico"),
            ("VOCE TEM ALGUM DISTURBIO DO SONO?", "Médico"),
            ("VOCE SOFRE DE ENXAQUECAS OU DORES DE CABECA FREQUENTES?", "Médico"),
        ]
    },
    
    "💊 Medicamentos": {
        "fields": [
            ("VOCE FAZ USO DE ALGUM MEDICAMENTO DE FORMA CONTINUA (TODOS OS DIAS)?", "Médico"),
            ("SE SIM, LISTE O MEDICAMENTO, DOSAGEM E FREQUENCIA:", "Médico"),
            ("VOCE PRECISARA TOMAR MEDICAMENTO DURANTE O HORARIO ESCOLAR?", "Médico"),
        ]
    },
    
    "💉 Vacinação": {
        "fields": [
            ("VOCE FOI VACINADO CONTRA O COVID?", "Médico"),
            ("TIPO DE VACINA COVID-19:", "Médico"),
            ("VOCE RECEBEU AS SEGUINTES VACINAS?", "Médico"),
        ]
    },
    
    "🧠 Saúde Mental e Aprendizagem": {
        "fields": [
            ("VOCE JA FOI DIAGNOSTICADO OU TRATADO POR ALGUMA CONDICAO DE SAUDE MENTAL?", "Médico"),
            ("SE SIM, MARQUE AS CONDICOES QUE SE APLICAM:", "Médico"),
            ("VOCE TEM UM DIAGNOSTICO DE DIFICULDADE DE APRENDIZAGEM OU CONDICAO NEURODIVERGENTE (EX.: TDAH, DISLEXIA, AUTISMO)?", "Médico"),
        ]
    },
    
    "📎 Documentos - Estudante": {
        "fields": [
            ("ANEXO: FOTO DO ROSTO DO ESTUDANTE (ESTILO 3X4)", "Matrícula"),
            ("ANEXO: FOTO FRENTE E VERSO DO RG E CPF DO ESTUDANTE", "Inicial"),
            ("ANEXO: EM CASO DO ESTUDANTE JA POSSUIR PASSAPORTE ANEXAR PAGINA DA FOTO COM O NUMERO DO PASSAPORTE", "Inicial"),
        ]
    },
    
    "📎 Documentos - Pais": {
        "fields": [
            ("ANEXO: COMPROVANTE DE RESIDENCIA DA SUA MAE", "Matrícula"),
            ("ANEXO: COMPROVANTE DE RESIDENCIA DO SEU PAI", "Matrícula"),
            ("ANEXO: FOTO FRENTE E VERSO DO RG E CPF DA MAE DO ESTUDANTE", "Inicial"),
            ("ANEXO: FOTO FRENTE E VERSO DO RG E CPF DO PAI DO ESTUDANTE", "Inicial"),
            ("ANEXO: COMPROVANTE DE ENDERECO DO ESTUDANTE", "Inicial"),
        ]
    },
    
    "📎 Documentos - Escolares": {
        "fields": [
            ("ANEXO: HISTORICO ESCOLAR DO ANO DE 2023", "Matrícula"),
            ("ANEXO: HISTORICO/BOLETIM ESCOLAR DO ANO DE 2024", "Matrícula"),
            ("ANEXO: BOLETIM ATUALIZADO DE 2025", "Matrícula"),
        ]
    },
    
    "📎 Documentos - Médicos": {
        "fields": [
            ("ANEXO: ANEXE AQUI SEU RELATORIO DE SAUDE (RELATORIO MEDICO QUE COMPROVE SUA CONDICAO DE SAUDE)  OBS: NESSE RELATORIO DEVE CONTER SEU DIAGNOSTICO COM CID, TIPO DE ACOMPANHAMENTO, O QUE EXACERBA SUA CONDICAO DE SAUDE E MEDICAMENTOS USADOS DE FORMA CONTINUA E EM CRISES.", "Médico"),
            ("ANEXO: ANEXE AQUI SEU RELATORIO MEDICO QUE COMPROVE SUA ALERGIA.", "Médico"),
            ("ANEXO: COMPROVANTE DE VACINACAO COVID-19", "Médico"),
            ("ANEXO: HISTORICO DE VACINACAO  (ANEXE AQUI SEU CARTAO DE VACINA, FRENTE E VERSO, DECLARACAO DE VACINA QUE VOCE JA TENHA TOMADO EMITIDO PELO CONECT SUS)", "Médico"),
            ("ANEXO: ANEXE AQUI SUA RECEITA DE MEDICAMENTOS", "Médico"),
        ]
    },
    
    "📎 Documentos - Outros": {
        "fields": [
            ("ANEXO: TERMO DE PARTICIPACAO/COMPROMISSO GRIFFE", "Matrícula"),
            ("ANEXO: CARTA PARA FAMILIA ANFITRIA EM INGLES", "Matrícula"),
            ("ANEXO: ALBUM DE FOTOS DO ESTUDANTE", "Matrícula"),
        ]
    },
}

def get_field_label(field_name: str) -> str:
    """
    Converte nome de campo em label amigável
    
    Args:
        field_name: Nome do campo da planilha
        
    Returns:
        Label formatada para exibição
    """
    # Remove emojis e números
    label = field_name
    label = label.replace('1️⃣', '').replace('2️⃣', '').replace('3️⃣', '')
    label = label.replace('4️⃣', '').replace('5️⃣', '').replace('6️⃣', '')
    label = label.replace('7️⃣', '').replace('8️⃣', '').replace('9️⃣', '')
    label = label.replace('🔟', '').replace('1️⃣1️⃣', '').replace('1️⃣2️⃣', '')
    label = label.replace('1️⃣3️⃣', '').replace('1️⃣4️⃣', '').replace('1️⃣5️⃣', '')
    label = label.replace('1️⃣6️⃣', '').replace('1️⃣7️⃣', '')
    
    # Capitaliza apenas primeira letra
    label = label.strip()
    if label:
        label = label[0].upper() + label[1:].lower()
    
    return label