"""Extração e verificação de citações legais contra a fonte oficial.

Esta é a peça que sustenta a promessa do produto. A regra é: nenhuma citação
chega ao usuário sem ter sido aberta na origem, com data de consulta
registrada. Quando a verificação falha, o campo sai em branco e o laudo diz
qual termo foi pesquisado — nunca um número plausível no lugar.

O módulo é deliberadamente separado do modelo. Ele confere a saída de
qualquer IA, inclusive a nossa, e roda sem chave de API.

Uso:
    from prumo import citacoes
    achados = citacoes.extrair(texto)
    laudo = citacoes.verificar(achados)
    print(citacoes.relatorio(laudo))
"""

from __future__ import annotations

import dataclasses
import datetime
import html
import os
import re
import ssl
import urllib.error
import urllib.request

PLANALTO = "https://www.planalto.gov.br/ccivil_03"
UA = "Prumo/0.1 (verificador de citações; contato@prumo.example)"
TIMEOUT = 20

# ---------------------------------------------------------------- extração

# "Lei nº 9.784, de 1999" / "Lei 9784/99" / "Lei Complementar nº 123/2006"
# O lookbehind existe porque "Decreto-Lei nº 1.598" contém uma "Lei nº 1.598"
# que não é lei nenhuma.
RE_LEI = re.compile(
    r"(?<!Decreto-)(?<!Decreto )\bLei\s+(?P<compl>Complementar\s+)?"
    r"(?:n[ºo°]?\.?\s*)?(?P<num>\d{1,3}(?:\.\d{3})*|\d{3,6})"
    r"\s*(?:,\s*de\s+(?:\d{1,2}\s+de\s+\w+\s+de\s+)?|[/])\s*(?P<ano>\d{2,4})",
    re.I,
)

# "Decreto nº 70.235/1972" / "Decreto-Lei nº 1.598, de 1977"
RE_DECRETO = re.compile(
    r"\bDecreto(?P<dl>[-\s]Lei)?\s+"
    r"(?:n[ºo°]?\.?\s*)?(?P<num>\d{1,3}(?:\.\d{3})*|\d{3,6})"
    r"\s*(?:,\s*de\s+(?:\d{1,2}\s+de\s+\w+\s+de\s+)?|[/])\s*(?P<ano>\d{2,4})",
    re.I,
)

RE_CTN = re.compile(r"\b(?:CTN|C[óo]digo\s+Tribut[áa]rio\s+Nacional)\b", re.I)
RE_CF = re.compile(r"\b(?:CF/?88|Constitui[çc][ãa]o\s+Federal|CRFB)\b", re.I)

RE_SUMULA_CARF = re.compile(
    r"\bS[úu]mula\s+CARF\s+(?:vinculante\s+)?n?[ºo°]?\.?\s*(?P<num>\d{1,3})", re.I
)
RE_SUMULA_TRIB = re.compile(
    r"\bS[úu]mula\s+(?:vinculante\s+)?n?[ºo°]?\.?\s*(?P<num>\d{1,4})"
    r"\s*(?:d[oa]\s+)?(?P<corte>STF|STJ)\b",
    re.I,
)
RE_SUMULA_TRIB_2 = re.compile(
    r"\bS[úu]mula\s+(?P<corte>Vinculante|STF|STJ)\s+n?[ºo°]?\.?\s*(?P<num>\d{1,4})", re.I
)

# "art. 26", "artigo 150", "arts. 173 e 174", "art. 5º"
RE_ART = re.compile(r"\barts?(?:igos?)?\.?\s*(\d{1,4})\s*[ºo°]?", re.I)

# Blocos das leis ordinárias no Planalto, por ano de publicação.
BLOCOS = [
    (2023, 2026, "2023-2026"),
    (2019, 2022, "2019-2022"),
    (2015, 2018, "2015-2018"),
    (2011, 2014, "2011-2014"),
    (2007, 2010, "2007-2010"),
    (2003, 2006, "2003-2006"),
]


