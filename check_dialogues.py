# -*- coding: utf-8 -*-
from pathlib import Path
import re

for cap in [1, 2, 3]:
    p = Path(f"novela/capitulos_scifi/capitulo_{cap}.md")
    print(f"\n==================== {p.name} ====================")
    lines = p.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        # Buscar párrafos que terminen en punto dentro de diálogos pero falte punto exterior o similar
        # O párrafos que terminen en letra
        if re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]$', s):
            print(f"[SIN PUNTO FINAL] L{idx}: {s}")
        # Diálogos: verificar puntuación al final de parlamento
        if s.startswith(u"—") or s.startswith(u"-"):
            # Si termina con raya o guión sin cerrar
            pass
        # Guiones largos vs guiones cortos
        if "--" in s:
            print(f"[DOBLE GUION] L{idx}: {s}")
