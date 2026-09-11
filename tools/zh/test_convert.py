# -*- coding: utf-8 -*-
"""End-to-end conversion test: generate manga-like pages, convert to CBZ/PDF/MOBI."""
import io
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, 'testdata')
SRC = os.path.join(WORK, 'pages')
OUT = os.path.join(WORK, 'out')

from PIL import Image, ImageDraw  # noqa: E402

os.makedirs(SRC, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# 6 pages, manga-ish: white bg, black border, some gray art
if not os.path.exists(os.path.join(SRC, 'page_001.png')):
    for i in range(1, 7):
        im = Image.new('L', (1200, 1800), 255)
        d = ImageDraw.Draw(im)
        d.rectangle([60, 60, 1140, 1740], outline=0, width=6)
        d.rectangle([140, 200, 1060, 700], outline=0, width=3)
        d.ellipse([300, 850, 900, 1450], outline=0, width=4)
        d.text((150, 120), 'PAGE %d' % i, fill=0)
        d.rectangle([140, 1500, 1060, 1650], fill=180)
        im.save(os.path.join(SRC, 'page_%03d.png' % i))

CBZ = os.path.join(WORK, 'test.cbz')
with zipfile.ZipFile(CBZ, 'w', zipfile.ZIP_DEFLATED) as z:
    for i in range(1, 7):
        z.write(os.path.join(SRC, 'page_%03d.png' % i), 'page_%03d.png' % i)
print('input CBZ:', CBZ, os.path.getsize(CBZ), 'bytes')

PY = os.path.join(ROOT, 'venv', 'Scripts', 'python.exe')
C2E = os.path.join(ROOT, 'kcc-c2e.py')

results = []
for fmt in ['CBZ', 'PDF', 'EPUB']:
    cmd = [PY, C2E, '-p', 'KPW5', '-f', fmt, '--noprocessing', '-o', OUT, CBZ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       cwd=ROOT, timeout=600)
    print(f'\n===== {fmt} exit={p.returncode} =====')
    if p.stdout:
        print('STDOUT (tail):', p.stdout[-800:])
    if p.stderr:
        print('STDERR (tail):', p.stderr[-1500:])
    results.append((fmt, p.returncode))

print('\n=== summary ===')
for fmt, rc in results:
    print(f'{fmt}: {"OK" if rc == 0 else "FAIL(" + str(rc) + ")"}')

print('\noutput dir contents:')
for f in sorted(os.listdir(OUT)):
    full = os.path.join(OUT, f)
    print('  ', f, os.path.getsize(full), 'bytes')
