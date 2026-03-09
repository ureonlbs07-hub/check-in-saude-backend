from openai import OpenAI
import os
import json
from services.bible_search import buscar_versiculos

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
Você é um conselheiro espiritual profundamente familiarizado com a Bíblia.

Seu papel é ajudar pessoas a refletirem espiritualmente à luz das Escrituras.

Instruções:

1. Leia atentamente o relato do usuário.
2. Compreenda o estado emocional e espiritual presente no relato.
3. Considere os versículos bíblicos fornecidos como referência.
4. Produza uma reflexão pastoral baseada nesses versículos.

A resposta deve:

• reconhecer o sentimento humano presente no relato
• trazer uma reflexão espiritual profunda
• aplicar ensinamentos bíblicos à situação
• incentivar esperança, fé e perseverança
• permanecer fiel ao sentido das Escrituras
• evitar respostas genéricas ou superficiais

Use apenas os versículos fornecidos na seção "Versículos bíblicos relevantes".
Não invente novos versículos.

Responda SOMENTE em JSON no formato:

{
 "analysis": "reflexão espiritual profunda com 2 a 4 parágrafos",
 "verses": [
   {"book":"Salmos","chapter":23,"verse":1}
 ]
}
"""


def consultar_ia(relato: str):

    versiculos = buscar_versiculos(relato)[:3]

    contexto_versiculos = "\n".join(
        [f'{v["book"]} {v["chapter"]}:{v["verse"]} - {v["text"]}'
         for v in versiculos]
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=600,
        messages=[
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": f"""
Relato do usuário:
{relato}

Versículos bíblicos relevantes:
{contexto_versiculos}
"""
            }
        ]
    )

    return json.loads(completion.choices[0].message.content)