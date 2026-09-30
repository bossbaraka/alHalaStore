#!/usr/bin/env python3
"""Refine box pricing: drop the middle maamoul box, set pastry box prices."""
SRC = "index.html"
html = open(SRC, encoding="utf-8").read()
changes = []


def rep(old, new, count=1, label=""):
    global html
    n = html.count(old)
    if n != count:
        raise SystemExit(f"FAIL [{label}]: expected {count}, found {n}")
    html = html.replace(old, new)
    changes.append(f"{label} ({n}x)")


# ---- maamoul: remove the plain middle "بوكس" row ----
rep(
    '          <li><span class="q-name">بوكس</span><span class="leader"></span><span class="q-price"><b>45</b><span>ريال</span></span></li>\n',
    "",
    1,
    "drop middle maamoul box",
)

# ---- pastries: large 60 / small 30 ----
rep(
    '          <div class="b-box-line"><span class="q-name">بوكس كبير</span><span class="leader"></span><span class="q-price"><b>30</b><span>ريال</span></span></div>\n'
    '          <div class="b-box-line"><span class="q-name">بوكس وسط</span><span class="leader"></span><span class="q-price"><b>20</b><span>ريال</span></span></div>\n',
    '          <div class="b-box-line"><span class="q-name">بوكس كبير</span><span class="leader"></span><span class="q-price"><b>60</b><span>ريال</span></span></div>\n'
    '          <div class="b-box-line"><span class="q-name">بوكس صغير</span><span class="leader"></span><span class="q-price"><b>30</b><span>ريال</span></span></div>\n',
    1,
    "pastry box prices (60 / 30)",
)

rep(
    "ومتوفرة بمقاسين: بوكس وسط وبوكس كبير.",
    "ومتوفرة بمقاسين: بوكس صغير وبوكس كبير.",
    1,
    "pastry description sizes",
)

open(SRC, "w", encoding="utf-8").write(html)
print("[OK] pricing refined:")
for c in changes:
    print("  -", c)
