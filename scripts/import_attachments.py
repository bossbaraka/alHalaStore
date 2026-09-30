#!/usr/bin/env python3
"""
ماسح المرفقات — scans every plausible location a dropped image could land in,
auto-detects which menu slot it belongs to, normalises it, and rebuilds the
standalone menu.

Usage:
    python3 scripts/import_attachments.py                  # scan + auto-match
    python3 scripts/import_attachments.py --list          # only show what was found
    python3 scripts/import_attachments.py file.jpg basbousa-02-qashta.jpg
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from upload_server import IMAGES, UPLOADS, identify, normalise, rebuild  # noqa: E402

# candidate drop-zones: the announced attachment path first, then every other
# plausible mount/workspace location, so a fix on the platform side is picked
# up automatically without touching the code again.
CANDIDATE_DIRS = [
    os.environ.get("ARENA_UPLOAD_DIR", ""),
    "/home/user/uploads",
    os.path.join(os.getcwd(), "uploads"),
    os.path.join(os.getcwd(), "inbox"),
    "/uploads", "/mnt/uploads", "/data/uploads", "/files",
    "/tmp/uploads", "/tmp/arena-uploads", "/mnt/data", "/data", "/files",
]
EXTRA_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".avif")

# filename keyword -> target slot (order matters: first match wins)
RULES = [
    (("qashta", "قشط", "cream"), "basbousa-02-qashta.jpg"),
    (("halib", "halib", "milk", "حليب", "محموس"), "basbousa-plate.jpg"),
    (("beehive", "honey", "نحل", "عسل"), "basbousa-beehive.jpg"),
    (("cheese", "pastry", "box", "معجن", "بوكس"), "basbousa-cheese.jpg"),
    (("hero", "بنر", "cover"), "hero-real.jpg"),
    (("story", "قصه", "قصتي"), "story-real.jpg"),
    (("sig", "توقيع", "signature"), "sig-real.jpg"),
    (("logo", "شعار"), "logo.png"),
]
for i in range(1, 9):
    RULES.append(((f"maamoul-0{i}", f"maamoul_0{i}"), f"maamoul-0{i}-half.jpg"))


def dirs():
    seen, out = set(), []
    for d in CANDIDATE_DIRS:
        if not d:
            continue
        d = os.path.abspath(os.path.expanduser(d))
        if d in seen or not os.path.isdir(d):
            continue
        seen.add(d)
        out.append(d)
    return out


def guess(name):
    low = name.lower()
    for keys, target in RULES:
        if any(k in low for k in keys):
            cand = os.path.join(IMAGES, target)
            if os.path.exists(cand):
                return target
    return None


def find_images():
    found = []
    for d in dirs():
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if os.path.isfile(p) and f.lower().endswith(EXTRA_EXT):
                found.append(p)
    return found


def import_one(path, target, dry=False):
    dst = os.path.join(IMAGES, target)
    if not dry:
        with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tf:
            tf.write(open(path, "rb").read())
            tmp = tf.name
        try:
            mode = normalise(tmp, dst)
        finally:
            os.unlink(tmp)
    else:
        mode = "dry-run"
    w, h = identify(dst) or (0, 0)
    kb = round(os.path.getsize(dst) / 1024)
    print(f"  ✔ {os.path.basename(path)}  →  {target}  ({w}×{h}, {kb} KB, {mode})")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="*", help="optional: <image> <target>")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if len(a.file) == 2:
        ok = import_one(a.file[0], a.file[1], a.dry_run)
        if ok and not a.dry_run:
            print("  rebuild:", rebuild())
        return 0 if ok else 1

    found = find_images()
    if not found:
        print("لم يُعثر على أي صور في:")
        for d in dirs():
            print("  -", d)
        print("(المسارات غير الموجودة تُتجاهل)")
        return 1

    print(f"وُجد {len(found)} صورة في {len(dirs())} مجلد:")
    matched = 0
    for p in found:
        target = guess(os.path.basename(p))
        size = identify(p)
        dims = f"{size[0]}×{size[1]}" if size else "?"
        if a.list:
            print(f"  · {p}  ({dims})  →  {target or 'غير محدد — استخدم: ملف هدف'}")
            continue
        if not target:
            print(f"  – {os.path.basename(p)} ({dims}) — لا يوجد تطابق، تجاوزُها")
            continue
        import_one(p, target, a.dry_run)
        matched += 1

    if not a.list and matched and not a.dry_run:
        print("  rebuild:", rebuild())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
