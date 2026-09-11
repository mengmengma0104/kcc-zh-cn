# -*- coding: utf-8 -*-
"""Apply the Chinese translation table to KCC Python sources and .ui files.

Python files: AST-driven exact span replacement of string literals, so only the
literal payload changes and all surrounding code/formatting is untouched.
UI files: ElementTree rewrite of <string> element text.
"""
import ast
import io
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from translations import UI, MESSAGES  # noqa: E402

TABLE = {}
TABLE.update(UI)
TABLE.update(MESSAGES)


def escape_literal(value):
    """Render a Python string literal the way the source files do (u"..." / "...")."""
    out = value.replace('\\', '\\\\').replace('"', '\\"')
    out = out.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    return out


def apply_python(path):
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    # byte/char offsets per line start
    offsets = []
    pos = 0
    for line in lines:
        offsets.append(pos)
        pos += len(line)

    edits = []          # (start, end, replacement)
    matched = {}        # translation -> count
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if node.value not in TABLE:
            continue
        new = TABLE[node.value]
        if new == node.value:
            continue
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        original = src[start:end]
        prefix = ''
        if original[:1] in ('u', 'U', 'f', 'F', 'r', 'R', 'b', 'B'):
            prefix = original[0]
        if 'f' in prefix.lower():
            # never rewrite f-strings: placeholders must stay live
            continue
        body = src[start + len(prefix):end]
        quote = body[:3] if body[:3] in ('"""', "'''") else body[:1]
        if quote not in ('"', "'", '"""', "'''"):
            continue
        edits.append((start, end, prefix + quote + escape_literal(new) + quote))
        matched[node.value] = matched.get(node.value, 0) + 1

    if not edits:
        return 0, []

    edits.sort(key=lambda e: e[0], reverse=True)
    out = src
    for start, end, rep in edits:
        out = out[:start] + rep + out[end:]

    io.open(path, 'w', encoding='utf-8', newline='').write(out)
    return len(edits), sorted(matched.keys())


def apply_ui(path):
    tree = ET.parse(path)
    root = tree.getroot()
    count = 0
    for string_el in root.iter('string'):
        if string_el.text and string_el.text in TABLE:
            new = TABLE[string_el.text]
            if new != string_el.text:
                string_el.text = new
                count += 1
        # <string notr="true"> must never be translated
    if count:
        tree.write(path, encoding='utf-8', xml_declaration=True)
    return count


def main():
    targets_py = [
        os.path.join(ROOT, 'kindlecomicconverter', 'KCC_gui.py'),
        os.path.join(ROOT, 'kindlecomicconverter', 'KCC_ui.py'),
        os.path.join(ROOT, 'kindlecomicconverter', 'KCC_ui_editor.py'),
        os.path.join(ROOT, 'kindlecomicconverter', 'KCC_spread_label.py'),
        os.path.join(ROOT, 'kindlecomicconverter', 'shared.py'),
    ]
    targets_ui = [
        os.path.join(ROOT, 'gui', 'KCC.ui'),
        os.path.join(ROOT, 'gui', 'MetaEditor.ui'),
    ]

    total = 0
    used = set()
    for p in targets_py:
        if not os.path.exists(p):
            print('MISSING', p)
            continue
        n, keys = apply_python(p)
        used.update(keys)
        total += n
        print(f'{os.path.basename(p):24s} replaced {n}')
    for p in targets_ui:
        if not os.path.exists(p):
            print('MISSING', p)
            continue
        n = apply_ui(p)
        total += n
        print(f'{os.path.basename(p):24s} replaced {n}')

    print('total replacements:', total)
    unused = sorted(k for k in TABLE if k not in used)
    print('table entries never matched:', len(unused))
    for k in unused[:40]:
        print('   UNUSED:', repr(k)[:110])


if __name__ == '__main__':
    main()
