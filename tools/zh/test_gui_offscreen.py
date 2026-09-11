# -*- coding: utf-8 -*-
"""Offscreen regression test: exercise every combo entry through real code paths.

Verifies the display-text/userData split works for 100% of device and format
entries, and that the conversion option builder resolves them without KeyError.
"""
import os
import sys
import traceback

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402

from kindlecomicconverter import KCC_gui  # noqa: E402

app = KCC_gui.QApplicationMessaging(sys.argv)
window = KCC_gui.QMainWindowKCC()
gui = KCC_gui.KCCGUI(app, window)

device = gui.deviceBox
fmt = gui.formatBox

errors = []
untranslated_ok = []
device_ok = 0
format_ok = 0

# ---- devices ----
for i in range(device.count()):
    data = device.itemData(i)
    if data is None:            # separator row
        continue
    text = device.itemText(i)
    if data not in gui.profiles:
        errors.append(f'device[{i}] userData {data!r} not a profiles key')
        continue
    device.setCurrentIndex(i)
    try:
        gui.changeDevice()
        opts, cur_fmt = KCC_gui.get_options()
    except Exception as e:
        errors.append(f'device[{i}] {data!r} ({text!r}) -> {type(e).__name__}: {e}')
        traceback.print_exc()
        continue
    label = gui.profiles[data]['Label']
    if opts.profile != label:
        errors.append(f'device[{i}] {data!r}: profile {opts.profile!r} != {label!r}')
        continue
    # Brand/model names (Kindle/Kobo/reMarkable product names) stay in English by
    # design; only note entries that have no Chinese at all for the coverage report.
    if not any(ord(c) > 127 for c in text):
        untranslated_ok.append(text)
    device_ok += 1

# ---- formats ----
for i in range(fmt.count()):
    data = fmt.itemData(i)
    if data is None:
        continue
    text = fmt.itemText(i)
    if data not in gui.formats:
        errors.append(f'format[{i}] userData {data!r} not a formats key')
        continue
    fmt.setCurrentIndex(i)
    try:
        gui.changeFormat(i)
        opts, cur_fmt = KCC_gui.get_options()
    except Exception as e:
        errors.append(f'format[{i}] {data!r} ({text!r}) -> {type(e).__name__}: {e}')
        traceback.print_exc()
        continue
    expected = gui.formats[data]['format']
    if opts.format != expected:
        errors.append(f'format[{i}] {data!r}: format {opts.format!r} != {expected!r}')
        continue
    format_ok += 1

print()
print(f'devices exercised OK : {device_ok}')
print(f'formats exercised OK : {format_ok}')
print(f'errors               : {len(errors)}')
for e in errors:
    print('  ERROR:', e)
print(f'brand names kept EN  : {len(untranslated_ok)}')
for t in untranslated_ok:
    print('   EN:', t)

# ---- window title / translation spot checks ----
print()
print('window title :', window.windowTitle())
print('convert btn  :', gui.convertButton.text())
print('device text  :', device.itemText(0))
print('format text  :', fmt.itemText(0))
print('crop label   :', gui.croppingPowerLabel.text())
print('manga check  :', gui.mangaBox.text())

sys.exit(1 if errors else 0)
