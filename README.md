# Prumo

Central de prompts de integridade corporativa para o encontro com a fiscalização.

O produto gera o documento certo no momento da abordagem — ata de atendimento, pedido de
fundamentação legal por escrito, registro de solicitação indevida e comunicação à corregedoria
e à ouvidoria. A tese do produto é uma só: **tornar a recusa documentada mais fácil do que a
cedência silenciosa.**

Prumo é ferramenta de documentação e treinamento. Não substitui advogado nem parecer jurídico,
e nenhum prompt orienta pagamento, facilitação, intermediação informal ou ocultação de registro
perante agente público.

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

### Ilustrações

Todo o material gráfico é SVG autoral desenhado no repositório — o CSP da publicação bloqueia
qualquer imagem externa. As cores da ilustração são tokens `--art-*` redefinidos por tema, de
modo que o desenho acompanha o claro e o escuro da página.

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
python3 design/build.py
```

Lê cada arquivo de `design/src`, substitui o marcador `/* FONTFACE */` pelas regras `@font-face`
declaradas no comentário `<!-- FONTS: ... -->` do próprio arquivo e escreve o resultado em
`design/dist`. Sem dependências.
