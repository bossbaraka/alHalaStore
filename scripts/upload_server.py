#!/usr/bin/env python3
"""
رفع الصور مباشرة إلى المشروع — Direct image importer for the Sweet Story menu.

لماذا هذا السكربت؟
---------------
مجلد المرفقات (/home/user/uploads/) لا يصل إلى صندوق العمل إطلاقاً، لذلك فشلت
كل محاولات الإرفاق في المحادثة. هذا الخادم يتجاوز تلك المشكلة تماماً: افتح
صفحة الرفع من متصفحك، اسحب الصورة وأفلتها، فتُحفظ داخل المشروع فوراً،
ويتم ضبط مقاسها/nسبة أبعادها لتطابق مكانها في المنيو، ثم يُعاد بناء ملف
القائمة المدمجة sweet-story-menu.html تلقائياً.

الاستخدام:
    python3 scripts/upload_server.py [--port 8001]

يعتمد على المكتبة القياسية فقط + ImageMagick (اختياري).
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
import mimetypes
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(ROOT, "images")
UPLOADS = os.path.join(ROOT, "uploads")
MAX_EDGE = 1400  # أقصى ضلع للتجهيز ((show retina) بكسل)

# الملفات القابلة للاستبدال + وصفها الظاهر للمستخدم
TARGETS = [
    ("basbousa-02-qashta.jpg", "بسبوسة بالقشطة"),
    ("basbousa-plate.jpg", "بسبوسة الحليب المحموس"),
    ("basbousa-beehive.jpg", "بسبوسة خلية النحل"),
    ("basbousa-cheese.jpg", "المعجنات البوكس"),
    ("maamoul-01-halib.jpg", "معمول بالحليب المحموس"),
    ("maamoul-02-qashta.jpg", "معمول بالقشطة والتمر"),
    ("maamoul-03-shovan.jpg", "معمول الشوفان"),
    ("maamoul-06-zaatar.jpg", "معمول مربعات الزعتر"),
    ("hero-real.jpg", "صورة الواجهة الرئيسية (Hero)"),
    ("sig-real.jpg", "صورة التوقيع"),
    ("story-real.jpg", "صورة قصتنا"),
    ("logo.png", "الشعار (Logo)"),
]
TARGETS = [(f, label) for f, label in TARGETS if os.path.exists(os.path.join(IMAGES, f))]
ALLOWED = {f for f, _ in TARGETS}


# ---------------------------------------------------------------- helpers
def have(tool):
    return shutil.which(tool) is not None


def identify(path):
    """Return (width, height) or None."""
    if not have("identify"):
        return None
    out = subprocess.run(
        ["identify", "-format", "%w %h", path], capture_output=True, text=True
    )
    m = re.search(r"(\d+)\s+(\d+)", out.stdout)
    return (int(m.group(1)), int(m.group(2))) if m else None


def normalise(src_path, dst_path):
    """Crop (centre) to the target's aspect ratio, then shrink to fit."""
    sw, sh = identify(src_path) or (0, 0)
    dw, dh = identify(dst_path) or (0, 0)

    if not (have("convert") and sw and sh):
        shutil.copyfile(src_path, dst_path)  # fallback: plain copy
        return "copy"

    cmd = ["convert", src_path]
    if dw and dh and sw and sh:
        src_ar, dst_ar = sw / sh, dw / dh
        if abs(src_ar - dst_ar) > 0.01:  # only crop when ratios differ
            if src_ar > dst_ar:  # source too wide -> trim sides
                cw = int(round(sh * dst_ar))
                cmd += ["-crop", f"{cw}x{sh}+0+0", "+repage"]
            else:  # source too tall -> trim top/bottom
                ch = int(round(sw / dst_ar))
                cmd += ["-crop", f"{sw}x{ch}+0+0", "+repage"]
    cmd += [
        "-resize", f"{MAX_EDGE}x{MAX_EDGE}>",
        "-strip", "-interlace", "Plane", "-sampling-factor", "4:2:0",
        "-quality", "84", dst_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return "ok" if res.returncode == 0 else "copy-failed"


def rebuild():
    script = os.path.join(ROOT, "scripts", "inline_images.py")
    if not os.path.exists(script):
        return "skipped"
    res = subprocess.run(
        ["python3", script], cwd=ROOT, capture_output=True, text=True
    )
    return "ok" if res.returncode == 0 else "failed"


def state():
    out = []
    for name, label in TARGETS:
        path = os.path.join(IMAGES, name)
        dims = identify(path) or (0, 0)
        out.append(
            {
                "name": name,
                "label": label,
                "w": dims[0],
                "h": dims[1],
                "kb": round(os.path.getsize(path) / 1024) if os.path.exists(path) else 0,
            }
        )
    return out


# ---------------------------------------------------------------- page
PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>رفع صور المنيو — قصة الحلى</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#F5F1E8;color:#463D33;padding:32px 20px}
.wrap{max-width:940px;margin-inline:auto}
h1{font-size:26px;margin-bottom:6px}
p.sub{color:#6F6252;font-size:14px;margin-bottom:22px;line-height:1.9}
.card{background:#EDE7DA;border:1px solid rgba(165,139,103,.34);border-radius:6px;padding:22px;margin-bottom:20px}
label{display:block;font-size:13px;color:#A58B67;margin-bottom:8px}
select{width:100%;padding:12px;border-radius:4px;border:1px solid rgba(165,139,103,.4);
 background:#F5F1E8;color:#463D33;font-size:15px;font-family:inherit}
#drop{margin-top:14px;border:2px dashed rgba(165,139,103,.55);border-radius:6px;background:#F5F1E8;
 padding:34px 18px;text-align:center;cursor:pointer;transition:.2s}
#drop.over{background:#E3D8C6;border-color:#A58B67}
#drop .big{font-size:17px;margin-bottom:6px}
#drop .small{font-size:12.5px;color:#6F6252}
button{margin-top:14px;width:100%;padding:14px;border:0;border-radius:4px;background:#463D33;
 color:#F5F1E8;font-size:15px;font-family:inherit;cursor:pointer;transition:.2s}
button:hover{background:#6F6252}
button:disabled{opacity:.45;cursor:not-allowed}
#log{margin-top:16px;font-size:13.5px;line-height:2;white-space:pre-wrap}
.ok{color:#128C4B}.err{color:#B3261E}.info{color:#6F6252}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}
.card-i{background:#F5F1E8;border:1px solid rgba(165,139,103,.3);border-radius:5px;padding:10px;text-align:center}
.card-i img{width:100%;height:100px;object-fit:cover;border-radius:3px;background:#E3D8C6}
.card-i .n{font-size:12.5px;font-weight:600;margin-top:8px}
.card-i .d{font-size:11px;color:#A58B67;direction:ltr}
.row{display:flex;gap:16px;flex-wrap:wrap}
</style></head><body><div class="wrap">
<h1>رفع صور المنيو</h1>
<p class="sub">اسحب الصورة وأفلتها هنا (أو اضغط للاختيار من جهازك) — تُحفظ في المشروع فوراً،
ويتم ضبط أبعادها تلقائياً لتطابق مكانها، ثم يُعاد بناء ملف القائمة المدمجة.</p>

<div class="card">
  <label>الصورة ستُستبدل في:</label>
  <select id="target"></select>
  <div id="drop"><div class="big">📥 اسحب الصورة هنا أو اضغط للاختيار</div>
  <div class="small">JPG · PNG · WEBP — يُفضّل صور عمودية عالية الجودة</div></div>
  <input type="file" id="file" accept="image/*" hidden>
  <button id="go" disabled>رفع واستبدال</button>
  <div id="log"></div>
</div>

<div class="card"><label>الصور الحالية في المشروع:</label><div class="grid" id="grid"></div></div>
</div>
<script>
const B=location.pathname.replace(/\/upload\/?$/,'');
const $=s=>document.querySelector(s);
let picked=null;
$('#drop').onclick=()=>$('#file').click();
$('#file').onchange=e=>{picked=e.target.files[0]||null;if(picked)$('#drop .big').textContent='🖼 '+picked.name;};
['dragenter','dragover'].forEach(ev=>$('#drop').addEventListener(ev,e=>{e.preventDefault();$('#drop').classList.add('over')}));
['dragleave','drop'].forEach(ev=>$('#drop').addEventListener(ev,e=>{e.preventDefault();$('#drop').classList.remove('over')}));
$('#drop').addEventListener('drop',e=>{picked=e.dataTransfer.files[0]||null;if(picked){$('#drop .big').textContent='🖼 '+picked.name;$('#go').disabled=false}});
$('#go').onclick=async()=>{
  if(!picked)return;
  const btn=$('#go');btn.disabled=true;btn.textContent='جارٍ الرفع…';
  const rd=new FileReader();
  rd.onload=async()=>{
    $('#log').innerHTML='<span class="info">جارٍ الرفع والمعالجة…</span>';
    try{
      const r=await fetch(B+'/api/upload',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({target:$('#target').value,name:picked.name,dataUrl:rd.result})});
      const j=await r.json();
      $('#log').innerHTML = j.ok
        ? '<span class="ok">✔ تم بنجاح: '+j.target+' ('+j.w+'×'+j.h+', '+j.kb+' ك.ب) — '+(j.rebuilt==='ok'?'وأُعيد بناء القائمة المدمجة':'')+'</span>'
        : '<span class="err">✖ '+j.error+'</span>';
      load();btn.textContent='رفع واستبدال';btn.disabled=!picked;
      if(picked){btn.disabled=false}
    }catch(err){$('#log').innerHTML='<span class="err">✖ '+err+'</span>';btn.disabled=false}
  };
  rd.readAsDataURL(picked);
};
async function load(){
  const s=await (await fetch(B+'/api/state')).json();
  $('#target').innerHTML=s.map(i=>'<option value="'+i.name+'">'+i.label+' — '+i.name+'</option>').join('');
  $('#grid').innerHTML=s.map(i=>'<div class="card-i"><img src="'+B+'/img/'+i.name+'?t='+Date.now()+'">'+
    '<div class="n">'+i.label+'</div><div class="d">'+i.w+'×'+i.h+' · '+i.kb+'KB</div></div>').join('');
}
load();
</script></body></html>"""


# ---------------------------------------------------------------- handler
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    static_root = None  # when set, repo files are served too (menu + uploader on one port)

    def log_message(self, fmt, *args):  # quiet
        pass

    def _serve_static(self, path):
        rel = path.lstrip("/") or "index.html"
        fp = os.path.normpath(os.path.join(self.static_root, rel))
        if not fp.startswith(os.path.abspath(self.static_root)) or not os.path.isfile(fp):
            return self._send(404, json.dumps({"error": "not found"}))
        ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
        with open(fp, "rb") as f:
            return self._send(200, f.read(), ctype)

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.unquote(self.path.split("?")[0])
        # the uploader page: at /upload when the menu is served from the same port
        if path.rstrip("/") in ("/upload", "/uploader", "/upload.html") or (
            self.static_root is None and path in ("/", "/index.html")
        ):
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if path == "/api/state":
            return self._send(200, json.dumps(state(), ensure_ascii=False))
        if path.startswith("/img/"):
            name = os.path.basename(path[5:])
            fp = os.path.join(IMAGES, name)
            if not os.path.exists(fp):
                return self._send(404, json.dumps({"error": "not found"}))
            with open(fp, "rb") as f:
                return self._send(200, f.read(), "image/jpeg")
        if self.static_root:
            return self._serve_static(path)
        self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path.split("?")[0] != "/api/upload":
            return self._send(404, json.dumps({"error": "not found"}))
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or "{}")
        except Exception as e:
            return self._send(400, json.dumps({"ok": False, "error": f"طلب غير صالح: {e}"}))

        target = os.path.basename(str(data.get("target", "")))
        if target not in ALLOWED:
            return self._send(400, json.dumps({"ok": False, "error": "هدف غير مسموح"}))

        data_url = str(data.get("dataUrl", ""))
        if ";base64," not in data_url:
            return self._send(400, json.dumps({"ok": False, "error": "ملف غير صالح"}))
        try:
            blob = base64.b64decode(data_url.split(";base64,", 1)[1])
        except Exception as e:
            return self._send(400, json.dumps({"ok": False, "error": f"فشل فك الترميز: {e}"}))

        os.makedirs(UPLOADS, exist_ok=True)
        os.makedirs(IMAGES, exist_ok=True)

        # 1) keep the original untouched in uploads/
        orig = os.path.basename(str(data.get("name") or "upload")) or "upload"
        orig = re.sub(r"[^A-Za-z0-9._؀-ۿ -]", "_", orig)
        if not os.path.splitext(orig)[1]:
            orig += ".jpg"
        with open(os.path.join(UPLOADS, orig), "wb") as f:
            f.write(blob)

        # 2) process into the target slot
        dst = os.path.join(IMAGES, target)
        with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tf:
            tf.write(blob)
            src = tf.name
        try:
            normalise(src, dst)
        finally:
            os.unlink(src)

        rebuilt = rebuild()
        dims = identify(dst) or (0, 0)
        return self._send(
            200,
            json.dumps(
                {
                    "ok": True,
                    "target": target,
                    "w": dims[0],
                    "h": dims[1],
                    "kb": round(os.path.getsize(dst) / 1024),
                    "original": orig,
                    "rebuilt": rebuilt,
                },
                ensure_ascii=False,
            ),
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8001)
    ap.add_argument("--open", action="store_true", help="open in a local browser")
    ap.add_argument("--static", metavar="DIR", help="also serve DIR (the menu) from this port")
    a = ap.parse_args()
    Handler.static_root = os.path.abspath(a.static) if a.static else None
    srv = ThreadingHTTPServer(("0.0.0.0", a.port), Handler)
    url = f"http://localhost:{a.port}/"
    print(f"[upload server] listening on 0.0.0.0:{a.port}  ->  {url}")
    print(f"[upload server] {len(TARGETS)} replaceable image slots")
    if a.open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
