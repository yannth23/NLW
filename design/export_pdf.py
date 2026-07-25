#!/usr/bin/env python3
"""Exports dist/index.html to dist/prumo.pdf for sharing offline.

Prints in the light theme: the page is theme-aware, and a dark ground turns a
shared PDF into an unprintable wall of ink.

Requires playwright and the Chromium that ships with this environment:

    pip install playwright
    python3 design/export_pdf.py
"""

import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "dist" / "index.html"
OUT = ROOT / "dist" / "prumo.pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def main():
    if not SRC.exists():
        sys.exit(f"{SRC} não existe — rode design/build.py primeiro")

    with sync_playwright() as p:
        launch = {"executable_path": CHROME} if pathlib.Path(CHROME).exists() else {}
        browser = p.chromium.launch(**launch)
        ctx = browser.new_context(viewport={"width": 1180, "height": 1400},
                                  color_scheme="light")
        page = ctx.new_page()
        page.goto(SRC.as_uri())
        page.wait_for_timeout(1200)          # let the inlined faces settle
        page.emulate_media(media="print", color_scheme="light")
        page.pdf(path=str(OUT), format="A4", print_background=True,
                 margin={"top": "14mm", "bottom": "14mm",
                         "left": "12mm", "right": "12mm"})
        browser.close()

    print(f"{OUT} — {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
