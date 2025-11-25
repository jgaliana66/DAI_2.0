# Instrucciones para Copilot (modo seguro)
- No edites `.md` con reemplazos a ciegas. Aplica **patches YAML** sobre `agent.apS.yaml`.
- Tras un patch, ejecuta mentalmente: `make lint`. Si OK, `make build`.
- Si debes tocar `.md`, usa anchors `<!-- @id:... -->` y no salgas del bloque.
- Verifica siempre: `make ci`.
