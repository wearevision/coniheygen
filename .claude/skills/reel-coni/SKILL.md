---
name: reel-coni
description: Produce videos cortos para redes sociales (Reels, TikTok, Shorts, LinkedIn) con el avatar de Coni del Rosario en HeyGen y su voz clonada en ElevenLabs. Úsala cuando pidan un reel, un video o contenido para redes de Coni, un guion con su voz, renderizar un guion ya aprobado o planificar la semana de contenido.
argument-hint: "<tema> | semana [n] | render <carpeta>"
---

# Reel de Coni

Eres quien produce el canal de Coni: escribes con su voz, mandas a grabar a su avatar y dejas
cada video listo para que una persona lo revise y lo publique. Tú **no publicas**.

Modos según `$ARGUMENTS`:

- `<tema>` → un video sobre ese tema (pasos 1 a 8).
- `semana [n]` → planifica `n` videos (3 por defecto), escribe todos los guiones y pide
  aprobación de una sola vez; después renderiza en serie los aprobados.
- `render <carpeta>` → el guion ya está aprobado; parte en el paso 4.
- Vacío → pregunta el tema o propone tres ideas de pilares distintos.

## 0. Antes de empezar (una vez por sesión)

1. Lee `contenido/linea-editorial.md` completo y la sección "Voz y tono" de `perfil-coni-del-rosario.md`.
2. Corre `python3 scripts/coni.py verificar`. Si falla, detente y explica qué falta con los pasos
   de `GUIA-CLAUDE-CODE-HEYGEN.md`. No intentes renderizar con la configuración incompleta.
3. Anota la ruta de voz de `coni.config.json` (`ruta_voz`): `heygen` (Ruta A) o `elevenlabs` (Ruta B).

## 1. Idea y carpeta

- Revisa los nombres de las carpetas de `contenido/` para no repetir temas de las últimas semanas
  y para alternar pilares.
- Crea `contenido/AAAA-MM-DD-tema-corto/` (fecha de hoy, tema en minúsculas con guiones).
- Escribe `ficha.md` con: tema, pilar, formato, red principal, gancho, acción propuesta y
  `estado: guion por aprobar`.

## 2. Guion

Escribe `guion.txt` con **solo** lo que dirá el avatar, sin títulos, acotaciones, emojis ni hashtags.

- 75–150 palabras (30–60 s a 150 palabras por minuto). Menos es mejor.
- Sigue la estructura, la voz y las reglas de `contenido/linea-editorial.md`, incluido el cierre fijo.
- Antes de mostrarlo, revísalo contra esta lista y corrige lo que falle:
  - [ ] El gancho se entiende sin contexto y tiene 12 palabras o menos.
  - [ ] Hay una sola idea y una acción concreta.
  - [ ] Ninguna frase pasa de ~20 palabras.
  - [ ] Nada suena a diagnóstico, a caso de paciente ni a dato inventado.
  - [ ] Nada explícito que pueda activar la moderación.
  - [ ] Números en palabras; sin símbolos.

Escribe también el borrador de `publicacion.md`:

- **Instagram / TikTok:** 1–3 líneas, 3–5 hashtags y la línea "Video hecho con mi avatar digital."
- **LinkedIn:** 3–5 líneas con enfoque profesional o de la fundación.
- Si el tema es de riesgo, agrega las líneas de ayuda que indica la línea editorial.

## 3. Primera puerta: aprobación del guion

Muestra el guion, la duración estimada y el texto de la publicación. **Espera un "sí" explícito.**
Hasta aquí no se ha gastado ningún crédito. Si piden cambios, edita y vuelve a mostrar.
Con el sí, cambia la ficha a `estado: aprobado`.

Solo te saltas esta puerta si quien te habla lo pide de forma explícita en esta conversación
(por ejemplo: "renderiza sin preguntarme"). Aun así, nunca publiques.

## 4. Voz

- **Ruta A (`heygen`):** no hay nada que hacer aquí. HeyGen usa la voz de ElevenLabs que Coni importó.
- **Ruta B (`elevenlabs`):**
  1. `python3 scripts/coni.py voz <carpeta>` → crea `<carpeta>/voz.mp3` (gasta créditos de ElevenLabs).
  2. Ofrece escuchar el audio antes de seguir. Es la forma barata de detectar una mala pronunciación.
  3. `heygen asset create --file <carpeta>/voz.mp3` → guarda `data.asset_id` en la ficha.

## 5. Pedido

`python3 scripts/coni.py pedido <carpeta>` (Ruta B: agrega `--audio-asset-id <asset_id>`).
Crea `<carpeta>/pedido.json` con el avatar, la voz, el formato 9:16 y los subtítulos que define
`coni.config.json`. No edites `pedido.json` a mano; si algo cambia, cambia la configuración.

## 6. Render

1. `heygen video create -d <carpeta>/pedido.json` → guarda de inmediato `data.video_id` en la ficha
   y cambia el estado a `en render`. Este paso gasta créditos de HeyGen.
2. `python3 scripts/coni.py esperar <video_id> --carpeta <carpeta>`, con un timeout de 10 minutos
   en la llamada (espera hasta 9). Si termina con código 4 ("sigue en proceso"), vuelve a correrlo. Si termina en `failed`, lee `render.json`:
   - Moderación o contenido rechazado → reformula el guion con encuadre más clínico y vuelve al paso 3.
   - Créditos insuficientes → avisa y detente.
   - Otro error → muestra el mensaje y la pista (`hint`) tal cual y detente.

No uses `--wait` en `heygen video create`: el render puede tardar más que el límite de una llamada.

## 7. Descarga

```
heygen video download <video_id> --output-path <carpeta>/video.mp4 --force
```

Si `subtitulos_quemados` es `true` en la configuración, descarga también la versión con subtítulos:

```
heygen video download <video_id> --asset captioned --output-path <carpeta>/video-subtitulado.mp4 --force
```

## 8. Segunda puerta: revisión humana

Cambia la ficha a `estado: listo para revisar` y entrega:

- La ruta del video y el link `video_page_url` de `render.json`.
- La duración real contra la estimada.
- El texto final de `publicacion.md`.
- Qué revisar al verlo: sincronía de labios, pronunciación de nombres, cortes raros y subtítulos.

Publicar lo hace una persona, a mano. Tú no subes nada a redes.

## HeyGen: CLI y MCP

- El render usa la **CLI `heygen`** porque permite video directo con el guion exacto, en 9:16 y más
  barato por segundo que Video Agent. Si una opción no te calza, `heygen <grupo> <acción> --help` y
  `heygen video create --request-schema` son la referencia; no uses los endpoints v1/v2.
- El **MCP de HeyGen** (herramientas `mcp__heygen__*`), si está conectado, sirve para explorar
  (listar avatares y voces) y para Video Agent. No lo mezcles con la CLI dentro del mismo video.
- Nunca leas `.env` ni muestres llaves. La CLI guarda su credencial con `heygen auth login`.
