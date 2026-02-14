```python
import os
import re
from openai import OpenAI
from typing import Optional

# Configuração do cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SYSTEM PROMPT atualizado conforme requisitos específicos de fórmulas magistrais
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
- Exemplo: "Loção de Ácido Glicólico 10%: auxilia na renovação celular para pele com cravos"

4) NOTA DE SEGURANÇA
"Estas são opções de venda livre, mas a avaliação por farmacêutico é obrigatória antes da manipulação conforme Art. 32 da RDC 67/2007."

5) FONTE REGULATÓRIA
"Baseado no Formulário Nacional da Farmacopeia Brasileira e RDC 357/2020 da Anvisa."

REGRAS DE LINGUAGEM:
- Neutro, técnico e objetivo
- Sem perguntas ou convites para continuidade
- Resposta única e fechada
- Evite termos como "recomendo" ou "você deve"
- Contagem rigorosa de palavras (máx 220)
"""

def validar_sinais_alerta(relato: str) -> Optional[str]:
    """
    Verifica sinais de alerta que impedem sugestão de fórmulas e exigem orientação médica imediata.
    Retorna mensagem de alerta ou None se não houver sinais críticos.
    """
    sinais_alerta = {
        r'\b(febr.*[34][890123456789]\s*°C|febr.*alta|febr.*persistente)\b': 'Febre alta (>38°C) ou persistente',
        r'\b(dor\s+no\s+peito|dor\s+torácica|pressão\s+no\s+peito)\b': 'Dor torácica',
        r'\b(sangr.*vaginal|intenso|descontrolado|hemorragia)\b': 'Sangramento intenso',
        r'\b(gesta|grávi|enceinte|gravidez)\b': 'Gestação',
        r'\b(bebê|recém-nascido|lactente|criança\s+menor\s+que\s+2\s+anos|<\s*2\s+anos)\b': 'Criança menor de 2 anos',
        r'\b(falta\s+de\s+ar|dispneia|engasgo|dificuldade\s+respiratória)\b': 'Dificuldade respiratória',
        r'\b(tontura\s+intensa|desmaio|perda\s+de\s+consciência)\b': 'Tontura intensa ou desmaio'
    }
    
    relato_lower = relato.lower()
    for padrao, descricao in sinais_alerta.items():
        if re.search(padrao, relato_lower):
            return (f"⚠️ SINAL DE ALERTA IDENTIFICADO: {descricao}\n\n"
                   "Procure atendimento médico imediato ou farmacêutico presencial. "
                   "Não é adequado sugerir fórmulas magistrais sem avaliação profissional neste caso.")
    return None

def contar_palavras(texto: str) -> int:
    """Conta palavras mantendo apenas caracteres alfanuméricos e hífens internos."""
    palavras = re.findall(r'\b[a-zA-Z0-9À-ÿ]+(?:-[a-zA-Z0-9À-ÿ]+)*\b', texto)
    return len(palavras)

def consultar_ia(relato: str) -> str:
    """
    Analisa relato do usuário e retorna sugestões de fórmulas magistrais dentro dos limites regulatórios.
    
    Args:
        relato: Descrição dos sintomas pelo usuário
        
    Returns:
        String formatada com análise e sugestões (máx 220 palavras) ou mensagem de segurança
    """
    try:
        # Verificação prévia de sinais de alerta
        alerta = validar_sinais_alerta(relato)
        if alerta:
            return alerta
        
        # Chamada à API OpenAI com controle rigoroso de tokens
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Relato do usuário: {relato}"}
            ],
            max_tokens=400,  # Limite conservador para garantir 220 palavras na resposta
            temperature=0.2,  # Baixa temperatura para respostas técnicas e consistentes
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.2
        )
        
        resposta_bruta = response.choices[0].message.content.strip()
        
        # Pós-processamento: validação de comprimento e segurança
        palavras = contar_palavras(resposta_bruta)
        if palavras > 220:
            # Recortar mantendo estrutura essencial
            partes = re.split(r'\n\s*\n', resposta_bruta)
            resposta_ajustada = ""
            for parte in partes:
                if contar_palavras(resposta_ajustada + " " + parte) <= 210:
                    resposta_ajustada += "\n\n" + parte if resposta_ajustada else parte
                else:
                    break
            resposta_final = resposta_ajustada + "\n\n[Resposta truncada para limite regulatório de 220 palavras]"
        else:
            resposta_final = resposta_bruta
        
        # Garantir presença obrigatória da nota de segurança
        if "avaliação por farmacêutico" not in resposta_final.lower():
            resposta_final += "\n\n⚠️ NOTA DE SEGURANÇA: Estas são opções de venda livre, mas a avaliação por farmacêutico é obrigatória antes da manipulação conforme Art. 32 da RDC 67/2007."
        
        return resposta_final

    except Exception as e:
        # Log seguro sem expor detalhes sensíveis
        error_msg = f"Erro no processamento: {type(e).__name__}"
        print(f"[ERRO IA] {error_msg}")  # Para logs internos
        
        return ("Não foi possível gerar sugestões técnicas no momento. "
                "Consulte um farmacêutico para orientação adequada sobre fórmulas magistrais. "
                "Este serviço não substitui avaliação profissional presencial.")

# Exemplo de uso (opcional para testes)
if __name__ == "__main__":
    relato_teste = "Tenho pele oleosa com cravos no rosto e espinhas leves há 2 semanas. Não uso nenhum medicamento."
    resultado = consultar_ia(relato_teste)
    print("="*60)
    print("RELATO DO USUÁRIO:")
    print(relato_teste)
    print("\nRESPOSTA DO SISTEMA:")
    print(resultado)
    print(f"\nContagem de palavras: {contar_palavras(resultado)}")
    print("="*60)
```