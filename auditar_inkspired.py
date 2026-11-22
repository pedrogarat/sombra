# -*- coding: utf-8 -*-
import re
from pathlib import Path

queismo_pat = re.compile(
    r'\b(de que|a pesar que|antes que|despu[eé]s que|segur[oa]s? que|convencid[oa]s? que|'
    r'cuenta que|acord\w* que|enter\w* que|asegur\w* que|duda que|miedo que|orgullos\w* que|'
    r'consciente que|al margen que|en caso que|a condici[oó]n que|hasta el punto que|'
    r'con tal que|resulta de que|parece de que|piens\w* de que|cre[eo]\w* de que|'
    r'sab\w* de que|dij\w* de que|esper\w* de que|debo de |habr[ií]a que|para que|'
    r'a que la|a que el|en que )\b',
    re.IGNORECASE,
)

for cap in range(1, 6):
    p = Path(f"novela/capitulos_scifi/capitulo_{cap}.md")
    lines = p.read_text(encoding="utf-8").splitlines()
    print(f"\n================ CAP {cap} ================")
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if not s:
            continue
        # 1. Queismo / dequeismo
        for m in queismo_pat.finditer(s):
            if m.group(0).lower() not in ("para que",):
                print(f"  [QUEISMO/DEQUEISMO] L{i}: ({m.group(0)}) -> {s}")
        # 2. Viñetas
        if "•" in s or s.startswith("- "):
            print(f"  [VIÑETA] L{i}: {s}")
        # 3. Falta de punto final en párrafos o diálogos o citas
        if not s.startswith(("#", "---", "*")):
            if not s.endswith((".", ":", "!", "?", "»", '"', "…", "*")):
                print(f"  [SIN PUNTO FINAL] L{i}: {s[-90:]}")
        # 4. Fin en cursiva sin punto
        if s.endswith("*") and not s.startswith("*") and not re.search(r'[.!?»…:]\*+$', s):
            print(f"  [CURSIVA SIN PUNTO] L{i}: {s[-90:]}")
        # 5. Encabezado pegado al párrafo siguiente (sin línea en blanco)
        if s.startswith("#") and i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("*"):
            print(f"  [ENCABEZADO PEGADO] L{i}: {s} -> L{i+1}: {lines[i].strip()[:60]}")
        # 6. Repetición léxica en la misma línea (palabras >= 6 letras)
        words = re.findall(r'[a-záéíóúñ]{6,}', s.lower())
        seen = {}
        for idx_w, w in enumerate(words):
            if w in seen and idx_w - seen[w] <= 12:
                print(f"  [REPETICION] L{i}: '{w}' -> {s[:140]}")
            seen[w] = idx_w
