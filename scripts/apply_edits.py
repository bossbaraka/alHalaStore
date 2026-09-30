#!/usr/bin/env python3
"""Apply menu content updates to index.html (idempotent, assertion-guarded)."""
import re
import urllib.parse

SRC = "index.html"
html = open(SRC, encoding="utf-8").read()
changes = []


def rep(old, new, count=None, label=""):
    global html
    n = html.count(old)
    if n == 0:
        raise SystemExit(f"FAIL [{label}]: pattern not found -> {old[:90]!r}")
    if count is not None and n != count:
        raise SystemExit(f"FAIL [{label}]: expected {count} occurrences, found {n}")
    html = html.replace(old, new)
    changes.append(f"{label} ({n}x)")


# ------------------------------------------------------------------
# 1) Professional WhatsApp order message (URL-encoded)
# ------------------------------------------------------------------
MSG = (
    "السلام عليكم 🌸\n"
    "أرغب في طلب أصناف من مخبز «قصة الحلى — Sweet Story»:\n\n"
    "• الصنف / الأصناف:\n"
    "• الكمية (ربع كيلو / نصف كيلو / كيلو / القالب):\n"
    "• وقت الاستلام أو التوصيل:\n"
    "• العنوان أو ملاحظات أخرى:\n\n"
    "برجاء تأكيد التوفر والسعر الإجمالي ووسيلة الدفع. جزاكم الله خيراً 🤍"
)
MSG_ENC = urllib.parse.quote(MSG, safe="")
html, n = re.subn(r"(wa\.me/966540424081\?text=)[^\"]+", lambda m: m.group(1) + MSG_ENC, html)
if n != 3:
    raise SystemExit(f"FAIL [whatsapp]: expected 3 links, found {n}")
changes.append(f"whatsapp order message ({n}x)")

# ------------------------------------------------------------------
# 2) Address  ->  الخرج حي النهضة شارع الملك سلمان
# ------------------------------------------------------------------
MAPS = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(
    "الخرج حي النهضة شارع الملك سلمان"
)

rep(
    '<span class="ir-value">حيّ الطحين، شارع الخبّازين</span>\n'
    '          <span class="ir-sub">قصة الحلى — Sweet Story</span>',
    f'<a class="ir-value" href="{MAPS}" target="_blank" rel="noopener" '
    'style="text-decoration:underline">الخرج — حي النهضة، شارع الملك سلمان</a>\n'
    '          <span class="ir-sub">الخرج، المملكة العربية السعودية · اضغط لعرض الخريطة</span>',
    1,
    "address (contact)",
)

rep(
    '<li><svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg><span>حيّ الطحين، شارع الخبّازين</span></li>',
    '<li><svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg><span>الخرج — حي النهضة، شارع الملك سلمان</span></li>',
    1,
    "address (footer)",
)

# ------------------------------------------------------------------
# 3) Remove e-mail everywhere it is displayed
# ------------------------------------------------------------------
rep(
    '        <div class="info-row">\n'
    '          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>\n'
    '          <span class="ir-label">البريد الإلكتروني</span>\n'
    '          <span class="ir-value" style="direction:ltr">hello@sweetstory.sa</span>\n'
    '          <span class="ir-sub">نرد خلال يوم عمل</span>\n'
    '        </div>\n',
    "",
    1,
    "remove e-mail (contact)",
)

rep(
    '          <li><svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg><span style="direction:ltr">hello@sweetstory.sa</span></li>\n',
    "",
    1,
    "remove e-mail (footer)",
)

# ------------------------------------------------------------------
# 4) Section name  ->  البسبوسة والمعجنات
# ------------------------------------------------------------------
rep(
    '<a href="#basbousa" data-nav="basbousa">البسبوسة</a>',
    '<a href="#basbousa" data-nav="basbousa">البسبوسة والمعجنات</a>',
    4,
    "nav links (nav/mobile/footer/quickbar)",
)
rep('<span class="cc-name">البسبوسة</span>',
    '<span class="cc-name">البسبوسة والمعجنات</span>', 1, "home card title")
rep('<h2 class="sec-title">البسبوسة</h2>',
    '<h2 class="sec-title">البسبوسة والمعجنات</h2>', 1, "section title")
