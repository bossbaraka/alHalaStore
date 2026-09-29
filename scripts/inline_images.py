#!/usr/bin/env python3
"""Build self-contained digital menu with all assets inlined as data URIs.

Produces sweet-story-menu.html — a fully standalone, single-file menu
ready to open offline, share via WhatsApp, or host anywhere.
"""
import base64
import re
import os

SRC = "index.html"
OUT = "sweet-story-menu.html"

def mime(path):
    p = path.lower()
    if p.endswith(".png"):
        return "image/png"
    if p.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if p.endswith(".ttf"):
        return "font/ttf"
    return "application/octet-stream"

def to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def main():
    if not os.path.exists(SRC):
        print(f"ERROR: {SRC} not found in {os.getcwd()}")
        return

    with open(SRC, "r", encoding="utf-8") as f:
        html = f.read()

    inlined_count = 0

    # Inline HTML attributes: src="images/...", href="images/...", content="images/..."
    def repl_attr(m):
        nonlocal inlined_count
        attr, path = m.group(1), m.group(2)
        if not os.path.exists(path):
            print(f"WARN: missing {path}")
            return m.group(0)
        b64 = to_base64(path)
        inlined_count += 1
        print(f"  + Inlined {path} ({len(b64)//1024} KB)")
        return f'{attr}"data:{mime(path)};base64,{b64}"'

    html = re.sub(r'((?:src|href|content)=)"(images/[^"]+)"', repl_attr, html)

    # Inline CSS urls: url('images/...') or url('assets/fonts/...')
    def repl_css(m):
        nonlocal inlined_count
        path = m.group(2)
        if not os.path.exists(path):
            print(f"WARN: missing {path}")
            return m.group(0)
        b64 = to_base64(path)
        inlined_count += 1
        print(f"  + Inlined CSS {path} ({len(b64)//1024} KB)")
        return f"url('data:{mime(path)};base64,{b64}')"

    html = re.sub(r"url\((['\"]?)((?:images|assets)/[^'\")]+)\1\)", repl_css, html)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUT) // 1024
    print(f"\n[BUILD SUCCESS] Created {OUT}: {size_kb} KB ({inlined_count} assets embedded)")

if __name__ == "__main__":
    main()
