# -*- coding: utf-8 -*-
"""Test MOBI conversion (kindlegen) and full processing pipeline."""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, 'testdata')
OUT = os.path.join(WORK, 'out2')
CBZ = os.path.join(WORK, 'test.cbz')
os.makedirs(OUT, exist_ok=True)

PY = os.path.join(ROOT, 'venv', 'Scripts', 'python.exe')
C2E = os.path.join(ROOT, 'kcc-c2e.py')

# locate kindlegen and put it on PATH for the child process
KG_DIR = r'C:\Users\ASUS\Downloads\Kindle Comic Converter（2022-5-17）'
env = dict(os.environ)
env['PATH'] = KG_DIR + os.pathsep + env['PATH']
kg = os.path.join(KG_DIR, 'kindlegen.exe')
print('kindlegen exists:', os.path.exists(kg), kg)

print('\n--- test 1: MOBI (kindlegen) ---')
cmd = [PY, C2E, '-p', 'KPW5', '-f', 'MOBI', '-o', OUT, CBZ]
p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                   cwd=ROOT, timeout=900, env=env)
print('exit:', p.returncode)
print('stdout tail:', p.stdout[-1200:] if p.stdout else '')
print('stderr tail:', p.stderr[-1000:] if p.stderr else '')

print('\n--- test 2: full processing pipeline (crop/quantize/resize) ---')
cmd = [PY, C2E, '-p', 'KPW5', '-f', 'CBZ', '-m', '-c', '2', '-o', OUT, CBZ]
p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                   cwd=ROOT, timeout=900, env=env)
print('exit:', p.returncode)
print('stdout tail:', p.stdout[-1200:] if p.stdout else '')
print('stderr tail:', p.stderr[-1200:] if p.stderr else '')

print('\n--- test 3: KEPUB (Kobo profile) ---')
cmd = [PY, C2E, '-p', 'KoLC', '-f', 'EPUB', '-o', OUT, CBZ]
p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                   cwd=ROOT, timeout=900, env=env)
print('exit:', p.returncode)
print('stdout tail:', p.stdout[-800:] if p.stdout else '')

print('\noutput dir contents:')
for f in sorted(os.listdir(OUT)):
    full = os.path.join(OUT, f)
    print('  ', f, os.path.getsize(full), 'bytes')
