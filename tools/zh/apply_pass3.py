# -*- coding: utf-8 -*-
"""Pass 3: AST-based replacement for multi-line implicitly-concatenated literals."""
import ast
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

EXTRA = {
    'Use the PDF/EPUB image extraction method from older KCC versions. \n\nUse if standard extraction fails for whatever reason.':
        '使用旧版 KCC 的 PDF/EPUB 图片提取方式。\n\n标准提取方式因故失败时可尝试此项。',
    "Don't quantize PNG images to 16 colors (4 bit)\n\nThis will double file size but preserve all 256 colors (8 bit).\n\nEink only has 16 shades of gray so you probably don't want this.":
        '不把 PNG 图像量化为 16 色（4 位）\n\n这会使文件体积翻倍，但保留全部 256 色（8 位）。\n\n电子墨水屏只有 16 级灰阶，通常不建议开启。',
    'Only resize images and preserve original file structure.\n\nIgnores most options besides JPEG quality, color mode, output folder.':
        '仅缩放图像并保留原始文件结构。\n\n除 JPEG 质量、彩色模式、输出文件夹外，忽略大部分选项。',
    'Render vector PDFs to device width instead of height.\n\nUseful if you plan to crop a little off the top and bottom to fill screen.':
        '按设备宽度而非高度渲染矢量 PDF。\n\n如果打算裁掉上下少量边缘以填满屏幕，此选项很有用。',
    'Replace JPG with lossy WebP and PNG with lossless WebP. This includes the JPG Quality.\n\nIgnored for Kindle EPUB/MOBI and all PDF.':
        '用有损 WebP 替换 JPG、用无损 WebP 替换 PNG（JPEG 质量设置同样生效）。\n\n对 Kindle 的 EPUB/MOBI 以及所有 PDF 无效。',
    'The JPEG quality, on a scale from 0 (worst) to 95 (best). \n\nDefault is 85 for most devices besides Kindle Scribe and Colorsoft, which are 90.\n\nHigher values are larger and higher quality, and may resolve blank page issues.':
        'JPEG 质量，范围 0（最差）到 95（最好）。\n\n除 Kindle Scribe 和 Colorsoft（默认 90）外，多数设备默认 85。\n\n数值越高体积越大、质量越好，也可能解决空白页问题。',
    'Resize cover to exact device resolution by center-cropping to aspect ratio first.\nMay crop top/bottom or left/right depending on source aspect ratio. Not implemented for Kindle Scribe.':
        '先按宽高比居中裁剪，再把封面缩放到设备精确分辨率。\n根据源图宽高比，可能裁掉上下或左右。Kindle Scribe 不支持此功能。',
    'Keep any original ComicInfo.xml files.\n\nKeeping this file may crash some readers like the Kobo native CBZ reader.':
        '保留原有的 ComicInfo.xml 文件。\n\n保留该文件可能导致某些阅读器崩溃，例如 Kobo 自带的 CBZ 阅读器。',
    '<html><head/><body><p><span style=" font-weight:600; text-decoration: underline;">Unchecked - 2 page landscape<br/></span>2 viewports for left and right pages</p><p><span style=" font-weight:600; text-decoration: underline;">Checked - 1 page landscape<br/></span>A single centered viewport for 1 page</p></body></html>':
        '<html><head/><body><p><span style=" font-weight:600; text-decoration: underline;">未勾选 - 横向双页<br/></span>左右两页各用一个视口</p><p><span style=" font-weight:600; text-decoration: underline;">勾选 - 横向单页<br/></span>单页使用一个居中视口</p></body></html>',
    'Use the PDF/EPUB image extraction method from older KCC versions. \n\nUse if standard extraction fails for whatever reason.':
        '使用旧版 KCC 的 PDF/EPUB 图片提取方式。\n\n标准提取方式因故失败时可尝试此项。',
}


def escape_literal(value):
    out = value.replace('\\', '\\\\').replace('"', '\\"')
    return out.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


def apply(path, table):
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    offsets, pos = [], 0
    for line in lines:
        offsets.append(pos)
        pos += len(line)

    edits = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if node.value not in table:
            continue
        new = table[node.value]
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        body = src[start:end]
        prefix = body[0] if body[:1] in ('u', 'U') else ''
        quote = '"'
        edits.append((start, end, prefix + quote + escape_literal(new) + quote))

    for start, end, rep in sorted(edits, key=lambda e: e[0], reverse=True):
        src = src[:start] + rep + src[end:]
    io.open(path, 'w', encoding='utf-8', newline='').write(src)
    return len(edits)


n = apply(os.path.join(ROOT, 'kindlecomicconverter', 'KCC_ui.py'), EXTRA)
print('KCC_ui.py pass3 replacements:', n)
