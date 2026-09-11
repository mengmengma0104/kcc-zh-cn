# -*- coding: utf-8 -*-
"""Translate the remaining f-string fragments (placeholders must stay live)."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, 'kindlecomicconverter', 'KCC_gui.py')

REPLACEMENTS = [
    ("f'<b>{job_progress_number}Source:</b> '",
     "f'<b>{job_progress_number}源文件：</b> '"),
    ('f"kindlegen: {e.strerror}\\n\\n Re-install Rosetta/Kindle Previewer/other Intel app?\\n\\nPlease email Amazon to make Kindle Previewer Apple silicon native at amazon.com/kindle-help"',
     'f"kindlegen：{e.strerror}\\n\\n 是否重新安装 Rosetta/Kindle Previewer/其他 Intel 应用？\\n\\n请发邮件给 Amazon，推动 Kindle Previewer 原生支持 Apple 芯片：amazon.com/kindle-help"'),
    ("f'Editing {len(self.files)} files.'",
     "f'正在编辑 {len(self.files)} 个文件。'"),
    ("f'Processing {i}/{total}: {os.path.basename(file)}'",
     "f'正在处理 {i}/{total}：{os.path.basename(file)}'"),
    ("f'{os.path.basename(file)}: CBR is read-only'",
     "f'{os.path.basename(file)}：CBR 为只读'"),
    ('f"\\n...and {len(errors) - 10} more"',
     'f"\\n……另有 {len(errors) - 10} 个"'),
    ("f'Successfully updated {total} files.'",
     "f'已成功更新 {total} 个文件。'"),
    ("f'Volume count ({len(volumes)}) != file count ({fileCount})'",
     "f'卷号数量（{len(volumes)}）与文件数量（{fileCount}）不一致'"),
]

src = io.open(PATH, encoding='utf-8').read()
for old, new in REPLACEMENTS:
    n = src.count(old)
    if n != 1:
        print(f'WARN count={n} for {old[:70]!r}')
    src = src.replace(old, new, 1)

io.open(PATH, 'w', encoding='utf-8', newline='').write(src)
print('done')
