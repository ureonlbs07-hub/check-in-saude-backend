import os
import re
from openai import OpenAI
from typing import Optional

# Configuração do cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Você é um assistente especializado em análise de relatos para sugestão de fórmulas magistrais de venda livre em farmácias brasileiras.

REGRAS OBRIGATÓRIAS:
- NUNCA recomende medicamentos com tarja vermelha ou preta (sujeitos a prescrição).
- Limite-se a fórmulas isentas de prescrição conforme RDC 357/2020 da Anvisa e Formulário Nacional.
- NÃO faça diagnósticos médicos nem substitua orientação farmacêutica.
- Todas as sugestões devem ser fórmulas magistrais comuns em farmácias brasileiras com venda livre autorizada.
- Verifique SINAIS DE ALERTA: febre >39°C, dor torácica, sangramento, gestação, crianças <2 anos → direcionar a atendimento profissional.

ESTRUTURA DA RESPOSTA (220 palavras máx):

1) TÍTULO DO SINTOMA
Breve descrição do quadro relatado.

2) ANÁLISE DO RELATO
Identificação objetiva dos sintomas mencionados sem interpretação diagnóstica.

3) FÓRMULAS SUGERIDAS (máx 3)
- Nome da fórmula magistral + concentração
- Indicação conforme bulário brasileiro

4) NOTA DE SEGURANÇA
Estas são opções de venda livre, mas a avaliação por farmacêutico é obrigatória antes da manipulação conforme Art. 32 da RDC 67/2007.

5) FONTE REGULATÓRIA
Baseado no Formulário Nacional da Farmacopeia Brasileira e RDC 357/2020 da Anvisa.

REGRAS DE LINGUAGEM:
- Neutro, técnico e objetivo
- Sem perguntas ou convites para continuidade
- Resposta única e fechada
- Evite termos como "recomendo" ou "você deve"
- Contagem rigorosa de palavras (máx 220)
"""


def validar_sinais_alerta(relato: str) -> Optional[str]:
    sinais_alerta = {
        r'\bfebr.*(39|40)\b': 'Febre alta',
        r'\bdor\s+no\s+peito|dor\s+torácica\b': 'Dor torácica',
        r'\bhemorragia|sangramento\s+intenso\b': 'Sangramento intenso',
        r'\bgravidez|gestante|grávida\b': 'Gestação',
        r'\bcriança\s+menor\s+que\s+2\s+anos|<\s*2\s+anos\b': 'Criança menor de 2 anos',
        r'\bfalta\s+de\s+ar|dispneia\b': 'Dificuldade respiratória',
        r'\bdesmaio|perda\s+de\s+consciência\b': 'Desmaio'
    }

    relato_lower = relato.lower()

    for padrao, descricao in sinais_alerta.items():
        if re.search(padrao, relato_lower):
            return (
                f"SINAL DE ALERTA IDENTIFICADO: {descricao}.\n\n"
                "Procure atendimento médico imediato ou farmacêutico presencial. "
                "Não é adequado sugerir fórmulas magistrais sem avaliação profissional neste caso."
            )

    return None


def contar_palavras(texto: str) -> int:
    palavras = re.findall(r'\b\w+\b', texto)
    return len(palavras)


def consultar_ia(relato: str) -> str:
    try:
        alerta = validar_sinais_alerta(relato)
        if alerta:
            return alerta

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": relato}
            ],
            max_tokens=400,
            temperature=0.2
        )

        resposta = response.choices[0].message.content.strip()

        if contar_palavras(resposta) > 220:
            palavras = resposta.split()
            resposta = " ".join(palavras[:220])

        if "avaliação por farmacêutico" not in resposta.lower():
            resposta += (
                "\n\nEstas são opções de venda livre, mas a avaliação por farmacêutico "
                "é obrigatória antes da manipulação conforme Art. 32 da RDC 67/2007."
            )

        return resposta

    except Exception as e:
        print(f"[ERRO IA] {type(e).__name__}: {str(e)}")

        return (
            "Não foi possível gerar sugestões técnicas no momento. "
            "Consulte um farmacêutico para orientação adequada. "
            "Este serviço não substitui avaliação profissional presencial."
        )