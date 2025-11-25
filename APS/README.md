# APS v3.5 - Documentación del Pipeline YAML

Esta carpeta contiene toda la documentación relacionada con el sistema de procesamiento YAML para agentes SWARM bajo el estándar APS v3.5.

## 📚 Índice de Documentos

### 1. Metodología y Contexto APS v3.5
**[METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md](METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md)**
- Por qué existe APS v3.5
- Filosofía MD-first (`.md` como fuente de verdad)
- Evolución AS-IS → TO-BE
- Gap entre edición y validación
- Arquitectura modular (schemas, profiles, templates)
- Buenas prácticas y contrato para IA/Copilot
- **Sección 15**: Implementación de APS vía YAML Pipeline ⭐
- **Lee esto primero** para entender el contexto completo

---

### 2. Guía de Usuario Principal
**[YAML_PIPELINE_README.md](YAML_PIPELINE_README.md)**
- Contexto APS v3.5 y relación con metodología ⭐
- Quick start guide
- Estructura del proyecto
- Instalación y uso
- Ejemplos prácticos
- Troubleshooting
- **Empieza aquí** si quieres usar el pipeline directamente

---

### 3. Especificación Completa del Agente
**[AGENTE_YAML_PIPELINE.md](AGENTE_YAML_PIPELINE.md)** (1900+ líneas)
- **⚠️ ESTÁNDAR OFICIAL**: AST para manipulación YAML ⭐
- Identidad y rol del agente `@yaml-pipeline`
- Workflow detallado (4 fases)
- Sistema de confianza semántica
- DENY_TERMS contextual
- Validación de seguridad
- Integración con Makefile
- Modo batch y CI/CD
- Reglas centralizadas (APS v3.5+)
- Best practice: Manipulación YAML mediante AST
- **Referencia técnica completa**

---

### 4. Reglas del Linter (Documentación Unificada) ⭐ NUEVO
**[LINTER_RULES.md](LINTER_RULES.md)**
- Reglas estructurales (formato SID, unicidad, claves obligatorias)
- Reglas de contenido (DENY_TERMS, bloques obligatorios)
- Códigos de error y severidades (ERROR/WARNING/INFO)
- Políticas de detección contextual
- Agentes exentos
- Evolución de reglas y versionado
- FAQ y troubleshooting
- **Referencia completa de validación**

---

### 5. Migración a Reglas Centralizadas
**[MIGRATION_RULES_CENTRALIZATION.md](MIGRATION_RULES_CENTRALIZATION.md)**
- Problema: reglas dispersas en múltiples archivos
- Solución: fuente de verdad única (`aps_v3.5_rules.yaml`)
- Plan de migración en 4 fases
- Comparación antes/después
- Checklist de tareas
- Herramientas de validación
- **Esencial para actualizar a APS v3.6+**

---

### 6. Best Practice: Manipulación YAML
**[YAML_AST_BEST_PRACTICE.md](YAML_AST_BEST_PRACTICE.md)**
- Por qué string-replace es frágil
- Qué significa "parsear YAML a AST (dict)"
- Cómo funciona el flujo con AST
- Diferencia práctica entre string-replace y AST
- Cuándo usar string-replace (excepciones)
- Implementación de `YAMLBlockEditor` class
- **Guía técnica para manipulación robusta de YAML**

---

### 7. Roadmap de Mejoras ⭐ NUEVO
**[ROADMAP.md](ROADMAP.md)**
- Estado de implementación (40% completado)
- Mejoras ya implementadas en v2.0
- Mejoras esenciales inmediatas (DEBE)
- Mejoras esenciales corto plazo (SHOULD)
- Mejoras recomendadas (COULD)
- Cronograma sugerido (Sprints 1-3)
- **Planificación y priorización**

---

### 8. Esquemas y Vocabularios (aps-tooling/schemas/)

#### 8.1. Reglas Centralizadas APS v3.5
**`aps-tooling/schemas/aps_v3.5_rules.yaml`**
- Fuente de verdad canónica para todas las reglas
- Secciones: required_blocks, antipatterns, vocabulary, heuristics, protocols
- Leído por `yaml_lint_v2.py`
- Versionado: v3.5

#### 8.2. Vocabulario de SIDs ⭐ NUEVO
**`aps-tooling/schemas/sid_vocabulary_v1.yaml`**
- 35 acciones permitidas (verificar, capturar, generar, etc.)
- 24 relaciones permitidas (control.active_agent, usuario.confirmacion, etc.)
- 13 niveles permitidos (guard, workflow, protocol, etc.)
- Política de evolución (agregar, deprecar, versionar)
- Sistema de confianza HIGH/MEDIUM/LOW
- Mapeo de sinónimos
- **Referencia canónica de términos**

