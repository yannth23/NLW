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
