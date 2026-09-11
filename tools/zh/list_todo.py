# -*- coding: utf-8 -*-
"""List every remaining untranslated user-visible string (the work list)."""
import ast
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG = os.path.join(ROOT, 'kindlecomicconverter')
out = io.open(os.path.join(ROOT, 'tools', 'zh', 'todo_strings.txt'), 'w', encoding='utf-8')

HTML_TAG = re.compile(r'<[^>]+>')
# keep-in-English: identifiers, codes, URLs, formats, brand/model names
KEEP = re.compile(
    r'^(mainWindow|editorDialog|Label|PVOptions|ForceExpert|ForceColor|DefaultFormat|'
    r'DefaultUpscale|Kindle|Kobo|reMarkable|Other|Separator|MOBI|EPUB|CBZ|PDF|KFX|FOLDER|'
    r'Auto|RAR\d?|7z|kindlegen|ComicInfo|Critical|Information|Accept|Format|Volume|Series|'
    r'Writers|Pencillers|Inkers|Colorists|Writer|Penciller|Inker|RAR5|Ruby|'
    r'[A-Za-z_]+Box|[A-Za-z_]+Slider|[A-Za-z_]+Edit|[A-Za-z_]+Line|[A-Za-z_]+Button|'
    r'[A-Za-z_]+Layout|[A-Za-z_]+Widget|[A-Za-z_]+Label|[A-Za-z_]+Check|[A-Za-z_]+CheckBox)'
)
JUNK = re.compile(r'^[a-zA-Z0-9_./:\\\-]*$')


def prose(s):
    plain = HTML_TAG.sub('', s)
    plain = plain.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    if not re.search(r'[A-Za-z]{3,}', plain):
        return False
    if any(ord(c) > 127 for c in s):
        return False
    t = s.strip()
    if len(t) < 4:
        return False
    if JUNK.match(t):
        return False
    if KEEP.match(t):
        return False
    if t.startswith(':/') or t.startswith('http') or '\\' in t or '/' in t and ' ' not in t:
        return False
    return True


def collect_py(path, only_translate=False):
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    res = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == 'translate' and len(node.args) >= 2:
            a = node.args[1]
            if isinstance(a, ast.Constant) and isinstance(a.value, str) and prose(a.value):
                res.append((node.lineno, a.value))
        elif not only_translate and isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and prose(node.value):
            res.append((node.lineno, node.value))
    return sorted(set(res))


for name in ['KCC_ui.py', 'KCC_ui_editor.py']:
    items = collect_py(os.path.join(PKG, name), only_translate=True)
    out.write(f'===== {name}: {len(items)} remaining\n')
    for ln, v in items:
        out.write(f'{ln} | {v!r}\n\n')

items = collect_py(os.path.join(PKG, 'KCC_gui.py'))
out.write(f'\n===== KCC_gui.py: {len(items)} remaining\n')
for ln, v in items:
    out.write(f'{ln} | {v!r}\n\n')

items = collect_py(os.path.join(PKG, 'KCC_spread_label.py'))
out.write(f'\n===== KCC_spread_label.py: {len(items)} remaining\n')
for ln, v in items:
    out.write(f'{ln} | {v!r}\n\n')

out.close()
print('ok')
