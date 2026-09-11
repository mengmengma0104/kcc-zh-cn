# -*- coding: utf-8 -*-
"""Exhaustively dump every visible string from the live widget tree.

This is the authoritative coverage check: instead of eyeballing screenshots,
walk all widgets/dialogs and report any remaining English UI text.
"""
import io
import os
import re
import sys

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from PySide6.QtWidgets import (QApplication, QWidget, QComboBox, QLabel, QAbstractButton,
                               QGroupBox, QLineEdit, QSpinBox, QDoubleSpinBox, QSlider,
                               QProgressBar, QTabWidget, QTableView, QListView, QTreeView)
from kindlecomicconverter import KCC_gui  # noqa: E402

HTML = re.compile(r'<[^>]+>')
# strings that legitimately stay English
KEEP = re.compile(
    r'^(Kindle|Kobo|reMarkable|MOBI|EPUB|CBZ|PDF|KFX|FOLDER|Auto|7z|ComicInfo|'
    r'RAR\d?|JPEG|PNG|WebP|QQ|Ko-fi|Humble Bundle|Wiki|YouTube|Discord|README|FAQ)'
)

app = KCC_gui.QApplicationMessaging(sys.argv)
window = KCC_gui.QMainWindowKCC()
gui = KCC_gui.KCCGUI(app, window)
app.processEvents()


def texts_of(w):
    out = []
    if isinstance(w, QComboBox):
        out.append(('currentText', w.currentText()))
        out.append(('currentData', str(w.currentData())))
        for i in range(w.count()):
            out.append((f'item[{i}]', w.itemText(i)))
    if isinstance(w, QAbstractButton):
        out.append(('text', w.text()))
        out.append(('toolTip', w.toolTip()))
    if isinstance(w, (QLabel, QGroupBox)):
        out.append(('text', w.text()))
        out.append(('toolTip', w.toolTip()))
    if isinstance(w, (QLineEdit,)):
        out.append(('placeholder', w.placeholderText()))
        out.append(('text', w.text()))
        out.append(('toolTip', w.toolTip()))
    if isinstance(w, (QSpinBox, QDoubleSpinBox)):
        out.append(('prefix', w.prefix()))
        out.append(('suffix', w.suffix()))
        out.append(('specialValueText', w.specialValueText()))
    if isinstance(w, QTabWidget):
        for i in range(w.count()):
            out.append((f'tab[{i}]', w.tabText(i)))
    return out


rows = []
widgets = window.findChildren(QWidget)
for w in widgets:
    for kind, val in texts_of(w):
        if not val:
            continue
        rows.append((w.objectName(), w.__class__.__name__, kind, val))

# also probe the metadata editor dialog class
lines = []


def is_english_prose(v):
    plain = HTML.sub('', v).replace('&quot;', '"').replace('&amp;', '&')
    if not re.search(r'[A-Za-z]{3,}', plain):
        return False
    if any(ord(c) > 127 for c in v):
        return False
    t = plain.strip()
    if len(t) < 4:
        return False
    if KEEP.match(v.strip()):
        return False
    if re.match(r'^[A-Za-z0-9_./:\\\-+*()\[\]{}%<>=!?,\' ]+$', t) and ' ' not in t:
        return False
    return ' ' in t   # require a space -> likely a sentence/label phrase


out = io.open(os.path.join(ROOT, 'tools', 'zh', 'widget_dump.txt'), 'w', encoding='utf-8')
out.write('=== ALL visible strings in main window widget tree ===\n')
seen = set()
for obj, cls, kind, val in rows:
    key = (obj, kind, val)
    if key in seen:
        continue
    seen.add(key)
    marker = 'EN?' if is_english_prose(val) else '    '
    out.write(f'{marker} {obj:28s} {cls:18s} {kind:16s} {val[:110]!r}\n')

out.write('\n\n=== remaining English-prose candidates ===\n')
n = 0
for obj, cls, kind, val in rows:
    if is_english_prose(val):
        out.write(f'{obj:28s} {cls:18s} {kind:16s} {val[:160]!r}\n')
        n += 1
out.write(f'\ntotal candidates: {n}\n')
out.close()
print('total visible strings:', len(seen))
print('english-prose candidates:', n)
