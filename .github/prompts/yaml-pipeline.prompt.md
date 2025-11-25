---
name: "yaml-pipeline"
description: "APS v4.0 - YAML Pipeline Orchestrator"
agent: "yaml-pipeline"
argument-hint: "Ruta al archivo JSON SwarmBuilder"
---


# APS v4.0 - YAML Pipeline Orchestrator

Ejecuta el pipeline APS v4.0 completo sobre el archivo JSON adjunto/abierto:

## Instrucciones de Ejecución

1. **Identifica el archivo JSON SwarmBuilder** (abierto, adjunto, o ruta especificada)

2. **Ejecuta las 5 fases secuencialmente** en modo batch-by-phase:
   - **FASE 1**: Extrae goal → .md (carga `.github/agents/01-json-extractor.agent.md`)
   - **FASE 2**: Convierte .md → .yaml (carga `.github/agents/02-md2yaml-converter.agent.md`)
   - **FASE 3**: Enriquece semánticamente (carga `.github/agents/03-semantic-enricher.agent.md`) - **100% LLM**
   - **FASE 4**: Valida YAMLs (carga `.github/agents/04-yaml-validator.agent.md`)
   - **FASE 5**: Genera reporte maestro (carga `.github/agents/05-report-generator.agent.md`)

3. **Muestra resumen tras cada fase** antes de continuar

## Restricciones CRÍTICAS

- ❌ **NO subagentes** ni delegación
- ❌ **NO procesamiento file-by-file** (batch completo por fase)
- ✅ **Carga secuencial** de instrucciones (uno por uno)
- ✅ **FASE 3**: 100% razonamiento lingüístico (NO código)

## Archivo de Entrada

**Archivo JSON**: [especificar ruta o "detectar del contexto"]

## Workflow de Ejecución

### FASE 1: JSON Goal Extractor
1. Detectar JSON file del contexto
2. Validar estructura JSON (`agents` field presente)
3. Ejecutar script automatizado:
   ```bash
   python3 aps-tooling/scripts/extract_goals_from_json.py <JSON_PATH> --force
   ```
4. Verificar salida:
   - Carpeta creada: `swarm/agents/{base_name}/`
   - JSON copiado al nuevo folder
   - N archivos `.md` creados (uno por agente)
5. Generar resumen (archivos creados, conteo)

**Criterios de éxito**:
- ✅ N archivos `.md` creados = N agentes en JSON
- ✅ Archivos en `swarm/agents/{base_name}/XX-AgentName.md`
- ✅ Cada archivo contiene SOLO texto goal (sin headers, sin metadata)

---

### FASE 2: MD2YAML Converter
1. Verificar que existe `aps-tooling/scripts/md2yaml.py`
2. Invocar script en modo batch:
   ```bash
   python3 aps-tooling/scripts/md2yaml.py swarm/agents/{base_name}/
   ```
3. Verificar output: count `.yaml` files = count `.md` files
4. Spot check 2-3 archivos YAML para integridad de placeholders (`<<PENDING_AI>>`)
5. Generar resumen (archivos convertidos, success rate)

**Criterios de éxito**:
- ✅ Todas las conversiones `.md` → `.yaml` completas
- ✅ Todos los campos semánticos contienen `<<PENDING_AI>>`
- ✅ SIDs temporales: `TEMP_{block_type}_{NNN}`
- ✅ Exit code 0

---

### FASE 3: Semantic Enricher (100% LLM)
1. Cargar vocabulario: `aps-tooling/schemas/sid_vocabulary_v1.yaml`
2. Para CADA archivo `.yaml`:
   - Leer bloques con placeholders `<<PENDING_AI>>`
   - Analizar campo `content` lingüísticamente
   - Comparar semánticamente con términos del vocabulario
   - Seleccionar mejor match: `accion`, `relacion`, `nivel`
   - Generar SID: `{block_type}.{accion}.{relacion}.{nivel}`
   - Asignar confidence: HIGH/MEDIUM/LOW
   - Documentar razonamiento en `justificacion`
   - Actualizar archivo YAML
3. Manejar batches (sub-batches de 8-10 archivos si >20 total)
4. Generar estadísticas (total enriched, distribución de confidence)

**Criterios de éxito**:
- ✅ Todos los placeholders `<<PENDING_AI>>` reemplazados
- ✅ SIDs siguen convención: `{block_type}.{accion}.{relacion}.{nivel}`
- ✅ Todos los bloques tienen campos `confidence` y `justificacion`
- ✅ NO ejecución de código (100% razonamiento lingüístico)