@dataclasses.dataclass
class Citacao:
    """Uma referência normativa como apareceu no texto, já normalizada."""

    bruto: str
    tipo: str          # lei | lei-complementar | decreto | decreto-lei | ctn | cf | sumula
    numero: str
    ano: str | None
    artigo: str | None
    origem: int        # posição no texto, para desempate e ordenação

    @property
    def rotulo(self) -> str:
        nomes = {
            "lei": "Lei",
            "lei-complementar": "Lei Complementar",
            "decreto": "Decreto",
            "decreto-lei": "Decreto-Lei",
            "ctn": "CTN",
            "cf": "Constituição Federal",
            "sumula": "Súmula",
        }
        base = nomes.get(self.tipo, self.tipo)
        if self.tipo in ("ctn", "cf"):
            corpo = base
        elif self.tipo == "sumula":
            corpo = f"Súmula {self.numero}"
        else:
            corpo = f"{base} {int(self.numero):,}".replace(",", ".") + f"/{self.ano}"
        return f"{corpo}, art. {self.artigo}" if self.artigo else corpo

    @property
    def chave(self) -> tuple:
        return (self.tipo, self.numero, self.ano, self.artigo)


def _ano4(ano: str) -> str:
    """Normaliza ano de dois dígitos. 88 vira 1988, 06 vira 2006."""
    if len(ano) == 4:
        return ano
    n = int(ano)
    return str(1900 + n) if n >= 30 else str(2000 + n)


def _artigo_proximo(texto: str, ini: int, fim: int, janela: int = 90) -> str | None:
    """Procura o `art. N` mais próximo da norma, antes ou depois.

    "art. 26 da Lei 9.784/1999" e "Lei 9.784/1999, art. 26" são a mesma coisa e
    aparecem nas duas ordens no mesmo parágrafo.
    """
    antes = texto[max(0, ini - janela):ini]
    achados = list(RE_ART.finditer(antes))
    if achados:
        # o último antes da norma é o que a rege
        entre = antes[achados[-1].end():]
        if not re.search(r"[.;]\s", entre):
            return achados[-1].group(1)
    depois = texto[fim:fim + janela]
    m = RE_ART.search(depois)
    if m and not re.search(r"[.;]\s", depois[:m.start()]):
        return m.group(1)
    return None


def extrair(texto: str) -> list[Citacao]:
    """Devolve as citações do texto, sem repetição, na ordem em que aparecem."""
    achados: list[Citacao] = []

    for m in RE_LEI.finditer(texto):
        tipo = "lei-complementar" if m.group("compl") else "lei"
        achados.append(Citacao(
            bruto=m.group(0),
            tipo=tipo,
            numero=m.group("num").replace(".", ""),
            ano=_ano4(m.group("ano")),
            artigo=_artigo_proximo(texto, m.start(), m.end()),
            origem=m.start(),
        ))

    for m in RE_DECRETO.finditer(texto):
        achados.append(Citacao(
            bruto=m.group(0),
            tipo="decreto-lei" if m.group("dl") else "decreto",
            numero=m.group("num").replace(".", ""),
            ano=_ano4(m.group("ano")),
            artigo=_artigo_proximo(texto, m.start(), m.end()),
            origem=m.start(),
        ))

    for regex, tipo, numero in ((RE_CTN, "ctn", "5172"), (RE_CF, "cf", "1988")):
        for m in regex.finditer(texto):
            achados.append(Citacao(
                bruto=m.group(0),
                tipo=tipo,
                numero=numero,
                ano="1966" if tipo == "ctn" else "1988",
                artigo=_artigo_proximo(texto, m.start(), m.end()),
                origem=m.start(),
            ))

    for m in RE_SUMULA_CARF.finditer(texto):
        achados.append(Citacao(
            bruto=m.group(0), tipo="sumula", numero=f"CARF nº {m.group('num')}",
            ano=None, artigo=None, origem=m.start(),
        ))
    for regex in (RE_SUMULA_TRIB, RE_SUMULA_TRIB_2):
        for m in regex.finditer(texto):
            corte = m.group("corte").upper()
            rot = "Vinculante" if corte == "VINCULANTE" else corte
            achados.append(Citacao(
                bruto=m.group(0), tipo="sumula", numero=f"{rot} nº {m.group('num')}",
                ano=None, artigo=None, origem=m.start(),
            ))

    achados.sort(key=lambda c: c.origem)
    vistas: set[tuple] = set()
    unicas = []
    for c in achados:
        if c.chave in vistas:
            continue
        vistas.add(c.chave)
        unicas.append(c)
    return unicas


# ---------------------------------------------------------------- resolução

