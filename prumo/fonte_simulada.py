"""Um recorte da fonte oficial, para rodar o verificador sem rede.

Serve a dois usos: as fixtures dos testes e o `--demo` da linha de comando.
São trechos curtos das normas, no formato em que o Planalto publica — HTML
antigo, latin-1, entidades em vez de acentos, artigo por parágrafo. O parser
apanha exatamente disso, então a fixture precisa apanhar igual.

Não é cache e não substitui a consulta. Nada que sai daqui vale como citação
verificada: é o caminho do código que está sendo exercitado, não a norma.
"""

from __future__ import annotations

P = "https://www.planalto.gov.br/ccivil_03"


def _pagina(titulo: str, artigos: list[tuple[str, str]]) -> bytes:
    corpo = "".join(f"<p>Art. {n}. {t}</p>\n" for n, t in artigos)
    return f"<html><body>\n<p>{titulo}</p>\n{corpo}</body></html>".encode("latin-1")


L9784 = _pagina(
    "LEI N&ordm; 9.784, DE 29 DE JANEIRO DE 1999.",
    [("26", "O &oacute;rg&atilde;o competente perante o qual tramita o processo "
            "administrativo determinar&aacute; a intima&ccedil;&atilde;o do "
            "interessado. &sect; 3&ordm; A intima&ccedil;&atilde;o pode ser efetuada "
            "por ci&ecirc;ncia no processo, por via postal com aviso de recebimento."),
     ("50", "Os atos administrativos dever&atilde;o ser motivados, com "
            "indica&ccedil;&atilde;o dos fatos e dos fundamentos jur&iacute;dicos."),
     ("68", "Esta Lei entra em vigor na data de sua publica&ccedil;&atilde;o.")])

L13988 = _pagina(
    "LEI N&ordm; 13.988, DE 14 DE ABRIL DE 2020.",
    [("10", "A transa&ccedil;&atilde;o poder&aacute; contemplar os seguintes "
            "benef&iacute;cios. (Reda&ccedil;&atilde;o dada pela Lei n&ordm; 14.375, "
            "de 2022)"),
     ("11", "A proposta de transa&ccedil;&atilde;o dever&aacute; expor os meios "
            "para a extin&ccedil;&atilde;o dos cr&eacute;ditos.")])

L5172 = _pagina(
    "LEI N&ordm; 5.172, DE 25 DE OUTUBRO DE 1966. (C&oacute;digo Tribut&aacute;rio Nacional)",
    [("142", "Compete privativamente &agrave; autoridade administrativa constituir "
             "o cr&eacute;dito tribut&aacute;rio pelo lan&ccedil;amento."),
     ("150", "O lan&ccedil;amento por homologa&ccedil;&atilde;o ocorre quanto aos "
             "tributos cuja legisla&ccedil;&atilde;o atribua ao sujeito passivo o "
             "dever de antecipar o pagamento. &sect; 4&ordm; Se a lei n&atilde;o "
             "fixar prazo &agrave; homologa&ccedil;&atilde;o, ser&aacute; ele de "
             "cinco anos, a contar da ocorr&ecirc;ncia do fato gerador."),
     ("173", "O direito de a Fazenda P&uacute;blica constituir o cr&eacute;dito "
             "tribut&aacute;rio extingue-se ap&oacute;s cinco anos, contados do "
             "primeiro dia do exerc&iacute;cio seguinte &agrave;quele em que o "
             "lan&ccedil;amento poderia ter sido efetuado.")])

D70235 = _pagina(
    "DECRETO N&ordm; 70.235, DE 6 DE MAR&Ccedil;O DE 1972.",
    [("15", "A impugna&ccedil;&atilde;o, formalizada por escrito e instru&iacute;da "
            "com os documentos em que se fundamentar, ser&aacute; apresentada ao "
            "&oacute;rg&atilde;o preparador no prazo de trinta dias."),
     ("23", "Far-se-&aacute; a intima&ccedil;&atilde;o pessoalmente, por via postal "
            "ou por meio eletr&ocirc;nico. (Reda&ccedil;&atilde;o dada pela Lei "
            "n&ordm; 11.196, de 2005)"),
     ("33", "Da decis&atilde;o caber&aacute; recurso volunt&aacute;rio, total ou "
            "parcial, no prazo de trinta dias.")])

LCP87 = _pagina(
    "LEI COMPLEMENTAR N&ordm; 87, DE 13 DE SETEMBRO DE 1996.",
    [("20", "Para a compensa&ccedil;&atilde;o a que se refere o artigo anterior, "
            "&eacute; assegurado ao sujeito passivo o direito de creditar-se do "
            "imposto anteriormente cobrado."),
     ("33", "Na aplica&ccedil;&atilde;o do art. 20 observar-se-&aacute; o seguinte: "
            "I &ndash; somente dar&atilde;o direito de cr&eacute;dito as mercadorias "
            "destinadas ao uso ou consumo do estabelecimento nele entradas a partir "
            "de 1&ordm; de janeiro de 2033. (Reda&ccedil;&atilde;o dada pela Lei "
            "Complementar n&ordm; 171, de 2019)")])

CF88 = _pagina(
    "CONSTITUI&Ccedil;&Atilde;O DA REP&Uacute;BLICA FEDERATIVA DO BRASIL DE 1988",
    [("5", "Todos s&atilde;o iguais perante a lei. LV &ndash; aos litigantes, em "
           "processo judicial ou administrativo, s&atilde;o assegurados o "
           "contradit&oacute;rio e a ampla defesa, com os meios e recursos a ela "
           "inerentes."),
     ("155", "Compete aos Estados e ao Distrito Federal instituir impostos sobre "
             "opera&ccedil;&otilde;es relativas &agrave; circula&ccedil;&atilde;o de "
             "mercadorias.")])

FONTE: dict[str, bytes] = {
    f"{P}/leis/L9784.htm": L9784,
    f"{P}/_ato2019-2022/2020/lei/L13988.htm": L13988,
    f"{P}/leis/L5172compilado.htm": L5172,
    f"{P}/decreto/1970-1979/D70235.htm": D70235,
    f"{P}/leis/lcp/Lcp87.htm": LCP87,
    f"{P}/constituicao/constituicao.htm": CF88,
}


def abrir(url: str) -> tuple[int, bytes | None, str | None]:
    """Substituto de `citacoes._abrir`. O que não está no dicionário dá 404."""
    corpo = FONTE.get(url)
    return (200, corpo, None) if corpo else (404, None, None)