rep('alt="البسبوسة"', 'alt="البسبوسة والمعجنات"', 1, "home card alt")
rep('<span class="cc-latin">Basbousa Collection — 02</span>',
    '<span class="cc-latin">Basbousa &amp; Pastries — 02</span>', 1, "home card latin")
rep('<span class="latin-label">BASBOUSA COLLECTION — 02</span>',
    '<span class="latin-label">BASBOUSA &amp; PASTRIES — 02</span>', 1, "section latin")
rep('<p class="sec-sub">قوام غني، تفاصيل ناعمة، وطعم يُحضّر بحب.</p>',
    '<p class="sec-sub">قوام غني، تفاصيل ناعمة، ومعجنات محشوّة تُخبز حتى الذهبية.</p>',
    1, "section subtitle")
rep('<span class="bp-label">تُباع البسبوسة بالقالب — جاهزة ومغلّفة</span>',
    '<span class="bp-label">تُباع البسبوسة بالقالب والمعجنات بالبوكس — جاهزة ومغلّفة</span>',
    1, "basbousa pricing label")

# ------------------------------------------------------------------
# 5) Remove the site copyright line from the footer
# ------------------------------------------------------------------
rep(
    '      <p>© قصة الحلى — Sweet Story · معمول وبسبوسة</p>\n',
    "",
    1,
    "remove copyright",
)
rep(
    ".footer-bottom{margin-top:var(--s8);padding-top:var(--s3);border-top:var(--line-soft);display:flex;align-items:center;justify-content:space-between;gap:var(--s2);flex-wrap:wrap}",
    ".footer-bottom{margin-top:var(--s8);padding-top:var(--s3);border-top:var(--line-soft);display:flex;align-items:center;justify-content:center;gap:var(--s2);flex-wrap:wrap}",
    1,
    "center footer-bottom",
)

# ------------------------------------------------------------------
# 6) Maamoul cards: name only (drop prices)
# ------------------------------------------------------------------
before = html.count('<p class="p-price"><b>60 ر.س</b> للكيلو</p>')
html = html.replace('<p class="p-price"><b>60 ر.س</b> للكيلو</p>', "")
changes.append(f"maamoul card prices removed ({before}x)")
if before != 8:
    raise SystemExit(f"FAIL [maamoul prices]: expected 8, found {before}")

# ------------------------------------------------------------------
# 7) Nicer social icons + Snapchat
# ------------------------------------------------------------------
OLD_SOCIAL_CSS = """.f-social{display:flex;gap:var(--s2);margin-top:var(--s4)}
.f-social a{width:40px;height:40px;border:1px solid rgba(165,139,103,.4);border-radius:50%;display:flex;align-items:center;justify-content:center;transition:border-color .3s,background .3s}
.f-social a svg{width:16px;height:16px;stroke:var(--toasted);transition:stroke .3s}
.f-social a:hover{background:var(--soft-flour);border-color:var(--warm-wheat)}
.f-social a:hover svg{stroke:var(--deep-dough)}"""

NEW_SOCIAL_CSS = """.f-social-label{font-size:11px;letter-spacing:.22em;color:var(--warm-wheat);font-family:var(--serif-en);text-transform:uppercase;direction:ltr}
.f-social{display:flex;gap:14px;margin-top:var(--s2)}
.f-social a{
  width:46px;height:46px;border:1px solid rgba(165,139,103,.42);border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  color:var(--toasted);background:var(--flour-white);
  box-shadow:0 8px 18px -14px rgba(70,61,51,.55);
  transition:color .35s ease,background .35s ease,border-color .35s ease,transform .45s var(--ease),box-shadow .45s var(--ease);
}
.f-social a svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;transition:transform .45s var(--ease)}
.f-social a:hover{transform:translateY(-4px);box-shadow:0 16px 26px -16px rgba(70,61,51,.65)}
.f-social a:hover svg{transform:scale(1.08)}
.f-social a:focus-visible{outline:2px solid var(--warm-wheat);outline-offset:3px}
.f-social a[data-net="whatsapp"]:hover{color:#128C4B;border-color:rgba(18,140,75,.55);background:rgba(18,140,75,.08)}
.f-social a[data-net="instagram"]:hover{color:#A1308B;border-color:rgba(161,48,139,.5);background:rgba(161,48,139,.07)}
.f-social a[data-net="snapchat"]:hover{color:#8C6D1F;border-color:rgba(190,150,40,.6);background:rgba(255,244,204,.85)}"""