def urls(c: Citacao) -> list[str]:
    """URLs candidatas na fonte oficial, da mais provável para a menos.

    O Planalto não tem um padrão único: leis antigas ficam na raiz, as de 2003
    em diante em blocos de quatro anos, e várias existem em duas grafias
    (`L9784.htm` e `l9784.htm`) ou só na versão compilada.
    """
    n, ano = c.numero, int(c.ano or 0)

    if c.tipo == "cf":
        return [f"{PLANALTO}/constituicao/constituicao.htm"]
    if c.tipo == "ctn":
        return [f"{PLANALTO}/leis/L5172compilado.htm", f"{PLANALTO}/leis/L5172.htm"]
    if c.tipo == "lei-complementar":
        return [f"{PLANALTO}/leis/lcp/Lcp{n}.htm", f"{PLANALTO}/leis/lcp/lcp{n}.htm"]
    if c.tipo == "decreto-lei":
        return [f"{PLANALTO}/decreto-lei/Del{n}.htm",
                f"{PLANALTO}/decreto-lei/del{n}.htm"]
    if c.tipo == "decreto":
        cands = [f"{PLANALTO}/decreto/D{n}.htm", f"{PLANALTO}/decreto/d{n}.htm"]
        for ini, fim, bloco in BLOCOS:
            if ini <= ano <= fim:
                cands.insert(0, f"{PLANALTO}/_ato{bloco}/{ano}/decreto/D{n}.htm")
        if 1970 <= ano <= 1979:
            cands.insert(0, f"{PLANALTO}/decreto/1970-1979/D{n}.htm")
        if 1980 <= ano <= 1989:
            cands.insert(0, f"{PLANALTO}/decreto/1980-1989/D{n}.htm")
        if 1990 <= ano <= 1994:
            cands.insert(0, f"{PLANALTO}/decreto/1990-1994/D{n}.htm")
        return cands
    if c.tipo == "lei":
        cands = []
        for ini, fim, bloco in BLOCOS:
            if ini <= ano <= fim:
                cands.append(f"{PLANALTO}/_ato{bloco}/{ano}/lei/L{n}.htm")
                cands.append(f"{PLANALTO}/_ato{bloco}/{ano}/lei/l{n}.htm")
        cands += [f"{PLANALTO}/leis/L{n}.htm",
                  f"{PLANALTO}/leis/L{n}compilado.htm",
                  f"{PLANALTO}/leis/l{n}.htm"]
        if 2000 <= ano <= 2002:
            cands.insert(0, f"{PLANALTO}/leis/{ano}/L{n}.htm")
        return cands
    return []


def _limpa(bruto: bytes) -> str:
    """HTML do Planalto para texto corrido, preservando os marcadores de artigo."""
    txt = bruto.decode("latin-1", errors="replace")
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = txt.replace("\xa0", " ")
    return re.sub(r"[ \t]{2,}", " ", txt)


def _bloco_do_artigo(texto: str, numero: str) -> str | None:
    """Recorta o texto do artigo N, até o começo do artigo seguinte."""
    padrao = re.compile(rf"\bArt\.?\s*0*{re.escape(numero)}\s*[ºo°]?\s*[-.\s]", re.I)
    m = padrao.search(texto)
    if not m:
        return None
    resto = texto[m.end():]
    prox = re.search(r"\bArt\.?\s*\d", resto)
    return resto[:prox.start()] if prox else resto[:6000]


def _abrir(url: str) -> tuple[int, bytes | None, str | None]:
    ctx = ssl.create_default_context()
    bundle = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    if os.path.exists(bundle):
        try:
            ctx.load_verify_locations(bundle)
        except OSError:
            pass
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return r.status, r.read(), None
    except urllib.error.HTTPError as e:
        return e.code, None, None
    except Exception as e:                       # DNS, TLS, proxy, timeout
        return 0, None, f"{type(e).__name__}: {e}"


@dataclasses.dataclass
class Resultado:
    citacao: Citacao
    status: str          # CONFERE | ARTIGO_AUSENTE | NAO_ENCONTRADA | SEM_FONTE | INDISPONIVEL
    url: str | None
    consultado_em: str
    nota: str = ""
    alteracoes: list[str] = dataclasses.field(default_factory=list)

    @property
    def passa(self) -> bool:
        return self.status == "CONFERE"