---

### FASE 4: YAML Validator
1. Verificar que existe `aps-tooling/scripts/yaml_lint_v6_semantic.py`
2. Crear estructura organizada de reportes:
   ```bash
   BATCH_NAME="{base_name}"
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   REPORT_DIR="swarm/reports/validation/${BATCH_NAME}_${TIMESTAMP}"
   mkdir -p "${REPORT_DIR}/individual"
   ```
3. Para CADA archivo `.yaml` enriquecido:
   ```bash
   python3 aps-tooling/scripts/yaml_lint_v6_semantic.py \
     swarm/agents/${BATCH_NAME}/{file}.yaml \
     > "${REPORT_DIR}/individual/{file}_validation.md" 2>&1
   ```
4. Colectar exit codes (0/1/2)
5. Verificar generación de reportes
6. Generar resumen (archivos validados, distribución de exit codes, aggregate de confidence)

**Criterios de éxito**:
- ✅ Directorio organizado creado: `{batch_name}_{timestamp}/`
- ✅ Subdirectorio `individual/` creado
- ✅ Todos los archivos validados (reportes generados)
- ✅ Exit codes colectados: 0 (PASSED), 1 (WARNINGS), 2 (FAILED)
- ✅ Reportes individuales en `${REPORT_DIR}/individual/`

---

### FASE 5: Report Generator
1. Localizar directorio del batch: `swarm/reports/validation/{batch_name}_{timestamp}/`
2. Parsear reportes individuales: `${REPORT_DIR}/individual/*.md`
3. Agregar estadísticas globales
4. Identificar top 5+ patrones de error/warning
5. Analizar distribución de confidence
6. Generar plan de acción (Priority 1/2/3)
7. Escribir reporte consolidado:
   `${REPORT_DIR}/CONSOLIDADO_FINAL.md`
8. Mostrar resumen al usuario

**Criterios de éxito**:
- ✅ Directorio del batch localizado correctamente
- ✅ Reporte consolidado generado en mismo directorio del batch
- ✅ Top N errores identificados (N≥5)
- ✅ Recomendaciones accionables proporcionadas
- ✅ Referencias a documentación APS

---

## Manejo de Errores

**Si cualquier FASE falla**:
1. **DETENER** el pipeline inmediatamente
2. Mostrar mensaje de error con:
   - Qué FASE falló (1-5)
   - Qué error ocurrió
   - Qué archivo causó el error (si aplica)
3. Proporcionar guía de troubleshooting:
   - FASE 1: Revisar estructura JSON, file path
   - FASE 2: Revisar script md2yaml.py, Python environment
   - FASE 3: Revisar archivo vocabulary, parseabilidad YAML
   - FASE 4: Revisar script validator, archivos de reglas
   - FASE 5: Revisar que existan reportes individuales

**NO hacer**:
- ❌ Continuar a siguiente FASE después de error
- ❌ Silenciosamente saltear archivos fallidos
- ❌ Generar resultados parciales sin advertencia

---

## Resumen Final

Después de completar FASE 5, mostrar:

```
✅ APS v4 Pipeline Completed

Batch: {base_name}
Files processed: {count}

Phase Results:
  FASE 1: {n} .md files extracted
  FASE 2: {n} .yaml files converted
  FASE 3: {n} blocks enriched (HIGH: {h}%, MEDIUM: {m}%, LOW: {l}%)
  FASE 4: {n} files validated (PASSED: {p}, WARNINGS: {w}, FAILED: {f})
  FASE 5: Consolidated report generated

📊 Final Report:
swarm/reports/validation/{batch}_{timestamp}/CONSOLIDADO_FINAL.md

📁 Output Files:
- Markdown goals: swarm/agents/{base_name}/*.md
- Enriched YAMLs: swarm/agents/{base_name}/*.yaml
- Validation reports: swarm/reports/validation/{batch}_{timestamp}/
  - Individual reports: individual/*.md
  - Consolidated report: CONSOLIDADO_FINAL.md

Next Steps:
{action plan based on FASE 5 report}
```

---

## Referencias

- **Documentación completa**: `.github/prompts/ORCHESTRATOR.md`
- **Estrategia**: `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md`
- **Metodología**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Agentes**: `.github/agents/01-05-*.agent.md`

---

**Versión**: 4.0.0  
**Fecha**: 2025-11-21  
**Alias**: `@yaml-pipeline`

Comienza con FASE 1.
