#!/usr/bin/env python3
"""
مزامنة الصور من GitHub — pulls photos the user dropped into the repo and applies
them to the menu. This is the reliable delivery route: the chat attachment
pipeline never reaches the sandbox, and every public image host is firewalled
off — only GitHub is reachable.

Flow:
    1. the user uploads a photo from their phone:
       https://github.com/bossbaraka/alHalaStore/upload/main
    2. you run:  python3 scripts/sync_inbox.py
    3. every new image is matched to a menu slot, normalised, and the
       standalone menu is rebuilt.

Usage:
    python3 scripts/sync_inbox.py            # fetch + import everything new
    python3 scripts/sync_inbox.py --list     # only show what is waiting
    python3 scripts/sync_inbox.py --ref main # check another branch
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from upload_server import IMAGES, identify, normalise, rebuild  # noqa: E402
from import_attachments import guess  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".avif")


def git(*args):
    return subprocess.run(
        ["git", "-C", ROOT, *args], capture_output=True, text=True
    ).stdout.strip()


def remote_images(ref):
    """Image files present in the given remote ref."""
    out = git("ls-tree", "-r", "--name-only", f"origin/{ref}")
    return [
        p for p in out.splitlines()
        if p.lower().endswith(IMG_EXT) and not p.startswith("images/")
    ]


def known_files():
    """Image files already tracked in the working branch."""
    out = git("ls-tree", "-r", "--name-only", "HEAD")
    return {p for p in out.splitlines() if p.lower().endswith(IMG_EXT)}


def apply(path, target, dry=False):
    dst = os.path.join(IMAGES, target)
    if dry:
        print(f"  – {path} → {target} (dry-run)")
        return
    with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tf:
        tf.write(open(path, "rb").read())
        tmp = tf.name
    try:
        mode = normalise(tmp, dst)
    finally:
        os.unlink(tmp)
    w, h = identify(dst) or (0, 0)
    print(f"  ✔ {path}  →  {target}  ({w}×{h}, {round(os.path.getsize(dst)/1024)} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="main", help="remote branch to check (default: main)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    git("fetch", "origin", a.ref, "--quiet")
    new = [p for p in remote_images(a.ref) if p not in known_files()]
    if not new:
        print(f"لا توجد صور جديدة على origin/{a.ref} ✔")
        return 0

    print(f"صور جديدة بانتظار التطبيق على origin/{a.ref} ({len(new)}):")
    applied = 0
    for path in new:
        base = os.path.basename(path)
        target = guess(base) or _by_exact_name(base)
        if not target:
            print(f"  – {path} — لا يوجد تطابق تلقائي")
            continue
        # materialise the blob locally so the normaliser can read it
        os.makedirs(UPLOADS_TMP := os.path.join(ROOT, "uploads"), exist_ok=True)
        local = os.path.join(UPLOADS_TMP, base)
        with open(local, "wb") as f:
            f.write(subprocess.run(
                ["git", "-C", ROOT, "show", f"origin/{a.ref}:{path}"],
                capture_output=True).stdout)
        apply(local, target, a.dry_run)
        applied += 1

    if applied and not a.dry_run and not a.list:
        print("  rebuild:", rebuild())
        print("\nتم! حدّث الصفحة في متصفحك لتظهر الصورة الجديدة.")
    elif a.list and applied:
        print("\n(استخدم بدون --list للتطبيق)")
    return 0 if applied else 1


def _by_exact_name(base):
    stem = os.path.splitext(base)[0]
    p = os.path.join(IMAGES, stem + ".jpg")
    return stem + ".jpg" if os.path.exists(p) else None


if __name__ == "__main__":
    raise SystemExit(main())
