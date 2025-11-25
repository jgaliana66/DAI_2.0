# Preamble — Guardarraíles para Copilot
A partir de ahora, cuando pida cambios en el SWARM J2C:
- ❌ Prohibido usar `grep/sed/perl -pe/ed` para editar `.md`.
- ✅ Cambios estructurales SOLO via **patch** sobre `swarm/agents/<id>/agent.apS.yaml` (IDs o SIDs).
- ✅ Después de cada patch: `make lint` (si falla, no renderices MD).
- ✅ Si lint OK: `make build` para re-generar `.md` y sincronizar `swarm.json`.
- ⚠️ Excepción: si debes tocar `.md`, edita únicamente el contenido entre anchors `<!-- @id:... --> ... <!-- /@id:... -->`.
- 🧪 Muestra siempre un diff previo con 3 líneas de contexto; si el diff toca más de un bloque, ABORTA.
