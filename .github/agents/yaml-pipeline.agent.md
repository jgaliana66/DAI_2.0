---
name: "yaml-pipeline"
description: "APS v4.0 YAML Pipeline – Orquesta 5 agentes secuenciales especializados para procesar archivos JSON de SwarmBuilder."
version: "4.0.0"
model: gpt-4o
tools: []
---

# APS v4.0 – YAML Pipeline Orchestrator

Ejecuta el **pipeline APS v4.0 completo** sobre un archivo SwarmBuilder JSON (abierto, adjunto o indicado por ruta).

## 🧩 Instrucciones de Ejecución

1. **Identifica el archivo JSON** proporcionado por el usuario  
2. **Ejecuta las 5 fases secuencialmente (batch-by-phase):**
   - **FASE 1** — Extrae el _goal_ → `.md`  
     _Carga:_ `.github/agents/01-json-extractor.agent.md`
   - **FASE 2** — Convierte `.md` → `.yaml`  
     _Carga:_ `.github/agents/02-md2yaml-converter.agent.md`
   - **FASE 3** — Enriquecimiento semántico (SID + atributos)  
     _Carga:_ `.github/agents/03-semantic-enricher.agent.md`  
     ⚠ **100% razonamiento lingüístico (NO código)**  
   - **FASE 4** — Validación de YAMLs  
     _Carga:_ `.github/agents/04-yaml-validator.agent.md`
   - **FASE 5** — Reporte consolidado final  
     _Carga:_ `.github/agents/05-report-generator.agent.md`
3. **IMPORTANTE**: Presenta un resumen de cada fase antes de continuar con la siguiente
4. **NO saltees fases**; el orden de ejecución es estricto

## ⚠️ Restricciones de Ejecución

- **Carga secuencial**: Cada fase termina antes de pasar a la siguiente  
- **NO delegación**: El orquestador ejecuta las instrucciones de cada agente directamente (no crea subagentes ni transfiere el control)  
- **NO paralelización**: Completa todos los archivos en cada fase antes de avanzar  
- **Procesamiento batch-by-phase**: NUNCA proceses archivo por archivo a través de todas las fases

---

## 📚 Referencias internas

- `.github/prompts/ORCHESTRATOR.md`
- `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md`
- `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`

---

## ▶️ Inicio

Comienza ejecutando **FASE 1**.
