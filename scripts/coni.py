#!/usr/bin/env python3
"""Herramientas de apoyo para producir videos del avatar de Coni en HeyGen.

    python3 scripts/coni.py verificar
    python3 scripts/coni.py pedido  contenido/<pieza> [--audio-asset-id ID]
    python3 scripts/coni.py voz     contenido/<pieza>
    python3 scripts/coni.py esperar <video_id> [--carpeta contenido/<pieza>] [--max-min 9]

Solo usa la biblioteca estándar. Para HeyGen llama a la CLI oficial (`heygen`), que guarda
su propia credencial con `heygen auth login`. Para ElevenLabs (solo Ruta B) llama a su API
con ELEVENLABS_API_KEY, que se lee del entorno o del archivo .env en la raíz del repo.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "coni.config.json"
PENDIENTE = "PENDIENTE"
# Mismo ritmo que usa el revisor de guion del curso (curso-heygen.html).
PALABRAS_POR_MINUTO = 150
ELEVEN_BASE = os.environ.get("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io")
MODELOS_ELEVEN = {"eleven_multilingual_v2", "eleven_v3", "eleven_turbo_v2_5", "eleven_flash_v2_5"}


class Falla(Exception):
    """Error con un mensaje pensado para leerse tal cual."""


def cargar_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Falla(f"No encuentro {CONFIG.name} en la raíz del repo.")
    except json.JSONDecodeError as e:
        raise Falla(f"{CONFIG.name} no es JSON válido (línea {e.lineno}): {e.msg}")


def leer_env(nombre):
    if os.environ.get(nombre):
        return os.environ[nombre]
    archivo = RAIZ / ".env"
    if not archivo.exists():
        return None
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("export "):
            linea = linea[len("export "):]
        clave, sep, valor = linea.partition("=")
        if sep and clave.strip() == nombre:
            return valor.strip().strip("'\"") or None
    return None


def heygen(*args):
    """Corre la CLI de HeyGen y devuelve (código de salida, JSON de stdout o None, stderr)."""
    proc = subprocess.run(["heygen", *args], capture_output=True, text=True)
    try:
        datos = json.loads(proc.stdout) if proc.stdout.strip() else None
    except json.JSONDecodeError:
        datos = None
    return proc.returncode, datos, proc.stderr.strip()


def error_heygen(stderr):
    try:
        err = json.loads(stderr)["error"]
        return " · ".join(p for p in (err.get("message"), err.get("hint")) if p)
    except (json.JSONDecodeError, KeyError, TypeError):
        return stderr or "sin detalle"


def leer_guion(carpeta):
    archivo = carpeta / "guion.txt"
    if not archivo.exists():
        raise Falla(f"Falta {archivo}. El guion aprobado va ahí, solo con lo que dice el avatar.")
    texto = archivo.read_text(encoding="utf-8").strip()
    if not texto:
        raise Falla(f"{archivo} está vacío.")
    return texto


def estimar_segundos(texto):
    palabras = len(texto.split())
    pausas = texto.count("\n\n")
    return palabras / PALABRAS_POR_MINUTO * 60 + pausas * 0.6


def mmss(segundos):
    segundos = int(round(segundos))
    return f"{segundos // 60}:{segundos % 60:02d}"


def pendiente(valor):
    return not valor or valor == PENDIENTE


def cmd_verificar(_args):
    fallas = 0

    def linea(ok, texto, detalle=None):
        nonlocal fallas
        fallas += 0 if ok else 1
        print(f"  {'✔' if ok else '✘'} {texto}")
        if detalle:
            print(f"      {detalle}")

    print("Ficha técnica")
    cfg = cargar_config()
    hg = cfg.get("heygen", {})
    ruta = cfg.get("ruta_voz", "heygen")
    linea(ruta in ("heygen", "elevenlabs"), f"ruta_voz = {ruta}",
          None if ruta in ("heygen", "elevenlabs") else "Debe ser \"heygen\" o \"elevenlabs\".")
    linea(not pendiente(hg.get("avatar_id")), "heygen.avatar_id completo")
    if ruta == "heygen":
        linea(not pendiente(hg.get("voice_id")), "heygen.voice_id completo")
    else:
        linea(not pendiente(cfg.get("elevenlabs", {}).get("voice_id")), "elevenlabs.voice_id completo")

    print("\nHeyGen")
    if not shutil.which("heygen"):
        linea(False, "CLI de HeyGen instalada",
              "Instálala con: curl -fsSL https://static.heygen.ai/cli/install.sh | bash")
        print(f"\n{fallas} punto(s) por resolver.")
        return 1
    linea(True, "CLI de HeyGen instalada")
    codigo, _, err = heygen("auth", "status")
    sesion = codigo == 0
    linea(sesion, "Sesión iniciada en la CLI",
          None if sesion else "Corre: heygen auth login   (" + error_heygen(err) + ")")

    if sesion and not pendiente(hg.get("avatar_id")):
        codigo, datos, err = heygen("avatar", "looks", "get", hg["avatar_id"])
        look = (datos or {}).get("data") or {}
        if codigo == 0 and look:
            motores = look.get("supported_api_engines") or []
            linea(True, f"Avatar encontrado: {look.get('name', '(sin nombre)')} · {look.get('avatar_type', '?')}",
                  f"Motores disponibles: {', '.join(motores) or 'sin dato'}")
            linea(bool(look.get("preview_image_url")), "Avatar listo para usar",
                  None if look.get("preview_image_url") else "HeyGen aún lo está procesando. Espera unos minutos.")
            if hg.get("motor") and motores and hg["motor"] not in motores:
                linea(False, f"El motor \"{hg['motor']}\" no está disponible para este look",
                      "Deja \"motor\": null en coni.config.json.")
        else:
            linea(False, "Avatar encontrado",
                  "Revisa que sea el ID del look y no el del grupo. " + error_heygen(err))

    if sesion and ruta == "heygen" and not pendiente(hg.get("voice_id")):
        voz, token = None, None
        for _ in range(10):
            args = ["voice", "list", "--type", "private", "--limit", "100"]
            if token:
                args += ["--token", token]
            codigo, datos, err = heygen(*args)
            if codigo != 0 or not datos:
                break
            voz = next((v for v in datos.get("data", []) if v.get("voice_id") == hg["voice_id"]), None)
            token = datos.get("next_token") if datos.get("has_more") else None
            if voz or not token:
                break
        if codigo != 0:
            linea(False, "Listar voces en HeyGen", error_heygen(err))
        else:
            linea(bool(voz), f"Voz encontrada en HeyGen: {voz.get('name')}" if voz else "Voz encontrada en HeyGen",
                  None if voz else "No aparece entre tus voces privadas. Revisa la sesión 6 del curso "
                                   "o cambia a \"ruta_voz\": \"elevenlabs\".")

    if ruta == "elevenlabs":
        print("\nElevenLabs")
        clave = leer_env("ELEVENLABS_API_KEY")
        linea(bool(clave), "ELEVENLABS_API_KEY disponible",
              None if clave else "Cópiala a un archivo .env en la raíz (mira .env.example).")
        voice_id = cfg.get("elevenlabs", {}).get("voice_id")
        if clave and not pendiente(voice_id):
            req = urllib.request.Request(f"{ELEVEN_BASE}/v1/voices/{voice_id}", headers={"xi-api-key": clave})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    nombre = json.loads(r.read()).get("name", "(sin nombre)")
                linea(True, f"Voz encontrada en ElevenLabs: {nombre}")
            except urllib.error.HTTPError as e:
                linea(False, "Voz encontrada en ElevenLabs",
                      f"HTTP {e.code}. Revisa el voice_id y que la llave tenga permiso de lectura de Voices.")
            except urllib.error.URLError as e:
                linea(False, "Conexión con ElevenLabs", str(e.reason))

    marca = cfg.get("metricool", {}).get("marca_id")
    print("\nInstagram (Metricool)")
    print(f"  · marca_id: {marca}" if not pendiente(marca) else
          "  · marca_id pendiente. Solo hace falta para programar; Claude lo completa con get_brand_settings.")

    print("\nTodo listo." if fallas == 0 else f"\n{fallas} punto(s) por resolver.")
    return 0 if fallas == 0 else 1


def cmd_pedido(args):
    carpeta = Path(args.carpeta)
    cfg = cargar_config()
    hg = cfg.get("heygen", {})
    ruta = cfg.get("ruta_voz", "heygen")
    texto = leer_guion(carpeta)

    if pendiente(hg.get("avatar_id")):
        raise Falla("Falta heygen.avatar_id en coni.config.json.")
    cuerpo = {
        "type": "avatar",
        "avatar_id": hg["avatar_id"],
        "title": f"Coni · {carpeta.name}",
        "aspect_ratio": hg.get("aspect_ratio") or "9:16",
        "caption": {"file_format": "srt"},
    }
    if hg.get("resolution"):
        cuerpo["resolution"] = hg["resolution"]
    if hg.get("motor"):
        cuerpo["engine"] = {"type": hg["motor"]}
    if hg.get("subtitulos_quemados"):
        cuerpo["caption"]["style"] = "default"

    if args.audio_asset_id:
        cuerpo["audio_asset_id"] = args.audio_asset_id
    elif ruta == "elevenlabs":
        raise Falla("La Ruta B necesita --audio-asset-id. Primero: `coni.py voz` y `heygen asset create`.")
    else:
        if pendiente(hg.get("voice_id")):
            raise Falla("Falta heygen.voice_id en coni.config.json.")
        cuerpo["script"] = texto
        cuerpo["voice_id"] = hg["voice_id"]
        ajustes_voz = {}
        ajustes = hg.get("ajustes_elevenlabs")
        if ajustes:
            if ajustes.get("model") and ajustes["model"] not in MODELOS_ELEVEN:
                raise Falla(f"Modelo de ElevenLabs no válido: {ajustes['model']}")
            if ajustes.get("model") == "eleven_v3" and ajustes.get("stability") not in (None, 0, 0.5, 1):
                raise Falla("Con eleven_v3, stability debe ser 0, 0.5 o 1.")
            ajustes_voz["engine_settings"] = {"engine_type": "elevenlabs", **ajustes}
        if hg.get("velocidad") not in (None, 1, 1.0):
            ajustes_voz["speed"] = hg["velocidad"]
        if ajustes_voz:
            cuerpo["voice_settings"] = ajustes_voz

    destino = carpeta / "pedido.json"
    destino.write_text(json.dumps(cuerpo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    segundos = estimar_segundos(texto)
    print(f"Pedido listo: {destino}")
    print(f"  Voz: {'audio propio (Ruta B)' if args.audio_asset_id else 'ElevenLabs vía HeyGen (Ruta A)'}")
    print(f"  Guion: {len(texto.split())} palabras · ~{mmss(segundos)}")
    if segundos > 90:
        print("  Aviso: pasa de 90 s. Para Reels y TikTok conviene 30–60 s.")
    return 0


def cmd_voz(args):
    carpeta = Path(args.carpeta)
    cfg = cargar_config().get("elevenlabs", {})
    clave = leer_env("ELEVENLABS_API_KEY")
    if not clave:
        raise Falla("Falta ELEVENLABS_API_KEY (en el entorno o en .env).")
    if pendiente(cfg.get("voice_id")):
        raise Falla("Falta elevenlabs.voice_id en coni.config.json.")
    texto = leer_guion(carpeta)
    carga = {"text": texto, "model_id": cfg.get("model_id") or "eleven_multilingual_v2"}
    if cfg.get("voice_settings"):
        carga["voice_settings"] = cfg["voice_settings"]
    formato = cfg.get("output_format") or "mp3_44100_128"
    req = urllib.request.Request(
        f"{ELEVEN_BASE}/v1/text-to-speech/{cfg['voice_id']}?output_format={formato}",
        data=json.dumps(carga).encode("utf-8"),
        headers={"xi-api-key": clave, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            audio = r.read()
    except urllib.error.HTTPError as e:
        raise Falla(f"ElevenLabs respondió HTTP {e.code}: {e.read()[:400].decode('utf-8', 'replace')}")
    except urllib.error.URLError as e:
        raise Falla(f"No pude conectar con ElevenLabs: {e.reason}")
    destino = carpeta / "voz.mp3"
    destino.write_bytes(audio)
    print(f"Audio listo: {destino} ({len(audio) // 1024} KB · ~{mmss(estimar_segundos(texto))})")
    print("Escúchalo antes de gastar créditos de video.")
    return 0


def cmd_esperar(args):
    limite = time.time() + args.max_min * 60
    while True:
        codigo, datos, err = heygen("video", "get", args.video_id)
        if codigo != 0:
            raise Falla(f"heygen video get falló (código {codigo}): {error_heygen(err)}")
        video = (datos or {}).get("data") or {}
        estado = video.get("status", "?")
        print(f"[{time.strftime('%H:%M:%S')}] {estado}", flush=True)
        if estado in ("completed", "failed"):
            if args.carpeta:
                (Path(args.carpeta) / "render.json").write_text(
                    json.dumps(video, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if estado == "failed":
                print(f"Falló: {video.get('failure_code', '')} {video.get('failure_message', '')}".strip())
                return 1
            print(f"Listo · {video.get('duration', '?')} s · {video.get('video_page_url', '')}")
            return 0
        if time.time() + args.intervalo > limite:
            print("Sigue en proceso. Vuelve a correr el mismo comando para seguir esperando.")
            return 4
        time.sleep(args.intervalo)


def main():
    p = argparse.ArgumentParser(description="Producción de videos del avatar de Coni.")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("verificar", help="Revisa que la conexión con HeyGen (y ElevenLabs) esté lista.")
    sp = sub.add_parser("pedido", help="Arma pedido.json para `heygen video create -d`.")
    sp.add_argument("carpeta")
    sp.add_argument("--audio-asset-id", help="Ruta B: asset de HeyGen con el audio de ElevenLabs.")
    sv = sub.add_parser("voz", help="Ruta B: genera voz.mp3 con ElevenLabs a partir de guion.txt.")
    sv.add_argument("carpeta")
    se = sub.add_parser("esperar", help="Espera a que HeyGen termine un video.")
    se.add_argument("video_id")
    se.add_argument("--carpeta", help="Guarda la respuesta final en <carpeta>/render.json.")
    se.add_argument("--max-min", type=float, default=9, help="Minutos máximos de espera (por defecto 9).")
    se.add_argument("--intervalo", type=float, default=30, help="Segundos entre consultas (por defecto 30).")
    args = p.parse_args()
    comandos = {"verificar": cmd_verificar, "pedido": cmd_pedido, "voz": cmd_voz, "esperar": cmd_esperar}
    try:
        return comandos[args.comando](args)
    except Falla as e:
        print(f"✘ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
