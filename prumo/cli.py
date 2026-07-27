"""Linha de comando do Prumo.

    python3 -m prumo prompts
    python3 -m prumo verificar prumo/exemplo/saida-com-erro.txt
    python3 -m prumo avaliar --prompt 02 prumo/exemplo/auto-exemplo.txt --dry-run
    python3 -m prumo avaliar --prompt 02 prumo/exemplo/auto-exemplo.txt

O `avaliar` sem `--dry-run` chama a API e exige ANTHROPIC_API_KEY. O
`verificar` não chama modelo nenhum: ele confere citação, e serve para auditar
a saída de qualquer ferramenta.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

from . import citacoes, prompts
from .laudo import LAUDO

MAX_TOKENS = 8000


def _ler(caminho: str) -> str:
    p = pathlib.Path(caminho)
    if not p.exists():
        sys.exit(f"arquivo não encontrado: {caminho}")
    return p.read_text(encoding="utf-8", errors="replace")


def cmd_prompts(_args) -> int:
    print(prompts.listar())
    return 0


def cmd_verificar(args) -> int:
    texto = _ler(args.arquivo)
    achados = citacoes.extrair(texto)
    if args.somente_extrair:
        for c in achados:
            print(f"{c.rotulo:<46} <- {c.bruto!r}")
        return 0
    if args.demo:
        from unittest import mock

        from .fonte_simulada import abrir
        print("### fonte simulada — recorte local das normas, não vale como "
              "consulta\n")
        with mock.patch.object(citacoes, "_abrir", side_effect=abrir):
            resultados = citacoes.verificar(achados)
    else:
        resultados = citacoes.verificar(achados)
    print(citacoes.relatorio(resultados))
    reprovadas = [r for r in resultados
                  if r.status in ("ARTIGO_AUSENTE", "NAO_ENCONTRADA")]
    return 1 if reprovadas else 0


def cmd_avaliar(args) -> int:
    prompt = prompts.BIBLIOTECA.get(args.prompt)
    if prompt is None:
        sys.exit(f"prompt {args.prompt} não existe. "
                 f"Disponíveis: {', '.join(prompts.BIBLIOTECA)}")

    auto = _ler(args.arquivo)
    mensagens = prompt.montar(auto, args.contexto or "")
    requisicao = {
        "model": prompts.MODELO,
        "max_tokens": MAX_TOKENS,
        "system": prompts.sistema(),
        "messages": mensagens,
        "output_config": {"format": {"type": "json_schema", "schema": LAUDO}},
    }

    if args.dry_run:
        print(f"# {prompt.id} — {prompt.nome} ({prompt.familia})")
        print(f"# modelo: {requisicao['model']}   max_tokens: {MAX_TOKENS}")
        print(f"# saída: json_schema, {len(LAUDO['properties'])} campos, "
              f"{len(LAUDO['required'])} obrigatórios")
        print()
        print("=== system (cacheado) " + "=" * 55)
        print(prompts.PREAMBULO)
        print()
        print("=== user " + "=" * 68)
        print(mensagens[0]["content"])
        return 0

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("defina ANTHROPIC_API_KEY, ou rode com --dry-run para ver a "
                 "requisição sem chamar a API")

    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic")

    cliente = anthropic.Anthropic()
    try:
        resp = cliente.messages.create(**requisicao)
    except anthropic.APIError as e:
        sys.exit(f"API: {e}")

    # A recusa é um desfecho previsto, não um erro. O prompt 08 recusa quando o
    # pedido é ajudar a atender a solicitação indevida em vez de registrá-la.
    if resp.stop_reason == "refusal":
        print("O modelo recusou o pedido.", file=sys.stderr)
        print(f"request_id: {resp._request_id}", file=sys.stderr)
        return 2
    if resp.stop_reason == "max_tokens":
        print("Resposta truncada em max_tokens; o JSON abaixo está incompleto.",
              file=sys.stderr)

    bruto = "".join(b.text for b in resp.content if b.type == "text")
    try:
        laudo = json.loads(bruto)
    except json.JSONDecodeError:
        print(bruto)
        return 3

    print(json.dumps(laudo, ensure_ascii=False, indent=2))

    # A saída do modelo passa pelo verificador antes de valer como laudo.
    print("\n" + "=" * 92)
    print("VERIFICAÇÃO DE CITAÇÕES\n")
    alvo = json.dumps(laudo.get("citacoes", []), ensure_ascii=False)
    resultados = citacoes.verificar(citacoes.extrair(alvo))
    print(citacoes.relatorio(resultados))
    return 1 if any(r.status in ("ARTIGO_AUSENTE", "NAO_ENCONTRADA")
                    for r in resultados) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="prumo", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("prompts", help="lista a biblioteca").set_defaults(fn=cmd_prompts)

    v = sub.add_parser("verificar", help="confere as citações de um texto")
    v.add_argument("arquivo")
    v.add_argument("--somente-extrair", action="store_true",
                   help="só mostra o que foi reconhecido, sem abrir a fonte")
    v.add_argument("--demo", action="store_true",
                   help="usa o recorte local em vez do Planalto, para ver o "
                        "relatório sem depender da rede")
    v.set_defaults(fn=cmd_verificar)

    a = sub.add_parser("avaliar", help="roda um prompt sobre um auto de infração")
    a.add_argument("arquivo")
    a.add_argument("--prompt", default="02")
    a.add_argument("--contexto", default="", help="informação adicional do contribuinte")
    a.add_argument("--dry-run", action="store_true",
                   help="imprime a requisição montada sem chamar a API")
    a.set_defaults(fn=cmd_avaliar)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
