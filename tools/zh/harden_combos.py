# -*- coding: utf-8 -*-
"""Harden KCC_gui.py: switch combo lookups from display text to userData key."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, 'kindlecomicconverter', 'KCC_gui.py')

src = io.open(PATH, encoding='utf-8').read()
orig = src

pairs = [
    ('GUI.deviceBox.currentText()', 'GUI.deviceBox.currentData()'),
    ('GUI.formatBox.currentText()', 'GUI.formatBox.currentData()'),
]

for old, new in pairs:
    n = src.count(old)
    src = src.replace(old, new)
    print(f'{old} -> {new}: {n} occurrences')

if src == orig:
    print('NO CHANGE')
    sys.exit(0)

io.open(PATH, 'w', encoding='utf-8', newline='').write(src)
print('written', PATH)
print('remaining currentText on device/format boxes:',
      src.count('deviceBox.currentText'), src.count('formatBox.currentText'))
