````markdown
# 🧠 SWARM J2C — APS v4.0 Pipeline de Agentes Especializados Secuenciales
**Contexto funcional para GitHub Copilot**

El proyecto **SWARM J2C** es un sistema de agentes para **Journey to Cloud** con pipeline APS v4.0 de 5 agentes especializados secuenciales para procesamiento de archivos SwarmBuilder JSON.

---

## 🎯 Objetivo general

Procesar archivos SwarmBuilder JSON mediante pipeline de 5 fases especializadas:
- **FASE 1**: Extracción de goals desde JSON → archivos `.md`
- **FASE 2**: Conversión mecánica `.md` → `.yaml` con placeholders
- **FASE 3**: Enriquecimiento semántico 100% LLM (sin código)
- **FASE 4**: Validación de YAMLs contra reglas APS v3.5
- **FASE 5**: Generación de reporte consolidado maestro

**Metodología**: APS v3.5 (Agent Prompting Specification)

---

## ⚙️ Principios clave

- **5 agentes especializados secuenciales**: Cada fase se ejecuta para TODOS los archivos antes de avanzar (batch-by-phase)
- **NO subagentes ni delegación**: Orquestador carga instrucciones secuencialmente
- **FASE 3 es 100% LLM**: Razonamiento lingüístico puro, sin ejecución de código
- **Fuente de verdad**: Archivos `.md` en `swarm/agents/{batch}/` (goals extraídos)
- **YAMLs enriquecidos**: Salida final con SIDs semánticos y metadatos de confianza
- **Pipeline determinístico**: Mismo JSON → misma estructura de salida

---

## 🛠️ Pipeline APS v4.0 (Uso con alias)

```bash
# Invocar pipeline completo
@yaml-pipeline swarm/json/J2C-v1-Swarm-v3-5.json

# El orquestador ejecutará secuencialmente:
# FASE 1: 01-json-extractor.agent.md
# FASE 2: 02-md2yaml-converter.agent.md
# FASE 3: 03-semantic-enricher.agent.md (100% LLM)
# FASE 4: 04-yaml-validator.agent.md
# FASE 5: 05-report-generator.agent.md
```

**Resultado**: 
- Archivos `.md` en `swarm/agents/{batch}/`
- YAMLs enriquecidos en `swarm/agents/{batch}/`
- Reportes individuales en `swarm/reports/validation/`
- Reporte consolidado maestro en `swarm/reports/validation/{batch}_CONSOLIDADO_FINAL_{timestamp}.md`

---

## 🧩 Rol de Copilot

> **Tu función es asistir en la ejecución del pipeline APS v4.0, respetando la especialización y secuencialidad de las fases.**

**DO:**
- ✅ Usar alias `@yaml-pipeline` para invocar el orquestador completo
- ✅ Invocar agentes individuales standalone con sus `.prompt.md` si se requiere una sola fase
- ✅ Respetar el orden secuencial (FASE 1→2→3→4→5)
- ✅ Completar TODOS los archivos en cada fase antes de avanzar (batch-by-phase)
- ✅ En FASE 3: usar 100% razonamiento lingüístico para enriquecimiento semántico
- ✅ Consultar `.github/agents/yaml-pipeline-v4/README.md` para detalles de cada agente
- ✅ Validar YAMLs contra reglas APS v3.5 (`aps-tooling/schemas/`)

**DON'T:**
- ❌ Ejecutar fases fuera de orden o en paralelo
- ❌ Procesar archivos file-by-file a través de todas las fases (prohibido)
- ❌ Usar subagentes o mecanismos de delegación
- ❌ Ejecutar código Python en FASE 3 (debe ser 100% LLM linguistic reasoning)
- ❌ Modificar SIDs manualmente o saltear campos de confianza
- ❌ Continuar pipeline si una fase falla (detener inmediatamente)

---

## 📚 Recursos

**Agentes y Prompts (v4.0)**:
- `.github/agents/yaml-pipeline-v4/` - 5 agentes especializados (`.agent.md`)
- `.github/prompts/yaml-pipeline-v4/` - Orquestador + 5 prompts standalone (`.prompt.md`)
- `.github/copilot-instructions.md` - Alias `@yaml-pipeline` configurado

**Documentación APS**:
- `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md` - Metodología completa
- `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md` - Estrategia v4.0
- `APS/YAML_PIPELINE_README.md` - Guía técnica del pipeline

**Tooling**:
- `aps-tooling/scripts/md2yaml.py` - Conversión mecánica (FASE 2)
- `aps-tooling/scripts/yaml_lint_v6_semantic.py` - Validador (FASE 4)
- `aps-tooling/schemas/sid_vocabulary_v1.yaml` - Vocabulario semántico (FASE 3)

**Legacy**:
- `.github/agents/legacy/yaml-pipeline-v3.2.0-monolithic.md` - Pipeline anterior (deprecated)

---

## 🏗️ Arquitectura APS v4.0

```
SwarmBuilder JSON (input)
    ↓
FASE 1: JSON Goal Extractor
    ↓ (TODOS los .md creados)
FASE 2: MD2YAML Converter (mechanical)
    ↓ (TODOS los .yaml con placeholders <<PENDING_AI>>)
FASE 3: Semantic Enricher (100% LLM)
    ↓ (TODOS los .yaml con SIDs semánticos + confidence)
FASE 4: YAML Validator
    ↓ (TODOS validados → reportes individuales)
FASE 5: Report Generator
    ↓ (Reporte consolidado maestro)
Outputs: .md, .yaml, reports (PASSED/WARNINGS/FAILED)
```

**Aislamiento de fases**: Cada fase se completa para TODOS los archivos antes de avanzar (batch-by-phase).

---

## 🎯 Agentes Especializados

| Fase | Agente | Responsabilidad | Output |
|------|--------|----------------|---------|
| 1 | `01-json-extractor` | Extraer goals desde JSON | `*.md` (goals puros) |
| 2 | `02-md2yaml-converter` | Convertir MD → YAML mecánicamente | `*.yaml` (placeholders) |
| 3 | `03-semantic-enricher` | Enriquecer semánticamente (100% LLM) | `*.yaml` (SIDs + confianza) |
| 4 | `04-yaml-validator` | Validar contra APS v3.5 | Reportes individuales |
| 5 | `05-report-generator` | Consolidar resultados | Reporte maestro |

**Invocación**:
- **Completa**: `@yaml-pipeline path/to/file.json` (orquestador ejecuta las 5 fases)
- **Individual**: Cargar `.github/prompts/yaml-pipeline-v4/0X-{nombre}.prompt.md` (fase específica)

---

**Framework:** SWARM J2C · **Versión:** APS v4.0 · **Última actualización:** 2025-11-21  
**Metodología:** APS v3.5 (Agent Prompting Specification)  
© 2025 Recursos en la Red

````
