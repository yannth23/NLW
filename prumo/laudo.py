"""Esquema do laudo — o formato de saída que o modelo é obrigado a preencher.

Existe por dois motivos. O primeiro é operacional: com `output_config.format`
de tipo `json_schema` o modelo não devolve prosa livre, e os campos entram no
verificador de citação sem parser. O segundo é de produto: o esquema tem um
campo obrigatório `nao_verificado`, então dizer "não consegui confirmar" é uma
resposta válida e barata. Quando a única saída possível é um texto bonito, é
o texto bonito que o modelo entrega.
"""

from __future__ import annotations

CITACAO = {
    "type": "object",
    "additionalProperties": False,
    "required": ["norma", "dispositivo", "pertinencia"],
    "properties": {
        "norma": {
            "type": "string",
            "description": "Norma citada, na forma 'Lei nº 9.784/1999'. "
                           "Deixe vazio se não tiver certeza do número.",
        },
        "dispositivo": {
            "type": "string",
            "description": "Artigo, parágrafo e inciso. Ex.: 'art. 26, §3º'.",
        },
        "pertinencia": {
            "type": "string",
            "description": "Em uma frase, o que esse dispositivo resolve neste auto.",
        },
        "redacao_na_data_do_fato": {
            "type": "string",
            "description": "A redação vigente na data do fato gerador, quando "
                           "diferente da atual. Vazio se não houve alteração.",
        },
    },
}

LAUDO = {
    "type": "object",
    "additionalProperties": False,
    "required": ["resumo", "achados", "citacoes", "nao_verificado", "proximo_passo"],
    "properties": {
        "resumo": {
            "type": "string",
            "description": "Três a cinco linhas. O que o auto cobra, de quem e por quê.",
        },
        "achados": {
            "type": "array",
            "description": "Os pontos que mudam o resultado, do mais forte ao mais fraco.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["ponto", "fundamento", "forca"],
                "properties": {
                    "ponto": {"type": "string"},
                    "fundamento": {"type": "string"},
                    "forca": {"type": "string", "enum": ["alta", "média", "baixa"]},
                    "prova_necessaria": {
                        "type": "string",
                        "description": "O documento que precisa ser juntado para sustentar.",
                    },
                },
            },
        },
        "valores": {
            "type": "object",
            "additionalProperties": False,
            "description": "Só preencha o que estiver no auto. Não estime.",
            "required": [],
            "properties": {
                "principal": {"type": "string"},
                "multa": {"type": "string"},
                "juros": {"type": "string"},
                "total": {"type": "string"},
                "divergencia_apurada": {
                    "type": "string",
                    "description": "Diferença entre o lançado e o que a norma comporta, "
                                   "com a memória de cálculo.",
                },
            },
        },
        "prazo": {
            "type": "object",
            "additionalProperties": False,
            "required": [],
            "properties": {
                "rito": {"type": "string", "description": "Órgão e norma que rege o rito."},
                "marco": {"type": "string", "description": "O evento que inicia a contagem."},
                "dias": {"type": "string"},
                "data_limite": {"type": "string"},
                "observacao": {
                    "type": "string",
                    "description": "Deixe explícito quando o prazo depender de norma local "
                                   "que não foi confirmada.",
                },
            },
        },
        "citacoes": {"type": "array", "items": CITACAO},
        "nao_verificado": {
            "type": "array",
            "description": "Tudo que não deu para confirmar na fonte. Este campo "
                           "cheio é resposta melhor do que um número inventado.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["item", "motivo"],
                "properties": {
                    "item": {"type": "string"},
                    "motivo": {"type": "string"},
                    "termo_pesquisado": {"type": "string"},
                },
            },
        },
        "proximo_passo": {
            "type": "string",
            "description": "A ação seguinte de quem recebeu o auto, em uma frase.",
        },
    },
}
