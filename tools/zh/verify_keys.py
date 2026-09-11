# -*- coding: utf-8 -*-
"""AST-verify that combo dict keys are still the original English strings."""
import ast
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'kindlecomicconverter', 'KCC_gui.py')
src = io.open(p, encoding='utf-8').read()
tree = ast.parse(src)

EXPECTED_FORMATS = [
    "MOBI/AZW3", "EPUB", "CBZ", "Folder of images", "PDF", "PDF (200MB limit)",
    "KFX (Send to Kindle EPUB)", "MOBI + EPUB", "EPUB (200MB limit)",
    "MOBI + EPUB (200MB limit)",
]
EXPECTED_PROFILES = [
    "Kindle Oasis 9/10", "Kindle 8/10", "Kindle Oasis 8", "Kindle Voyage",
    "Kindle 1860x1920", "Kindle 1920x1920", "Kindle 1240x1860", "Kindle 1324x1986",
    "Kindle Scribe 1/2", "Kindle Scribe 3", "Kindle Scribe Colorsoft", "Kindle 11",
    "Kindle Paperwhite 11", "Kindle Paperwhite 12", "Kindle Colorsoft",
    "Kindle Paperwhite 7/10", "Kindle Paperwhite 5/6", "Kindle 4/5/7", "Kindle DX",
    "Kobo Mini/Touch", "Kobo Glo", "Kobo Glo HD", "Kobo Aura", "Kobo Aura HD",
    "Kobo Aura H2O", "Kobo Aura ONE", "Kobo Clara HD", "Kobo Libra H2O", "Kobo Forma",
    "Kindle 1", "Kindle 2", "Kindle Keyboard", "Kindle Touch", "Kobo Nia",
    "Kobo Clara 2E", "Kobo Clara Colour", "Kobo Libra 2", "Kobo Libra Colour",
    "Kobo Sage", "Kobo Elipsa", "reMarkable 1", "reMarkable 2",
    "reMarkable Paper Pro", "reMarkable Paper Pro Move", "Other",
]
EXPECTED_GUI_ORDER_FIRST = "Kindle Scribe Colorsoft"

found_formats = None
found_profiles = None
found_gui = None

for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Attribute) and t.attr == 'formats' and isinstance(node.value, ast.Dict):
                found_formats = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
            if isinstance(t, ast.Attribute) and t.attr == 'profiles' and isinstance(node.value, ast.Dict):
                found_profiles = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
            if isinstance(t, ast.Name) and t.id == 'profilesGUI' and isinstance(node.value, ast.List):
                found_gui = [e.value for e in node.value.elts
                             if isinstance(e, ast.Constant) and isinstance(e.value, str)]

print('formats keys found:', len(found_formats or []))
print('formats exact match:', found_formats == EXPECTED_FORMATS)
if found_formats != EXPECTED_FORMATS:
    print('  got     :', found_formats)
    print('  expected:', EXPECTED_FORMATS)

print('profiles keys found:', len(found_profiles or []))
print('profiles exact match:', found_profiles == EXPECTED_PROFILES)
if found_profiles != EXPECTED_PROFILES:
    missing = [k for k in EXPECTED_PROFILES if k not in (found_profiles or [])]
    extra = [k for k in (found_profiles or []) if k not in EXPECTED_PROFILES]
    print('  missing:', missing)
    print('  extra  :', extra)

print('profilesGUI first entry:', (found_gui or [None])[0])
print('profilesGUI contains Other:', 'Other' in (found_gui or []))
print('profilesGUI Separator count:', (found_gui or []).count('Separator'))
print('profilesGUI length:', len(found_gui or []))

# any Chinese left in dict keys of formats/profiles?
bad = [k for k in (found_formats or []) + (found_profiles or []) if any(ord(c) > 127 for c in k)]
print('non-ascii keys:', bad)
