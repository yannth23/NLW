# Prumo

Segunda opinião sobre o auto de infração fiscal.

O produto lê o auto, apura qual redação da norma regia o fato gerador, confere o lançamento
parcela a parcela contra a faixa legal, quantifica o custo de cada caminho (defender, pagar com
redução, parcelar, transacionar) e devolve a data limite do rito do ente autuante.

**A posição competitiva é verificabilidade, não corpus.** A categoria de pesquisa tributária com
IA já tem legislação, CARF, STJ e STF. O que ela não resolve é citação que não existe e norma
aplicada na redação errada. Duas regras de produto endereçam isso:

1. Toda citação passa por verificação contra a fonte oficial antes de chegar ao usuário, com data
   de consulta registrada. Quando a verificação falha, o campo sai em branco e o laudo lista o
   termo pesquisado.
2. Toda norma vem na redação vigente na data do fato gerador, não na de hoje.

O produto se mede: cem autos reais anonimizados com desfecho conhecido, rodados a cada versão,
em três métricas (citações que resolvem, vigência correta, valor dentro da faixa). O número
acompanha a proposta comercial e não a página, porque envelhece.

## Verificador de citação

O verificador é a peça que sustenta a promessa. Ele roda **fora do modelo**, sem chave de API,
e confere a saída de qualquer IA — inclusive a nossa. São quatro etapas:

1. **Extrair.** `citacoes.extrair(texto)` reconhece lei, lei complementar, decreto, decreto-lei,
   CTN, Constituição e súmulas nas grafias em que aparecem de verdade (`Lei nº 9.784, de 1999`,
   `Lei 9784/99`, `lei 9.784/1999`), e amarra o `art. N` mais próximo, antes ou depois da norma.
   Um ponto final entre os dois corta o vínculo.
2. **Resolver a URL.** `citacoes.urls(c)` monta as candidatas no Planalto. Não há padrão único:
   lei anterior a 2000 fica em `/leis/L9784.htm`, de 2003 em diante em blocos de quatro anos
   (`/_ato2019-2022/2020/lei/L13988.htm`), lei complementar em `/leis/lcp/`, e várias existem
   só na versão `compilado`. A lista vai da mais provável para a menos.
3. **Abrir e achar o artigo.** Baixa a página, tira o HTML, recorta o bloco do `Art. N` até o
   artigo seguinte. `Art. 5` não casa dentro de `Art. 50`.
4. **Classificar.** `CONFERE` só quando a norma abriu **e** o artigo estava lá. `ARTIGO_AUSENTE`
   quando a lei existe e o artigo não — é o erro mais comum e o mais difícil de perceber lendo.
   `NAO_ENCONTRADA`, `SEM_FONTE` (súmula, que não tem URL determinística) e `INDISPONIVEL`
   (fonte fora do ar) **não passam**. Falha fechada: se não deu para abrir, não sai.

Quando o bloco do artigo contém `(Redação dada pela Lei nº ...)`, o relatório marca a alteração.
É o gancho da regra de vigência: artigo alterado exige saber a data do fato gerador.

```bash
python3 -m prumo prompts                                            # a biblioteca
python3 -m prumo verificar prumo/exemplo/saida-com-erro.txt --demo  # sem rede
python3 -m prumo verificar parecer.txt                              # contra o Planalto
python3 -m prumo avaliar --prompt 02 auto.txt --dry-run             # a requisição montada
ANTHROPIC_API_KEY=... python3 -m prumo avaliar --prompt 02 auto.txt # roda e verifica
python3 -m unittest prumo.testes -v                                 # 32 testes, sem rede
```

`prumo/exemplo/saida-com-erro.txt` imita um parecer de IA com onze citações, três delas
plantadas. O verificador reprova a lei que não existe e o artigo que não consta da lei, e
devolve `exit 1`. `prumo/exemplo/auto-exemplo.txt` é um auto de ICMS sintético para o `avaliar`.