---

## 🎯 Flujos de Trabajo Recomendados

### Nuevo Usuario
1. Lee [`METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`](METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md) → Contexto y filosofía APS
2. Lee [`YAML_PIPELINE_README.md`](YAML_PIPELINE_README.md) → Quick start práctico
3. Prueba modo interactivo: `@yaml-pipeline archivo.md`
4. Revisa [`ROADMAP.md`](ROADMAP.md) → Qué está implementado y qué viene
5. Consulta [`LINTER_RULES.md`](LINTER_RULES.md) si hay errores de validación

### Desarrollador del Pipeline
1. Lee [`AGENTE_YAML_PIPELINE.md`](AGENTE_YAML_PIPELINE.md) → Especificación completa (⚠️ AST oficial)
2. Lee [`YAML_AST_BEST_PRACTICE.md`](YAML_AST_BEST_PRACTICE.md) → Evita string-replace
3. Consulta [`aps-tooling/schemas/sid_vocabulary_v1.yaml`](../aps-tooling/schemas/sid_vocabulary_v1.yaml) → Vocabulario permitido
4. Consulta [`LINTER_RULES.md`](LINTER_RULES.md) → Semántica de reglas y códigos de error
5. Implementa usando `yaml.safe_load()` + modificaciones dict + `yaml.safe_dump()`

### Actualización a APS v3.6
1. Lee [`MIGRATION_RULES_CENTRALIZATION.md`](MIGRATION_RULES_CENTRALIZATION.md)
2. Copia `swarm/schemas/aps_v3.5_rules.yaml` → `aps_v3.6_rules.yaml`
3. Copia `swarm/schemas/sid_vocabulary_v1.yaml` → `sid_vocabulary_v2.yaml`
4. Modifica SOLO los nuevos schemas (versión, nuevas reglas)
5. Actualiza linter para leer v3.6
6. Todos los scripts se actualizan automáticamente

### CI/CD Integration
1. Lee [`YAML_PIPELINE_README.md`](YAML_PIPELINE_README.md) → Sección "Modo Batch CI/CD"
2. Copia `.github/workflows/yaml-pipeline-ci.yml`
3. Ajusta patterns y configuración
4. Push → pipeline automático con exit codes 0-5

### Troubleshooting Validación
1. Consulta [`LINTER_RULES.md`](LINTER_RULES.md) → Códigos de error y severidades
2. Revisa [`swarm/schemas/sid_vocabulary_v1.yaml`](../swarm/schemas/sid_vocabulary_v1.yaml) → Términos permitidos
3. Verifica que usas AST (no string-replace) según [`YAML_AST_BEST_PRACTICE.md`](YAML_AST_BEST_PRACTICE.md)
4. Consulta FAQ en [`LINTER_RULES.md`](LINTER_RULES.md) sección 8

---

## 🗂️ Estructura Relacionada

```
DAI Arquitectura/
├── APS/                                    ← ESTA CARPETA
│   ├── README.md                           ← Este archivo
│   ├── YAML_PIPELINE_README.md             ← Quick start
│   ├── AGENTE_YAML_PIPELINE.md             ← Especificación completa
│   ├── MIGRATION_RULES_CENTRALIZATION.md   ← Migración reglas
│   └── YAML_AST_BEST_PRACTICE.md           ← Best practice manipulación
├── code/
│   ├── md2yaml.py                          ← Conversión MD → YAML
│   ├── yaml_lint.py                        ← Linter (legacy)
│   ├── yaml_lint_v2.py                     ← Linter con reglas centralizadas
│   ├── enrich_yaml_with_llm.py             ← Enriquecimiento
│   └── yaml_pipeline_cli.py                ← CLI batch para CI/CD
├── swarm/
│   ├── agents/                             ← Agentes SWARM
│   └── schemas/
│       └── aps_v3.5_rules.yaml             ← Fuente de verdad canónica
├── .github/workflows/
│   └── yaml-pipeline-ci.yml                ← GitHub Actions workflow
├── Makefile                                ← Targets del pipeline
└── METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md  ← Metodología APS
```

---

## 🔧 Comandos Rápidos

### Validar YAML
```bash
# Linter legacy (reglas hardcoded)
python3 code/yaml_lint.py swarm/agents/archivo.yaml

# Linter v2 (reglas centralizadas)
python3 code/yaml_lint_v2.py swarm/agents/archivo.yaml
```

