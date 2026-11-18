# -*- coding: utf-8 -*-
from pathlib import Path
import re

def auditar_capitulo(ruta):
    p = Path(ruta)
    print(f"\n==========================================")
    print(f" AUDITANDO: {p.name}")
    print(f"==========================================")
    lines = p.read_text(encoding="utf-8").splitlines()
    
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        
        # 1. Títulos de secciones o metadatos
        if s.startswith(('#', '---', '>')):
            continue
            
        # 2. Puntos al final de viñetas o listas
        if s.startswith(u'•'):
            if not s.endswith(('.', ':', '!', '?')):
                print(f"[VIÑETA SIN PUNTO FINAL] L{i}: {s}")
            continue

        # 3. Fecha/hora al inicio de sección
        if s.startswith('*') and s.endswith('*'):
            continue
            
        # 4. Falta de punto al final de párrafo narrativo
        if not s.endswith(('.', ':', u'—', '!', '?', u'»', '"', u'…')):
            print(f"[PARRAFO SIN PUNTO FINAL] L{i}: {s}")
            
        # 5. Diálogos mal puntuados (ejemplo: —Diálogo— dijo él sin punto final)
        if s.startswith(u'—'):
            # Si tiene inciso narrativo al final, debe terminar en punto
            if not s.endswith(('.', '!', '?', u'»', '"', u'…')):
                print(f"[DIALOGO SIN SIGNO FINAL] L{i}: {s}")
        
        # 6. Uso alterno Sala 2 vs Sala Dos
        if 'sala 2' in s.lower():
            print(f"[USO DE 'SALA 2'] L{i}: {s}")
        if 'sala dos' in s.lower() and not s.startswith('#'):
            print(f"[USO DE 'SALA DOS'] L{i}: {s}")
            
        # 7. Tiempo de pausa
        if any(w in s.lower() for w in ['diez minutos', 'media hora']):
            print(f"[PAUSA / TIEMPO] L{i}: {s}")

auditar_capitulo("novela/capitulos_scifi/capitulo_1.md")
auditar_capitulo("novela/capitulos_scifi/capitulo_2.md")
auditar_capitulo("novela/capitulos_scifi/capitulo_3.md")
