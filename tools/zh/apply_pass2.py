# -*- coding: utf-8 -*-
"""Apply the second pass: remaining multi-line tooltips and leftover fragments."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG = os.path.join(ROOT, 'kindlecomicconverter')

# exact source strings -> Chinese. Keys must match the file content verbatim.
UI_EXTRA = {
    'Use the PDF/EPUB image extraction method from older KCC versions. \\n\\nUse if standard extraction fails for whatever reason.':
        '使用旧版 KCC 的 PDF/EPUB 图片提取方式。\\n\\n标准提取方式因故失败时可尝试此项。',
    'Do not rotate double page spreads in spread splitter option.':
        '在跨页拆分选项中不旋转跨页图。',
    "Delete input file(s) or directory. It's not recoverable!":
        '删除输入文件或目录。此操作不可恢复！',
    "Don't quantize PNG images to 16 colors (4 bit)\\n\\nThis will double file size but preserve all 256 colors (8 bit).\\n\\nEink only has 16 shades of gray so you probably don't want this.":
        '不把 PNG 图像量化为 16 色（4 位）\\n\\n这会使文件体积翻倍，但保留全部 256 色（8 位）。\\n\\n电子墨水屏只有 16 级灰阶，通常不建议开启。',
    'Only resize images and preserve original file structure.\\n\\nIgnores most options besides JPEG quality, color mode, output folder.':
        '仅缩放图像并保留原始文件结构。\\n\\n除 JPEG 质量、彩色模式、输出文件夹外，忽略大部分选项。',
    'Force full color images to be saved in lossless PNG format, dramatically increases the filesize.':
        '强制把全彩图像保存为无损 PNG，文件体积会大幅增加。',
    'Render vector PDFs to device width instead of height.\\n\\nUseful if you plan to crop a little off the top and bottom to fill screen.':
        '按设备宽度而非高度渲染矢量 PDF。\\n\\n如果打算裁掉上下少量边缘以填满屏幕，此选项很有用。',
    'Use a more compatible 8 bit PNG instead of 4 bit.':
        '使用兼容性更好的 8 位 PNG，而不是 4 位。',
    'Rotate 2 page spreads in opposite direction than normal.':
        '跨页图按相反方向旋转。',
    'Erase rainbow effect on color eink screen by attenuating interfering frequencies':
        '通过衰减干扰频率，消除彩色电子墨水屏的彩虹纹',
    'Replace JPG with lossy WebP and PNG with lossless WebP. This includes the JPG Quality.\\n\\nIgnored for Kindle EPUB/MOBI and all PDF.':
        '用有损 WebP 替换 JPG、用无损 WebP 替换 PNG（JPEG 质量设置同样生效）。\\n\\n对 Kindle 的 EPUB/MOBI 以及所有 PDF 无效。',
    'The JPEG quality, on a scale from 0 (worst) to 95 (best). \\n\\nDefault is 85 for most devices besides Kindle Scribe and Colorsoft, which are 90.\\n\\nHigher values are larger and higher quality, and may resolve blank page issues.':
        'JPEG 质量，范围 0（最差）到 95（最好）。\\n\\n除 Kindle Scribe 和 Colorsoft（默认 90）外，多数设备默认 85。\\n\\n数值越高体积越大、质量越好，也可能解决空白页问题。',
    'Resize cover to exact device resolution by center-cropping to aspect ratio first.\\nMay crop top/bottom or left/right depending on source aspect ratio. Not implemented for Kindle Scribe.':
        '先按宽高比居中裁剪，再把封面缩放到设备精确分辨率。\\n根据源图宽高比，可能裁掉上下或左右。Kindle Scribe 不支持此功能。',
    'Shift first page to opposite side in landscape for two page spread alignment':
        '横向时把首页偏移到另一侧，以对齐跨页',
    'Keep any original ComicInfo.xml files.\\n\\nKeeping this file may crash some readers like the Kobo native CBZ reader.':
        '保留原有的 ComicInfo.xml 文件。\\n\\n保留该文件可能导致某些阅读器崩溃，例如 Kobo 自带的 CBZ 阅读器。',
    'Hold shift while clicking for a low quality preview.':
        '按住 Shift 点击可生成低质量预览。',
    'Greater than default may cause performance issues on older ereaders.':
        '高于默认值可能导致老设备出现性能问题。',
    'Hover over each option/button to see an explanation! Options can be partially checked or fully checked!':
        '把鼠标悬停在每个选项/按钮上可查看说明！选项支持半选和全选！',
    '<html><head/><body><p><span style=" font-weight:600; text-decoration: underline;">Unchecked - 2 page landscape<br/></span>2 viewports for left and right pages</p><p><span style=" font-weight:600; text-decoration: underline;">Checked - 1 page landscape<br/></span>A single centered viewport for 1 page</p></body></html>':
        '<html><head/><body><p><span style=" font-weight:600; text-decoration: underline;">未勾选 - 横向双页<br/></span>左右两页各用一个视口</p><p><span style=" font-weight:600; text-decoration: underline;">勾选 - 横向单页<br/></span>单页使用一个居中视口</p></body></html>',
    '<html><head/><body><p style=\'white-space:pre\'><span style=" font-weight:600; text-decoration: underline;">Unchecked - Rotate Last<br/></span>' :
        None,   # placeholder, skipped
}

GUI_EXTRA = {
    '"><b>The new version is available!</b></a>': '"><b>有新版本可用！</b></a>',
    ' day(s) left': ' 天后结束',
    ' [referral]': ' [推广链接]',
    'Creating MOBI files': '正在生成 MOBI 文件',
}


def replace_in_file(path, mapping, label):
    src = io.open(path, encoding='utf-8').read()
    changed = 0
    for old, new in mapping.items():
        if new is None:
            continue
        n = src.count(old)
        if n == 0:
            print(f'  [{label}] NOT FOUND: {old[:80]!r}')
            continue
        src = src.replace(old, new)
        changed += n
    if changed:
        io.open(path, 'w', encoding='utf-8', newline='').write(src)
    print(f'{label}: {changed} replacements')


print('--- pass 2: multi-line tooltips ---')
replace_in_file(os.path.join(PKG, 'KCC_ui.py'), UI_EXTRA, 'KCC_ui.py')
print('--- pass 2: gui fragments ---')
replace_in_file(os.path.join(PKG, 'KCC_gui.py'), GUI_EXTRA, 'KCC_gui.py')

# field_specs tooltip titles (English UI text, logic-neutral)
p = os.path.join(PKG, 'KCC_gui.py')
src = io.open(p, encoding='utf-8').read()
field_fixes = [
    ("(self.seriesLine, 'Series',", "(self.seriesLine, '系列',"),
    ("(self.writerLine, 'Writer',", "(self.writerLine, '编剧',"),
    ("(self.pencillerLine, 'Penciller',", "(self.pencillerLine, '作画',"),
    ("(self.inkerLine, 'Inker',", "(self.inkerLine, '墨线',"),
    ("(self.coloristLine, '上色：',", "(self.coloristLine, '上色',"),
]
cnt = 0
for old, new in field_fixes:
    if old in src:
        src = src.replace(old, new)
        cnt += 1
    else:
        print('  field_spec NOT FOUND:', old)
io.open(p, 'w', encoding='utf-8', newline='').write(src)
print(f'field_specs titles fixed: {cnt}')
