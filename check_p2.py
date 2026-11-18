# -*- coding: utf-8 -*-
from pathlib import Path

for cap in [1, 2, 3]:
    p = Path(f"novela/capitulos_scifi/capitulo_{cap}.md")
    print(f"\n*** {p.name} ***")
    lines = p.read_text(encoding="utf-8").splitlines()
    for num, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        if s.startswith(u'—') and u'—' in s[1:]:
            parts = s.split(u'—')
            if len(parts) >= 4:
                p2 = parts[3].strip()
                if not p2.endswith(('.', '!', '?', u'…', u'»', '"', "'")):
                    print(f"L{num} segundo parlamento sin punto: {s}")