### Pipeline Interactivo
```bash
# Invocar agente en Copilot Chat
@yaml-pipeline swarm/agents/J2C-v1-Swarm-v3-5/archivo.md

# Desde Makefile (recordatorio)
make agent-pipeline FILE=swarm/agents/.../archivo.md
```

### Pipeline Batch (CI/CD)
```bash
# Modo CI con JSON output
python3 code/yaml_pipeline_cli.py --batch "swarm/agents/**/*.md" --ci-mode

# Desde Makefile
make agent-pipeline-batch PATTERN="swarm/agents/**/*.md"
```

### Ver Reglas APS
```bash
# Inspeccionar fuente de verdad
cat swarm/schemas/aps_v3.5_rules.yaml

# Validar schema YAML
python3 -c "import yaml; yaml.safe_load(open('swarm/schemas/aps_v3.5_rules.yaml'))"
```

---

## 📊 Resumen de Mejoras (v2.0)

| Característica | Estado | Documento |
|---------------|--------|-----------|
| Modo batch CI/CD | ✅ | `YAML_PIPELINE_README.md` |
| Reglas centralizadas | ✅ | `MIGRATION_RULES_CENTRALIZATION.md` + `swarm/schemas/aps_v3.5_rules.yaml` |
| AST manipulation | ✅ | `YAML_AST_BEST_PRACTICE.md` + `AGENTE_YAML_PIPELINE.md` |
| Sistema de confianza | ✅ | `AGENTE_YAML_PIPELINE.md` sección 4.3 |
| DENY_TERMS contextual | ✅ | `AGENTE_YAML_PIPELINE.md` sección 4.4 |
| Validación seguridad | ✅ | `AGENTE_YAML_PIPELINE.md` sección 4.5 |
| GitHub Actions | ✅ | `.github/workflows/yaml-pipeline-ci.yml` |
| **Vocabulario SID** | ✅ | `swarm/schemas/sid_vocabulary_v1.yaml` ⭐ |
| **Reglas unificadas** | ✅ | `LINTER_RULES.md` ⭐ |
| **Roadmap completo** | ✅ | `ROADMAP.md` ⭐ |
| **Enlace APS↔Pipeline** | ✅ | `METODOLOGIA_SWARM` sección 15 ⭐ |

**Progreso v2.0**: 11/11 características implementadas (100%)

### 🔄 Próximas Mejoras (Ver ROADMAP.md)

**Sprint 1 (Inmediato)**:
- Ninguna pendiente - todas las mejoras esenciales implementadas ✅

**Sprint 2 (Corto plazo)**:
- Esquema YAML formal completo con validador automático
- Implementar confianza en código de `enrich_yaml_with_llm.py`

**Sprint 3 (Mejoras)**:
- Unicidad global de SIDs
- Documentar política bloques auto-numerados

---

## 🎓 Conceptos Clave

### APS v3.5
Estándar de arquitectura para agentes SWARM que define:
- Bloques obligatorios (Entry Guard, State JSON, Loop Contract)
- Antipatrones prohibidos (NO-SALTO-AUTOMÁTICO)
- Protocolo de handoff estructurado
- Políticas de recursión y delegación

### SID (Semantic Identifier)
Identificador semántico con formato:
```
<TYPE>.<accion>.<relacion>.<nivel>
Ejemplo: BLK.verificar.control.active_agent.guard
```

### Sistema de Confianza
Clasifica SIDs en:
- **HIGH**: Match exacto en vocabulario canónico
- **MEDIUM**: Patrón heurístico o sinónimo reconocido
- **LOW**: Inferencia semántica sin vocabulario

### AST (Abstract Syntax Tree)
En contexto YAML: estructura de datos Python (dict) obtenida con `yaml.safe_load()`. Permite manipulación robusta sin depender de formato exacto.

---

## 🚀 Próximos Pasos

1. **Si es tu primera vez**: Lee `YAML_PIPELINE_README.md`
2. **Si desarrollas el pipeline**: Lee `AGENTE_YAML_PIPELINE.md` + `YAML_AST_BEST_PRACTICE.md`
3. **Si actualizas a APS v3.6**: Lee `MIGRATION_RULES_CENTRALIZATION.md`
4. **Si integras en CI/CD**: Ver `.github/workflows/yaml-pipeline-ci.yml`

---

**Versión**: 2.0  
**Última actualización**: 2025-11-19  
**Mantenedor**: Sistema SWARM J2C  
**Estado**: ✅ Production Ready