def verificar(citacoes: list[Citacao]) -> list[Resultado]:
    """Abre cada citação na fonte oficial e devolve o que encontrou.

    Sem fonte pública estável (súmulas do CARF e dos tribunais não têm URL
    determinística), o status é SEM_FONTE. Isso não é aprovação: o laudo
    trata SEM_FONTE e INDISPONIVEL como campo em branco, igual a
    NAO_ENCONTRADA. Só CONFERE libera a citação para o usuário.
    """
    hoje = datetime.date.today().isoformat()
    saida: list[Resultado] = []
    cache: dict[str, tuple[int, bytes | None, str | None]] = {}

    for c in citacoes:
        candidatas = urls(c)
        if not candidatas:
            saida.append(Resultado(c, "SEM_FONTE", None, hoje,
                                   "sem URL determinística na fonte oficial; "
                                   "exige conferência manual"))
            continue

        corpo = None
        achada = None
        falha = None
        for u in candidatas:
            if u not in cache:
                cache[u] = _abrir(u)
            code, body, err = cache[u]
            if code == 200 and body:
                corpo, achada = body, u
                break
            if err:
                falha = err

        if corpo is None:
            if falha:
                saida.append(Resultado(c, "INDISPONIVEL", candidatas[0], hoje,
                                       f"fonte inacessível ({falha})"))
            else:
                saida.append(Resultado(c, "NAO_ENCONTRADA", candidatas[0], hoje,
                                       "nenhuma das URLs candidatas respondeu 200"))
            continue

        texto = _limpa(corpo)
        if c.artigo is None:
            saida.append(Resultado(c, "CONFERE", achada, hoje, "norma localizada"))
            continue

        bloco = _bloco_do_artigo(texto, c.artigo)
        if bloco is None:
            saida.append(Resultado(c, "ARTIGO_AUSENTE", achada, hoje,
                                   f"a norma existe, o art. {c.artigo} não consta dela"))
            continue

        alteracoes = re.findall(
            r"\((?:Reda[çc][ãa]o dada|Inclu[íi]d[oa]|Revogad[oa]|Vig[êe]ncia)[^)]{0,120}\)",
            bloco[:4000])
        nota = "artigo localizado no corpo da norma"
        if alteracoes:
            nota += "; artigo alterado — confira a redação na data do fato gerador"
        saida.append(Resultado(c, "CONFERE", achada, hoje, nota,
                               [a.strip() for a in alteracoes[:4]]))

    return saida


# ---------------------------------------------------------------- relatório

SIMBOLO = {
    "CONFERE": "ok  ",
    "ARTIGO_AUSENTE": "FALHA",
    "NAO_ENCONTRADA": "FALHA",
    "SEM_FONTE": "manual",
    "INDISPONIVEL": "?   ",
}


def relatorio(resultados: list[Resultado], largura: int = 92) -> str:
    """Relatório em texto. Cada linha diz o que foi aberto e o que se achou."""
    if not resultados:
        return "Nenhuma citação legal encontrada no texto."

    linhas = ["CITAÇÃO".ljust(46) + "STATUS".ljust(16) + "CONSULTA", "-" * largura]
    for r in resultados:
        linhas.append(r.citacao.rotulo[:45].ljust(46)
                      + r.status.ljust(16) + r.consultado_em)
        linhas.append("    " + r.nota)
        if r.url:
            linhas.append("    " + r.url)
        for a in r.alteracoes:
            linhas.append("    ^ " + a[:largura - 8])
        linhas.append("")

    confere = sum(r.passa for r in resultados)
    falhas = [r for r in resultados
              if r.status in ("ARTIGO_AUSENTE", "NAO_ENCONTRADA")]
    pendentes = [r for r in resultados
                 if r.status in ("SEM_FONTE", "INDISPONIVEL")]

    linhas.append("-" * largura)
    linhas.append(f"{len(resultados)} citações — {confere} conferem, "
                  f"{len(falhas)} não resolvem, {len(pendentes)} sem conferência automática")
    if falhas:
        linhas.append("")
        linhas.append("Não entregar ao usuário. Sai em branco no laudo, com o termo pesquisado:")
        for r in falhas:
            linhas.append(f"  · {r.citacao.rotulo}  (pesquisado: \"{r.citacao.bruto}\")")
    if pendentes:
        linhas.append("")
        linhas.append("Exigem conferência humana antes de sair:")
        for r in pendentes:
            linhas.append(f"  · {r.citacao.rotulo}  — {r.nota}")
    return "\n".join(linhas)
