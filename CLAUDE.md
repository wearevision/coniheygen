# Proyecto: avatar digital de Coni del Rosario

Coni del Rosario es psicóloga clínica y sexóloga chilena (perfil en `perfil-coni-del-rosario.md`).
Este repo tiene dos partes:

1. **El curso** (`curso-heygen.html`, publicado en Vercel con `scripts/build.sh`): enseña a Coni a
   crear su gemelo digital en HeyGen y a conectar su voz de ElevenLabs.
2. **La producción de contenido**: Claude Code escribe guiones con la voz de Coni y los manda a
   grabar a su avatar en HeyGen. Se usa con la skill `/reel-coni`.

## Mapa de la producción

| Pieza | Archivo |
|---|---|
| Flujo paso a paso del agente | `.claude/skills/reel-coni/SKILL.md` |
| Pilares, tono y reglas editoriales | `contenido/linea-editorial.md` |
| IDs del avatar y de la voz, formato del video | `coni.config.json` |
| Verificar conexión, armar pedidos, generar voz, esperar renders | `scripts/coni.py` |
| Un video = una carpeta | `contenido/AAAA-MM-DD-tema/` |
| Guía para humanos | `GUIA-CLAUDE-CODE-HEYGEN.md` |

## Reglas

- **Dos puertas humanas.** No se gastan créditos sin un guion aprobado, y ningún video se publica
  sin que una persona lo vea. Claude nunca publica en redes.
- **Voz de Coni, no la tuya.** Todo guion sigue `contenido/linea-editorial.md`: tú, español de Chile,
  encuadre educativo, sin diagnósticos, sin anécdotas de pacientes y sin datos inventados.
- **Transparencia.** Cada video y cada publicación dicen que es un avatar digital.
- **Llaves fuera del repo.** La de HeyGen vive en `heygen auth login`; la de ElevenLabs en `.env`
  (ignorado por git). Nunca las leas, las imprimas ni las pegues en archivos versionados.
- **HeyGen solo por v3.** Usa la CLI `heygen` (o el MCP de HeyGen para explorar). Nada de endpoints v1/v2.
- Los `.mp4` y `.mp3` no se suben a git; quedan en HeyGen y en el disco local.

## Comandos útiles

```
python3 scripts/coni.py verificar            # ¿está todo conectado?
heygen avatar list --ownership private       # grupos de avatar propios
heygen avatar looks list --group-id <id>     # looks de un grupo (su id es el avatar_id)
heygen voice list --type private             # voces propias, incluida la de ElevenLabs
sh scripts/build.sh                          # arma public/index.html del curso
```
