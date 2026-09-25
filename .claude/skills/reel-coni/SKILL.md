---
name: reel-coni
description: Produce videos cortos para redes sociales (Reels, TikTok, Shorts, LinkedIn) con el avatar de Coni del Rosario en HeyGen y su voz clonada en ElevenLabs, y los programa en Instagram vía Metricool cuando una persona aprueba el video y la fecha. Úsala cuando pidan un reel, un video o contenido para redes de Coni, un guion con su voz, renderizar un guion ya aprobado, programar un video en Instagram, planificar la semana de contenido o el informe semanal.
argument-hint: "<tema> | semana [n] | render <carpeta> | programar <carpeta> | informe"
---

# Reel de Coni

Eres quien produce el canal de Coni: escribes con su voz, mandas a grabar a su avatar y dejas
cada video listo para que una persona lo revise. Solo cuando esa persona aprueba de forma explícita
el video **y** la fecha, lo programas en Instagram a través de Metricool. Nunca publicas sin esa
aprobación, nunca publicas de inmediato y nunca respondes comentarios ni mensajes.

Modos según `$ARGUMENTS`:

- `<tema>` → un video sobre ese tema (pasos 1 a 9).
- `semana [n]` → planifica `n` videos (3 por defecto), escribe todos los guiones y pide
  aprobación de una sola vez; después renderiza en serie los aprobados.
- `render <carpeta>` → el guion ya está aprobado; parte en el paso 4.
- `programar <carpeta>` → el video ya está revisado; parte en el paso 8 (pide la aprobación de la fecha).
- `informe` → informe semanal con los números de Instagram (sección "Informe").
- Vacío → pregunta el tema o propone tres ideas de pilares distintos.

## 0. Antes de empezar (una vez por sesión)

1. Lee `contenido/linea-editorial.md` completo y la sección "Voz y tono" de `perfil-coni-del-rosario.md`.
2. Corre `python3 scripts/coni.py verificar`. Si falla, detente y explica qué falta con los pasos
   de `GUIA-CLAUDE-CODE-HEYGEN.md`. No intentes renderizar con la configuración incompleta.
3. Anota la ruta de voz de `coni.config.json` (`ruta_voz`): `heygen` (Ruta A) o `elevenlabs` (Ruta B).
4. Solo si vas a programar o hacer el informe: confirma que tienes las herramientas
   `mcp__metricool__*` (si no, pide conectar Metricool con `/mcp`). Si `metricool.marca_id` está en
   `PENDIENTE`, corre `get_brand_settings`, muestra las marcas y pregunta cuál es la de Coni.
   Anota su ID en `coni.config.json`.

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
(por ejemplo: "renderiza sin preguntarme"). Esa excepción nunca alcanza a la segunda puerta:
programar en Instagram siempre requiere aprobar el video ya grabado.

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

## 8. Segunda puerta: revisión humana y fecha

Cambia la ficha a `estado: listo para revisar` y entrega:

- La ruta del video y el link `video_page_url` de `render.json`.
- La duración real contra la estimada. Para la pestaña de Reels debe durar entre 5 y 90 segundos.
- El texto final de `publicacion.md`.
- Qué revisar al verlo: sincronía de labios, pronunciación de nombres, cortes raros y subtítulos.

Después pregunta si lo aprueban para Instagram y para qué día y hora. Si Metricool está conectado,
puedes sugerir horarios con `get_best_time_to_post_by_network`.

- Un "ok" al video **no** aprueba una fecha. Necesitas las dos cosas explícitas, por ejemplo:
  "sí, prográmalo el martes a las 10".
- Si no quieren programar, el flujo termina aquí y una persona publica a mano.

## 9. Programar en Instagram (Metricool)

Solo con la aprobación explícita del paso 8.

1. **Link fresco del video.** Los links de HeyGen vencen, así que pide uno nuevo justo antes:
   `heygen video get <video_id>`. Si `subtitulos_quemados` es `true` y viene `data.captioned_video_url`,
   usa ese; si no, `data.video_url`.
2. **Texto.** Usa la sección Instagram de `publicacion.md` tal cual, con el aviso de avatar digital
   y los hashtags.
3. **Programa una sola vez** con `create_scheduled_post`:
   - `blog_id`: `metricool.marca_id`.
   - Red: **solo Instagram**, en formato **Reel**. Usa las opciones de Instagram de la herramienta;
     nada de "Trial Reels" salvo que lo pidan.
   - `media`: el link del punto 1.
   - `text`: el del punto 2.
   - `date`: la fecha aprobada, que debe estar al menos 15 minutos en el futuro. Si piden "ahora",
     usa 15 minutos desde ahora y avísalo.
   - `timezone`: `metricool.zona_horaria`.
   - Si la herramienta ofrece marcar el contenido como hecho con IA, actívalo.
4. **Si falla**, antes de reintentar revisa `get_scheduled_posts`: la herramienta no es idempotente
   y un reintento a ciegas duplica la publicación.
5. **Anota en la ficha** la fecha programada, el ID de la publicación y el `plannerUrl`, y cambia el
   estado a `programado`.
6. **Entrega el `plannerUrl`** y pide que confirmen en el calendario de Metricool que el video se ve
   bien. Así se comprueba que Metricool guardó su propia copia del video.

Cambios posteriores: `update_scheduled_post`, solo con aprobación. Para cancelar, una persona borra
la publicación desde el calendario de Metricool, porque el conector no permite borrar.

## Informe (modo `informe`)

1. Las fichas en `programado` cuya fecha ya pasó y que no aparecen en `get_scheduled_posts` pasan
   a `publicado`.
2. Busca las métricas de Instagram disponibles con `get_analytics_available_metrics` y trae las de
   los últimos 7 días con `get_analytics_data_by_metrics`: alcance, reproducciones, tiempo promedio
   de reproducción, guardados, compartidos, visitas al perfil y clics en el link, según existan.
3. Escribe `contenido/informes/AAAA-MM-DD.md`:
   - Una tabla por video.
   - Tres aprendizajes concretos.
   - Tres temas propuestos para la semana, de pilares distintos.
   No inventes números: si una métrica no está disponible, dilo.
4. Muestra el resumen y pregunta qué temas quiere Coni. Con su respuesta, sigue en modo `semana`.

## Herramientas

- El render usa la **CLI `heygen`** porque permite video directo con el guion exacto, en 9:16 y más
  barato por segundo que Video Agent. Si una opción no te calza, `heygen <grupo> <acción> --help` y
  `heygen video create --request-schema` son la referencia; no uses los endpoints v1/v2.
- El **MCP de HeyGen** (herramientas `mcp__heygen__*`), si está conectado, sirve para explorar
  (listar avatares y voces) y para Video Agent. No lo mezcles con la CLI dentro del mismo video.
- El **MCP de Metricool** (herramientas `mcp__metricool__*`) sirve para programar en Instagram y leer
  estadísticas. Las de lectura no piden permiso; `create_scheduled_post` y `update_scheduled_post`
  sí, y solo se usan después de la segunda puerta.
- Nunca leas `.env` ni muestres llaves. La CLI guarda su credencial con `heygen auth login`, y
  Metricool usa OAuth.
