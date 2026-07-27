"""Prumo — segunda opinião sobre o auto de infração fiscal.

Dois módulos independentes:

  citacoes.py   extrai e resolve citações legais contra a fonte oficial
  prompts.py    a biblioteca de prompts e o esquema do laudo

O verificador roda sem chave de API e sem modelo. É de propósito: ele existe
para conferir a saída de qualquer IA, inclusive a nossa.
"""

__all__ = ["citacoes", "prompts", "laudo"]
