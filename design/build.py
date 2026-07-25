#!/usr/bin/env python3
"""Inlines woff2 faces as data URIs so the published page never touches a font CDN.

Each source file in src/ declares the faces it needs in a comment:

    <!-- FONTS: Spectral=spectral:400,600 | Plex Sans=ibm-plex-sans:500 -->

build.py replaces the marker /* FONTFACE */ with the generated @font-face rules
and writes the result to dist/.
"""

import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
FONTS = ROOT / "fonts"
SRC = ROOT / "src"
DIST = ROOT / "dist"

DECL = re.compile(r"<!--\s*FONTS:\s*(.+?)\s*-->", re.S)


def face(family, slug, weight):
    path = FONTS / f"{slug}-latin-{weight}-normal.woff2"
    data = base64.b64encode(path.read_bytes()).decode()
    return (
        "@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
        "font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}"
        % (family, weight, data)
    )


def build(src):
    html = src.read_text()
    match = DECL.search(html)
    if not match:
        raise SystemExit(f"{src.name}: missing FONTS declaration")

    rules = []
    for group in match.group(1).split("|"):
        family, spec = group.strip().split("=")
        slug, weights = spec.split(":")
        for weight in weights.split(","):
            rules.append(face(family.strip(), slug.strip(), weight.strip()))

    out = html.replace("/* FONTFACE */", "\n".join(rules))
    target = DIST / src.name
    target.write_text(out)
    print(f"{src.name} -> dist/{src.name}  ({len(out) // 1024} KB, {len(rules)} faces)")


if __name__ == "__main__":
    DIST.mkdir(exist_ok=True)
    for src in sorted(SRC.glob("*.html")):
        build(src)
