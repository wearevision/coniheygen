# Contenido

Cada video es una carpeta con fecha y tema, por ejemplo `2026-09-29-celos/`:

```
2026-09-29-celos/
├── ficha.md        tema, pilar, formato, estado e IDs de HeyGen
├── guion.txt       solo lo que dice el avatar (la versión aprobada)
├── publicacion.md  texto para Instagram/TikTok y para LinkedIn
├── pedido.json     lo que se le pidió a HeyGen (se genera solo)
├── render.json     la respuesta final de HeyGen, con los links (se genera solo)
├── voz.mp3         solo en la Ruta B · no se sube a git
└── video.mp4       el video final · no se sube a git
```

Estados de la ficha, en orden:

`idea` → `guion por aprobar` → `aprobado` → `en render` → `listo para revisar` → `publicado`

Solo una persona cambia un video de `listo para revisar` a `publicado`, y lo publica a mano.

`linea-editorial.md` es el brief permanente: pilares, tono y reglas. El agente lo lee antes de cada guion.
