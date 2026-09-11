# -*- coding: utf-8 -*-
"""Verify nothing forbidden would be committed: no kindlegen, no exe, no venv/dist/build."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SKIP_DIRS = {'venv', 'build', 'dist', '.git', '__pycache__', '.idea', '.vscode'}
DANGEROUS_NAMES = ('kindlegen',)
DANGEROUS_EXT = ('.exe', '.dll', '.pyd', '.so', '.dylib', '.dmg', '.appimage', '.zip',
                 '.rar', '.7z', '.mobi', '.epub', '.cbz', '.pdf', '.png', '.jpg',
                 '.jpeg', '.ico', '.icns', '.bmp', '.xcf')

files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT).replace('\\', '/')
        files.append((rel, os.path.getsize(full)))

files.sort()
print('files to be considered for commit: %d' % len(files))
print('total bytes: %d (%.2f MB)' % (sum(s for _, s in files), sum(s for _, s in files) / 1048576))

# Executables/libs/archives are never acceptable anywhere in the repo.
# Raster images ARE acceptable inside icons/, images/ and tools/zh/shots/ (upstream assets
# and our verification screenshots).
HARD_BAD_EXT = ('.exe', '.dll', '.pyd', '.so', '.dylib', '.dmg', '.appimage',
                '.zip', '.rar', '.7z', '.mobi', '.epub', '.cbz', '.pdf', '.msi')
IMAGE_ALLOWED_PREFIX = ('icons/', 'images/', 'tools/zh/shots/')

print('\n=== HARD-FORBIDDEN files (exe/dll/archive/ebook) ===')
bad = []
for rel, size in files:
    low = rel.lower()
    base = os.path.basename(low)
    if 'kindlegen' in base:
        bad.append((rel, size, 'KINDLEGEN'))
    elif low.endswith(HARD_BAD_EXT):
        bad.append((rel, size, 'EXEC/ARCHIVE'))
if bad:
    for rel, size, why in bad:
        print('  [%s] %s (%d bytes)' % (why, rel, size))
else:
    print('  (none)  ✅')

print('\n=== image assets by location ===')
buckets = {}
for rel, size in files:
    if rel.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.ico', '.icns', '.xcf', '.svg')):
        for p in IMAGE_ALLOWED_PREFIX + ('icons/', 'images/'):
            if rel.startswith(p):
                buckets[p] = buckets.get(p, 0) + 1
                break
        else:
            buckets['<other/%s>' % rel.split('/')[0]] = buckets.get('<other>', 0) + 1
for k, v in sorted(buckets.items()):
    print('  %-22s %d' % (k, v))

print('\n=== top-level entries ===')
seen = set()
for rel, size in files:
    top = rel.split('/')[0]
    if top not in seen:
        seen.add(top)
        print('  ', top)

print('\n=== tools/zh contents (translation toolchain) ===')
for rel, size in files:
    if rel.startswith('tools/zh/'):
        print('  %-46s %d' % (rel, size))

print('\n=== images/icons sample (allowed assets) ===')
n = 0
for rel, size in files:
    if rel.startswith('images/') or rel.startswith('icons/'):
        n += 1
print('  count:', n)

print('\nVERDICT:', 'SAFE' if not bad else 'REVIEW NEEDED - %d dangerous files' % len(bad))