rep(OLD_SOCIAL_CSS, NEW_SOCIAL_CSS, 1, "social icon styles")

WA_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3z"/>'
           '<path d="M8.8 8.6c.3-.8.7-.8 1-.8l.7.1c.2 0 .4 0 .6.5.2.5.7 1.7.8 1.8.1.2.1.4 0 .6-.1.2-.2.4-.4.6-.2.2-.4.5-.6.6-.2.2-.4.4-.2.8.2.4.9 1.5 2 2.4 1.3 1.2 2.2 1.5 2.6 1.6.3.1.5.1.7-.1.2-.2.8-.9.9-1.2.2-.3.4-.3.6-.2l1.7.8"/></svg>')
IG_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5.5"/>'
           '<circle cx="12" cy="12" r="4"/>'
           '<circle cx="17.3" cy="6.7" r="1.05" fill="currentColor" stroke="none"/></svg>')
SC_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.7c-3.2 0-5.5 2.4-5.5 5.6 0 .5 0 1 .1 1.4-.4.2-.9.2-1.4 0-.6-.2-1.1.3-1 1 '
           '.1.6.6 1.1 1.2 1.4.4.2.6.5.5.9-.2.7-1 1.3-1.8 1.6-.5.2-.6.8-.2 1.1.9.7 2 1.1 3.1 1.3.1.6.3 1 .7 1.5.4.4 1 .3 '
           '1.3-.2.3-.4.8-.4 1.1 0 .3.3.5.6 1 .2.5 1 .4 1.2-.1.2-.4.3-.7.6-1 .3-.4.8-.4 1.1 0 .3.4.4.8.6 1 .2.5 1 .4 1.2-.1.1-.5.3-.9.7-1.5 '
           '1.1-.2 2.2-.6 3.1-1.3.4-.3.3-.9-.2-1.1-.8-.3-1.6-.9-1.8-1.6-.1-.4.1-.7.5-.9.6-.3 1.1-.8 1.2-1.4.1-.7-.4-1.2-1-1-.5.2-1 .2-1.4 0 '
           '.1-.4.1-.9.1-1.4 0-3.2-2.3-5.6-5.5-5.6Z"/></svg>')

rep(
    '        <div class="f-social">',
    '        <span class="f-social-label">Follow us</span>\n        <div class="f-social">',
    1,
    "social label",
)

# rebuild the two existing anchors with data-net + improved icons
rep(
    re.search(r'          <a href="https://wa\.me/966540424081\?text=[^"]+" target="_blank" rel="noopener" aria-label="واتساب">.*?</a>\n', html, re.S).group(0),
    f'          <a href="https://wa.me/966540424081?text={MSG_ENC}" target="_blank" rel="noopener" aria-label="واتساب" title="واتساب" data-net="whatsapp">{WA_ICON}</a>\n',
    1,
    "whatsapp icon",
)
rep(
    '          <a href="https://www.instagram.com/swet_story?stkn=MXY2NTFkODBmaThpaA==" target="_blank" rel="noopener" aria-label="انستغرام"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.4"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="0.8" fill="currentColor" stroke="none"/></svg></a>\n',
    '          <a href="https://www.instagram.com/swet_story?stkn=MXY2NTFkODBmaThpaA==" target="_blank" rel="noopener" aria-label="انستغرام" title="انستغرام" data-net="instagram">' + IG_ICON + '</a>\n'
    '          <a href="https://snapchat.com/t/cBWlfi67" target="_blank" rel="noopener" aria-label="سناب شات" title="سناب شات" data-net="snapchat">' + SC_ICON + '</a>\n',
    1,
    "instagram + snapchat icons",
)

open(SRC, "w", encoding="utf-8").write(html)
print("[OK] index.html updated:")
for c in changes:
    print("  -", c)
