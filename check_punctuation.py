# -*- coding: utf-8 -*-
from pathlib import Path

valid_ends = ('.', ':', u'—', '!', '?', u'»', '"', "'", '-', u'…')

for cap in [1, 2, 3]:
    p = Path(f"novela/capitulos_scifi/capitulo_{cap}.md")
    print(f"\n=== {p.name} ===")
    if not p.exists():
        print("No existe")
        continue
    lines = p.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        if s.startswith(('#', '---', '>', '*', u'•')):
            continue
        if not s.endswith(valid_ends):
            print(f"L{idx}: {s}")