`prumo/fonte_simulada.py` é um recorte curto das normas no formato do Planalto, usado pelos
testes e pelo `--demo`. Não é cache: nada que sai dele vale como citação verificada.

O `avaliar` chama `claude-opus-5` com `output_config.format` de tipo `json_schema`
(`prumo/laudo.py`), o preâmbulo em bloco de sistema cacheado, e passa a resposta pelo
verificador antes de imprimir. O esquema tem um campo obrigatório `nao_verificado`, para que
"não consegui confirmar" seja uma saída barata — quando a única saída possível é um texto
bem escrito, é o texto bem escrito que o modelo entrega.

## Estado atual

Direção visual **B — Painel** aprovada e desenvolvida em `design/src/index.html`: sala de
controle de compliance, Archivo com IBM Plex Mono, console de prompt operável por abas,
quadro de fases e severidades, e ilustração própria do aperto de mão entre executivo e
braço robótico.

As opções A e C ficam no repositório como registro da escolha:

| Opção | Nome | Mundo visual |
|---|---|---|
| A | Autos | Dossiê jurídico — papel frio, Spectral, margem com citações legais, carimbo |
| C | Banca | Institucional — Bodoni Moda, linha de prumo em ouro, um único bloco invertido |

### Sem ilustração

A faixa central não usa imagem. O aperto de mão entre humano e robô é o clichê mais gasto da
categoria, e o console operável, o quadro de fases e a tabela de artefatos já provam capacidade
melhor do que uma foto provaria. No lugar dela, um painel de declaração: o texto forte à
esquerda sobre um filete teal, a glosa em três parágrafos à direita.

Os geradores das duas tentativas de ilustração continuam em `design/art/`, sem uso:
`gen_handshake.py` (enquadramento fechado nas mãos) e `gen_scene.py` (plano médio com as duas
figuras). Vetor desenhado à mão não alcança realismo fotográfico — o rosto é o que denuncia.

### Ilustrações

Todo o material gráfico é SVG autoral desenhado no repositório — o CSP da publicação bloqueia
qualquer imagem externa.

O aperto de mão é gerado por `design/art/gen_handshake.py`, que emite o fragmento SVG para colar
em `design/src/index.html`. `design/art/gen_scene.py` desenha a mesma cena em plano médio, com o
executivo de perfil e o robô inteiros; ficou estilizada demais para o tom do site e não está em
uso, mas continua no repositório. Os dedos do robô e o polegar humano são cadeias de cápsulas com
largura decrescente, e o biseléé derivado da mesma curva — escrever isso à mão eram cinquenta
elementos quase idênticos que saíam de alinhamento a cada ajuste.

Os materiais (pele, lã do terno, aço) são físicos e não invertem com o tema: só o fundo, a luz
principal e a cor da sombra projetada seguem a página, via tokens `--art-*`. O fundo e a luz
ficam no CSS do painel, não no SVG, porque o desenho fica em letterbox dentro de um painel mais
alto e um `rect` pintado dentro do SVG terminaria na borda do viewBox, deixando emenda visível.

## Estrutura

```
design/
  build.py     inlina as fontes woff2 como data URI (o CSP da publicação bloqueia CDN de fonte)
  fonts/       woff2 latin — Spectral, IBM Plex Sans/Mono, Archivo, Bodoni Moda, Public Sans
  src/         fontes editáveis — index.html é o site, opcao-*.html são as alternativas
  dist/        páginas geradas, com as fontes embutidas
```

## Build

```bash
python3 design/build.py       # gera dist/ a partir de src/
python3 design/export_pdf.py  # gera dist/prumo.pdf a partir de dist/index.html
```

Lê cada arquivo de `design/src`, substitui o marcador `/* FONTFACE */` pelas regras `@font-face`
declaradas no comentário `<!-- FONTS: ... -->` do próprio arquivo e escreve o resultado em
`design/dist`. Sem dependências.
