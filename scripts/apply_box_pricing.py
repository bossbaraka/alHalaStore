#!/usr/bin/env python3
"""Switch the menu from weight-based pricing to box-based pricing (box sizes)."""
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


# ------------------------------------------------------------------
# 1) MAAMOUL: weights  ->  box sizes  (same price ladder)
# ------------------------------------------------------------------
rep('<span class="latin-label">Pricing</span>', '<span class="latin-label">Box Sizes</span>', 1, "maamoul pricing label")

rep(
    '<span class="unit"><b>ريال</b><span>للكيلو</span></span>',
    '<span class="unit"><b>ريال</b><span>للبوكس الكبير</span></span>',
    1,
    "maamoul main price unit",
)
rep(
    '<p class="price-note">اختر الكمية التي تناسبك — من ربع كيلو إلى كيلو كامل.</p>',
    '<p class="price-note">اختر البوكس الذي يناسبك — من بوكس صغير إلى بوكس كبير، معمول ومعبّأ وجاهز للتقديم.</p>',
    1,
    "maamoul price note",
)
rep(
    '          <li><span class="q-name">ربع كيلو</span><span class="leader"></span><span class="q-price"><b>16</b><span>ريال</span></span></li>\n'
    '          <li><span class="q-name">نصف كيلو</span><span class="leader"></span><span class="q-price"><b>30</b><span>ريال</span></span></li>\n'
    '          <li><span class="q-name">كيلو</span><span class="leader"></span><span class="q-price"><b>60</b><span>ريال</span></span></li>\n',
    '          <li><span class="q-name">بوكس صغير</span><span class="leader"></span><span class="q-price"><b>16</b><span>ريال</span></span></li>\n'
    '          <li><span class="q-name">بوكس وسط</span><span class="leader"></span><span class="q-price"><b>30</b><span>ريال</span></span></li>\n'
    '          <li><span class="q-name">بوكس</span><span class="leader"></span><span class="q-price"><b>45</b><span>ريال</span></span></li>\n'
    '          <li><span class="q-name">بوكس كبير</span><span class="leader"></span><span class="q-price"><b>60</b><span>ريال</span></span></li>\n',
    1,
    "maamoul box price list",
)

# ------------------------------------------------------------------
# 2) PASTRIES: box large + box medium
# ------------------------------------------------------------------
rep(
    '        <div class="b-price"><b>30 ر.س</b><span>للبوكس</span></div>',
    '        <div class="b-boxes">\n'
    '          <div class="b-box-line"><span class="q-name">بوكس كبير</span><span class="leader"></span><span class="q-price"><b>30</b><span>ريال</span></span></div>\n'
    '          <div class="b-box-line"><span class="q-name">بوكس وسط</span><span class="leader"></span><span class="q-price"><b>20</b><span>ريال</span></span></div>\n'
    '        </div>',
    1,
    "pastry box prices",
)

rep(
    ".b-info .b-price span{font-size:12.5px;color:var(--warm-wheat)}",
    ".b-info .b-price span{font-size:12.5px;color:var(--warm-wheat)}\n"
    ".b-info .b-boxes{margin-top:var(--s4);display:flex;flex-direction:column;gap:12px;border-top:var(--line);padding-top:var(--s2);max-width:330px}\n"
    ".b-info .b-box-line{display:flex;align-items:baseline;gap:var(--s2);width:100%}\n"
    ".b-info .b-box-line .q-name{font-size:15px;font-weight:500;color:var(--deep-dough)}\n"
    ".b-info .b-box-line .leader{flex:1;min-width:24px;border-bottom:1px dotted rgba(165,139,103,.45);transform:translateY(-5px)}\n"
    ".b-info .b-box-line .q-price{display:flex;align-items:baseline;gap:6px}\n"
    ".b-info .b-box-line .q-price b{font-family:var(--serif-ar);font-size:23px;font-weight:700;color:var(--deep-dough)}\n"
    ".b-info .b-box-line .q-price span{font-size:12px;color:var(--warm-wheat)}",
    1,
    "pastry box price styles",
)

rep(
    "<p class=\"b-desc\">صندوق معجنات محشوّة، مخبوزة حتى الذهبيّة — للمذاق المالح الذي يكمل الحلو.</p>",
    "<p class=\"b-desc\">صناديق معجنات محشوّة، مخبوزة حتى الذهبيّة — للمذاق المالح الذي يكمل الحلو. متوفرة Sizes officially here.</p>".replace(
        " متوفرة Sizes officially here.", " ومتوفرة بمقاسين: بوكس وسط وبوكس كبير."
    ),
    1,
    "pastry description",
)

# ------------------------------------------------------------------
# 3) Snapchat button in the contact page
# ------------------------------------------------------------------
SC_GHOST = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'
            '<path d="M12 2.7c-3.2 0-5.5 2.4-5.5 5.6 0 .5 0 1 .1 1.4-.4.2-.9.2-1.4 0-.6-.2-1.1.3-1 1 .1.6.6 1.1 1.2 1.4.4.2.6.5.5.9-.2.7-1 1.3-1.8 1.6-.5.2-.6.8-.2 1.1.9.7 2 1.1 3.1 1.3.1.6.3 1 .7 1.5.4.4 1 .3 '
            '1.3-.2.3-.4.8-.4 1.1 0 .3.3.5.6 1 .2.5 1 .4 1.2-.1.2-.4.3-.7.6-1 .3-.4.8-.4 1.1 0 .3.4.4.8.6 1 .2.5 1 .4 1.2-.1.1-.5.3-.9.7-1.5 '
            '1.1-.2 2.2-.6 3.1-1.3.4-.3.3-.9-.2-1.1-.8-.3-1.6-.9-1.8-1.6-.1-.4.1-.7.5-.9.6-.3 1.1-.8 1.2-1.4.1-.7-.4-1.2-1-1-.5.2-1 .2-1.4 0 '
            '.1-.4.1-.9.1-1.4 0-3.2-2.3-5.6-5.5-5.6Z"/></svg>')

rep(
    '          اتصال مباشر\n        </a>\n',
    '          اتصال مباشر\n        </a>\n'
    f'        <a class="btn-outline" href="https://snapchat.com/t/cBWlfi67" target="_blank" rel="noopener">\n'
    f'          {SC_GHOST}\n'
    '          تابعنا على سناب شات\n        </a>\n',
    1,
    "snapchat contact button",
)

open(SRC, "w", encoding="utf-8").write(html)
print("[OK] box-based pricing applied:")
for c in changes:
    print("  -", c)
