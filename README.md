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

Fase de direção visual. Três propostas completas, cada uma com identidade própria:

| Opção | Nome | Mundo visual |
|---|---|---|
| A | Autos | Dossiê jurídico — papel frio, Spectral, margem com citações legais, carimbo |
| B | Painel | Sala de controle de compliance — Archivo e mono, console de prompt operável, severidades |
| C | Banca | Institucional — Bodoni Moda, linha de prumo em ouro, um único bloco invertido |

## Estrutura

```
design/
  build.py     inlina as fontes woff2 como data URI (o CSP da publicação bloqueia CDN de fonte)
  fonts/       woff2 latin — Spectral, IBM Plex Sans/Mono, Archivo, Bodoni Moda, Public Sans
  src/         fontes editáveis das três opções
  dist/        páginas geradas, com as fontes embutidas
```

## Build

```bash
python3 design/build.py
```

Lê cada arquivo de `design/src`, substitui o marcador `/* FONTFACE */` pelas regras `@font-face`
declaradas no comentário `<!-- FONTS: ... -->` do próprio arquivo e escreve o resultado em
`design/dist`. Sem dependências.
