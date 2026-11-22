# -*- coding: utf-8 -*-
"""
Script autónomo para Windows: Generación y regeneración automática de banners 21:9 para SOMBRA.
- Prioriza los capítulos listados en banners_pendientes_rehacer.json (cola de mejoras/correcciones).
- Si la cola está vacía, busca el primer capítulo sin banner (del 1 al 25).
- Lanza agy.exe de forma silenciosa, verifica que el archivo cap_<N>.jpg se ha actualizado,
  compila la web (node build-novel-data.js), actualiza historial y sube a GitHub automáticamente.
- Se autoelimina del Programador de Tareas de Windows cuando termina el último capítulo pendiente.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
BANNERS_DIR = WORKSPACE / "img" / "banners"
PROMPTS_FILE = WORKSPACE / "novela" / "prompts_banners_21_9.md"
QUEUE_FILE = WORKSPACE / "banners_pendientes_rehacer.json"
AGY_EXE = Path.home() / ".gemini" / "bin" / "agy.exe"
TASK_NAME = "SOMBRA_Generador_Banners_21_9"


def cargar_cola():
    if QUEUE_FILE.exists():
        try:
            data = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [int(x) for x in data]
        except Exception as e:
            print(f"[Aviso] Error leyendo {QUEUE_FILE.name}: {e}")
    return []


def guardar_cola(cola):
    QUEUE_FILE.write_text(json.dumps(cola, indent=2), encoding="utf-8")


def encontrar_siguiente_capitulo():
    BANNERS_DIR.mkdir(parents=True, exist_ok=True)
    cola = cargar_cola()
    if cola:
        return cola[0], True  # (cap_num, es_regeneracion)
    for cap in range(1, 26):
        banner_jpg = BANNERS_DIR / f"cap_{cap}.jpg"
        banner_png = BANNERS_DIR / f"cap_{cap}.png"
        if not banner_jpg.exists() and not banner_png.exists():
            return cap, False
    return None, False


def extraer_prompt(cap_num):
    if not PROMPTS_FILE.exists():
        print(f"[ERROR] No se encuentra {PROMPTS_FILE}")
        return None
    content = PROMPTS_FILE.read_text(encoding="utf-8")
    patron = rf"###?\s*Cap[íi]tulo\s+{cap_num}\b.*?(?=###?\s*Cap[íi]tulo|\Z)"
    match = re.search(patron, content, re.DOTALL | re.IGNORECASE)
    if not match:
        print(f"[ERROR] No se encontró el prompt para el capítulo {cap_num} en {PROMPTS_FILE}")
        return None
    seccion = match.group(0)
    # Extraer entre comillas invertidas `...` o bloque ```...```
    code_block = re.search(r"```(?:\w+)?\s*\n(.*?)\n```", seccion, re.DOTALL)
    if code_block:
        return code_block.group(1).strip()
    inline_code = re.search(r"`([^`]{40,})`", seccion, re.DOTALL)
    if inline_code:
        return inline_code.group(1).strip()
    return seccion.strip()


def desinstalar_tarea_programada():
    """Elimina la tarea del Programador de Tareas de Windows cuando ya no quedan capítulos."""
    try:
        subprocess.run(
            ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
            capture_output=True,
            text=True,
        )
        print(f"[OK] Tarea programada '{TASK_NAME}' desinstalada de Windows automáticamente.")
    except Exception as e:
        print(f"[Aviso] No se pudo desinstalar la tarea programada: {e}")


def mostrar_notificacion_windows(titulo, mensaje, ruta_imagen=None):
    """Muestra una notificación nativa Toast en Windows con imagen y clic para abrirla en grande."""
    xml_img = ""
    launch_attr = ""
    if ruta_imagen and Path(ruta_imagen).exists():
        uri_img = Path(ruta_imagen).resolve().as_uri()
        xml_img = f'<image placement="hero" src="{uri_img}"/>'
        launch_attr = f'launch="{uri_img}" activationType="protocol"'

    ps_cmd = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null
    $template = @"
    <toast {launch_attr}>
        <visual>
            <binding template="ToastGeneric">
                <text>{titulo}</text>
                <text>{mensaje}</text>
                {xml_img}
            </binding>
        </visual>
    </toast>
"@
    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("SOMBRA Novela").Show($toast)
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
    except Exception as e:
        print(f"[Aviso] No se pudo enviar notificación nativa: {e}")


def actualizar_web_y_github():
    """Compila chapters-data.js / index.html, actualiza historial y despliega en GitHub."""
    pasos = [
        ("Compilando datos web (build-novel-data.js)", ["node", "build-novel-data.js"]),
        ("Actualizando bitácora (recopilar_historial.py)", [sys.executable, ".agents/skills/memo/scripts/recopilar_historial.py"]),
        ("Sincronizando con GitHub (sync_multiversion_to_github.py)", [sys.executable, "sync_multiversion_to_github.py"]),
    ]
    for desc, cmd in pasos:
        print(f"[*] {desc}...")
        res = subprocess.run(cmd, cwd=str(WORKSPACE), capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0:
            print(f"[ERROR] Falló '{desc}' (exit {res.returncode}):\n{res.stderr}\n{res.stdout}")
            return False
        print(f"[OK] {desc} completado.")
    return True


def main():
    print("=" * 60)
    print("  SOMBRA: Generador Autónomo de Banners 21:9 (Windows)")
    print("=" * 60)

    cap, es_regeneracion = encontrar_siguiente_capitulo()
    if cap is None:
        print("[OK] ¡Todos los capítulos pendientes han sido completados!")
        desinstalar_tarea_programada()
        mostrar_notificacion_windows(
            "SOMBRA Novela - Colección Completa",
            "¡Todos los banners 21:9 pendientes han sido actualizados y publicados en la web! La tarea automática se ha autoeliminado.",
        )
        sys.exit(0)

    modo = "REGENERACIÓN" if es_regeneracion else "NUEVO"
    print(f"[*] Siguiente capítulo a procesar ({modo}): Capítulo {cap}")
    prompt_texto = extraer_prompt(cap)
    if not prompt_texto:
        sys.exit(1)

    print(f"[*] Prompt cargado ({len(prompt_texto)} caracteres).")
    banner_dest = BANNERS_DIR / f"cap_{cap}.jpg"
    mtime_previo = banner_dest.stat().st_mtime if banner_dest.exists() else 0.0

    instruccion_agente = (
        f"Ejecuta esta tarea automática de banner 21:9 para el Capítulo {cap} de la novela SOMBRA:\n"
        f"REGLAS ESTRICTAS DE COHERENCIA VISUAL:\n"
        f"- Consulta los retratos canónicos en img/personajes/ (thomas.jpg, sarah.jpg, jean_luc.jpg, ramos.jpg, pleh.jpg, tripulacion.jpg) "
        f"para respetar fielmente la apariencia, etnia, edad, peinado y vestuario de cada personaje.\n"
        f"- CERO texto, letras, números o hologramas flotantes inventados.\n"
        f"1. Invoca al subagente 'image-generator' con Role 'Banner Image Generator Cap {cap}' usando exactamente este prompt:\n"
        f"'''\n{prompt_texto}\n'''\n"
        f"2. Cuando el subagente responda con la ruta del archivo generado, recórtalo a 21:9 sobrescribiendo img/banners/cap_{cap}.jpg ejecutando:\n"
        f"python recortar_banner_21_9.py \"<ruta_imagen_generada>\" {cap}\n"
        f"3. Verifica que img/banners/cap_{cap}.jpg exista y esté recién guardado.\n"
        f"4. Responde únicamente: [BANNER_CAP_{cap}_COMPLETADO]"
    )

    print(f"[*] Lanzando agy.exe para el Capítulo {cap} en segundo plano...")
    cmd = [
        str(AGY_EXE),
        "--mode", "auto",
        "--project", str(WORKSPACE),
        "--print", instruccion_agente,
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        print("[STDOUT]:")
        print(proc.stdout)
        if proc.stderr:
            print("[STDERR]:")
            print(proc.stderr)

        actualizado = banner_dest.exists() and (banner_dest.stat().st_mtime > mtime_previo)
        if actualizado:
            print(f"\n[ÉXITO] ¡Banner de Capítulo {cap} generado correctamente en {banner_dest}!")
            # Actualizar web, historial y GitHub directamente desde Python
            web_ok = actualizar_web_y_github()

            # Sacar de la cola si era una regeneración
            if es_regeneracion:
                cola = cargar_cola()
                if cap in cola:
                    cola.remove(cap)
                    guardar_cola(cola)
                    print(f"[OK] Capítulo {cap} retirado de la cola. Pendientes: {cola}")

            estado_web = "y web actualizada en GitHub" if web_ok else "(pendiente de push a GitHub)"
            mostrar_notificacion_windows(
                "SOMBRA Novela",
                f"Imagen Generada SOMBRA capítulo {cap} {estado_web}. Haz clic para verla en grande.",
                ruta_imagen=banner_dest,
            )

            # Comprobar si ya no queda nada pendiente tras este capítulo
            sig_cap, _ = encontrar_siguiente_capitulo()
            if sig_cap is None:
                desinstalar_tarea_programada()
                mostrar_notificacion_windows(
                    "SOMBRA Novela - Actualización Completa",
                    "¡Todos los banners críticos han sido regenerados y publicados en la web! La tarea automática se ha autoeliminado.",
                )
        else:
            print(f"\n[AVISO] El proceso finalizó, pero {banner_dest} no se actualizó (se reintentará en el próximo ciclo).")
    except Exception as e:
        print(f"[ERROR al ejecutar agy]: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
