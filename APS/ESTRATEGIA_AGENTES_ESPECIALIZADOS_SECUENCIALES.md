# Especificación: Arquitectura de Agentes Especializados APS v3.5

**Versión**: 1.0  
**Fecha**: 2025-11-20  
**Estado**: Especificación Normativa  
**Ámbito**: Pipeline YAML para agentes APS v3.5

---

## 📋 Contexto y Motivación

El agente monolítico **yaml-pipeline.md** ejecuta 4 fases en un único contexto:
1. Conversión MD → YAML
2. Enriquecimiento semántico
3. Validación semántica
4. Generación de reportes

**Problemas identificados**:
- ❌ Mantenimiento complejo (>300 líneas, múltiples responsabilidades)
- ❌ Ausencia de reutilización (imposible ejecutar fases individuales)
- ❌ Violación del principio de responsabilidad única
- ❌ Dificultad para evolución incremental de cada fase

---

## ✅ Arquitectura Propuesta: 5 Agentes Especializados

### Estructura Obligatoria:

```
swarm/agents/yaml-pipeline/
├── 01-json-extractor.md               # FASE 1: Extracción JSON → MD
├── 02-md2yaml-converter.md            # FASE 2: Conversión MD → YAML
├── 03-semantic-enricher.md            # FASE 3: Enriquecimiento semántico
├── 04-yaml-validator.md               # FASE 4: Validación semántica
└── 05-report-generator.md             # FASE 5: Reportes consolidados

# El orquestador NO es un agente, sino un PROMPT/ALIAS reutilizable
# Se almacena como:
.github/copilot-instructions.md         # Prompt orquestador como alias
```

**Nota importante**: El orquestador es un **prompt maestro** que coordina la ejecución de las 5 fases, no un archivo `.md` de agente. Se define como un **alias de Copilot** o **instrucción reutilizable**.

### Principio Fundamental de Ejecución por Fases

**En modo BATCH, el pipeline DEBE operar SIEMPRE así**:

```
FASE 1: Extracción del JSON → TODOS los archivos .md individuales
   ↓
FASE 2: Conversión de TODOS los archivos .md → .yaml
   ↓
FASE 3: Enriquecimiento semántico de TODOS los .yaml
   ↓
FASE 4: Validación semántica de TODOS los .yaml enriquecidos
   ↓
FASE 5: Generación de reporte consolidado único
```

**ESTÁ PROHIBIDO**:
- Procesar archivo por archivo ejecutando las 5 fases para cada uno
- Intercalar fases (ej: extraer agente 1, convertirlo, validarlo, luego extraer agente 2)
- Procesar parcialmente un lote y generar reportes intermedios fuera de FASE 5

---

## 🎯 Especificación de Agentes Especializados

### FASE 1 – 01-json-extractor.md

**Responsabilidad única**: Extracción **EXCLUSIVA** del atributo `goal` desde JSON SwarmBuilder a archivos `.md` individuales

**Entrada**:
- Ruta a archivo JSON de definición de swarm (ej: `swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json`)
- Directorio de salida para archivos `.md` individuales

**Salida**:
- N archivos `.md` individuales (uno por agente definido en el JSON)
- Nomenclatura: `{NN}-{agentName}.md` (ej: `01-J2Ci-Orchestrator.md`)
- **Contenido de cada archivo**: ÚNICAMENTE el valor del atributo `goal` (texto plano, sin encabezados, sin metadata)

**Herramientas autorizadas**:
- Lectura de archivos JSON
- Escritura de archivos Markdown con encoding UTF-8
- Análisis de estructura JSON mediante capacidades nativas del LLM

**Criterios de éxito obligatorios**:
- ✅ Todos los agentes del JSON extraídos a archivos `.md` individuales
- ✅ Nombres de archivo numerados secuencialmente (01, 02, 03...)
- ✅ Contenido `goal` preservado exactamente como aparece en JSON
- ✅ Archivos generados en el directorio especificado
- ✅ **Cada archivo .md contiene SOLO el texto del `goal`, sin ningún añadido**

**Prohibiciones explícitas**:
- 🚫 NO DEBE extraer otros atributos del JSON (`instructions`, `context`, `description`, `tools`, etc.)
- 🚫 NO DEBE añadir encabezados, títulos o formato al contenido del `goal` (como "# Goal" o "## Objetivo")
- 🚫 NO DEBE incluir metadata del agente (nombre, ID, versión) dentro del archivo .md
- 🚫 NO DEBE modificar, reformatear o interpretar el texto del `goal`
- 🚫 NO DEBE convertir a YAML (responsabilidad de FASE 2)
- 🚫 NO DEBE enriquecer semánticamente (responsabilidad de FASE 3)
- 🚫 NO DEBE validar contenido (responsabilidad de FASE 4)
- 🚫 NO DEBE crear scripts externos o módulos de extracción
- 🚫 NO DEBE procesar agentes selectivamente (TODOS los agentes del JSON)

**Ejemplo de extracción correcta**:

**JSON de entrada**:
```json
{
  "agents": [
    {
      "name": "Orchestrator",
      "description": "Coordina el flujo de trabajo",
      "goal": "Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.",
      "instructions": "...",
      "context": "..."
    }
  ]
}
```

**Archivo generado** (`01-Orchestrator.md`):
```
Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.
```

❌ **INCORRECTO** (incluye encabezado):
```markdown
# Goal
Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.
```

❌ **INCORRECTO** (incluye metadata):
```markdown
**Agent**: Orchestrator
**Goal**: Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.
```

---

### FASE 2 – 02-md2yaml-converter.md

**Responsabilidad única**: Conversión **MECÁNICA** de archivos `.md` a `.yaml` con estructura APS v3.5 y placeholders

**Entrada**:
- Ruta(s) a archivo(s) `.md` con definiciones de agentes
- Directorio de salida para archivos `.yaml`

**Salida**:
- Archivos `.yaml` con estructura APS v3.5 válida
- **Todos los campos semánticos con placeholder `<<PENDING_AI>>`** (sin inferencia)
- Log de conversión (archivos procesados, errores)

**Herramientas autorizadas**:
- `aps-tooling/scripts/md2yaml.py` (ÚNICO script permitido)
- Operaciones de lectura/escritura de archivos del sistema

**Criterios de éxito obligatorios**:
- ✅ Todos los archivos `.md` del lote convertidos a `.yaml`
- ✅ Estructura YAML válida (parseable por PyYAML)
- ✅ Bloques identificados correctamente (GOAL, BLK, INS, POL, OUT, LOOP, etc.)
- ✅ **TODOS** los campos semánticos con placeholder `<<PENDING_AI>>`: `accion`, `relacion`, `nivel`, `sid`
- ✅ **Ningún campo semántico debe contener valores inferidos** (ni siquiera parcialmente)

**Prohibiciones explícitas**:
- 🚫 NO DEBE realizar inferencia semántica (ni total ni parcial) - responsabilidad EXCLUSIVA de FASE 3
- 🚫 NO DEBE intentar deducir acciones, relaciones o niveles desde el texto del goal
- 🚫 NO DEBE generar SIDs preliminares, temporales o aproximados
- 🚫 NO DEBE usar vocabularios, sinónimos o heurísticas semánticas
- 🚫 NO DEBE validar SIDs (responsabilidad de FASE 4)
- 🚫 NO DEBE generar reportes (responsabilidad de FASE 5)
- 🚫 NO DEBE crear scripts nuevos, módulos Python o herramientas auxiliares
- 🚫 NO DEBE mencionar tokens, límites de contexto u optimizaciones del modelo
- 🚫 NO DEBE invocar otros agentes ni cambiar su identidad

**Ejemplo de conversión correcta (FASE 2)**:

**Archivo MD de entrada** (`01-Orchestrator.md`):
```
Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.
```

**Archivo YAML generado** (`01-Orchestrator.yaml`):
```yaml
GOAL:
  meta:
    accion: <<PENDING_AI>>
    relacion: <<PENDING_AI>>
    nivel: <<PENDING_AI>>
    sid: <<PENDING_AI>>
  descripcion: "Analizar requisitos del usuario y coordinar la ejecución de agentes especializados."
```

❌ **INCORRECTO** (incluye inferencia semántica):
```yaml
GOAL:
  meta:
    accion: analizar  # ❌ Esto es inferencia - PROHIBIDO en FASE 2
    relacion: control
    nivel: workflow
    sid: GOAL.analizar.control.workflow
  descripcion: "Analizar requisitos del usuario y coordinar la ejecución de agentes especializados."
```

---

### FASE 3 – 03-semantic-enricher.md

**Responsabilidad única**: Enriquecimiento de archivos `.yaml` con metadatos semánticos (SIDs) mediante análisis lingüístico puro

**Entrada**:
- Ruta(s) a archivo(s) `.yaml` con placeholders `<<PENDING_AI>>`
- Vocabulario SID (`aps-tooling/schemas/sid_vocabulary_v1.yaml`)

**Salida**:
- Archivos `.yaml` con campos semánticos completados:
  - `accion`: verbo canónico del vocabulario
  - `relacion`: relación semántica
  - `nivel`: nivel de abstracción
  - `sid`: identificador único generado (`BLK.accion.relacion.nivel`)
  - `confidence`: nivel de confianza (HIGH/MEDIUM/LOW)
  - `justificacion`: razonamiento de la inferencia

**Herramientas autorizadas**:
- Lectura de `aps-tooling/schemas/sid_vocabulary_v1.yaml`
- Lectura y escritura de archivos YAML
- Análisis semántico mediante razonamiento lingüístico del LLM

**Naturaleza del Proceso de Enriquecimiento**:

El enriquecimiento semántico es un proceso **100% lingüístico y semántico** realizado por el LLM.
**NO** involucra:
- Ejecución de código Python
- Interpretación de pseudocódigo
- Aplicación de algoritmos programáticos
- Procesamiento mediante funciones o heurísticas basadas en código
- Manipulación de estructuras de datos mediante programación

El agente **DEBE** aplicar razonamiento natural basado en:
- Comprensión semántica del texto en `descripcion`
- Comparación lingüística con términos del vocabulario SID
- Inferencia contextual del propósito del bloque
- Análisis de patrones de lenguaje natural

**Criterios de éxito obligatorios**:
- ✅ Todos los placeholders `<<PENDING_AI>>` reemplazados en todos los archivos
- ✅ SIDs generados siguiendo convención `{block_type}.{accion}.{relacion}.{nivel}`
- ✅ Campo `confidence` asignado (HIGH/MEDIUM/LOW) a cada bloque
- ✅ Campo `justificacion` documentado con razonamiento lingüístico de la inferencia

**Prohibiciones explícitas**:
- 🚫 NO DEBE ejecutar código, scripts o funciones Python
- 🚫 NO DEBE interpretar pseudocódigo como instrucciones ejecutables
- 🚫 NO DEBE aplicar algoritmos programáticos o heurísticas basadas en código
- 🚫 NO DEBE simular funciones o procesar datos mediante lógica programática
- 🚫 NO DEBE generar código inline, temporal o auxiliar para inferencia
- 🚫 NO DEBE validar unicidad de SIDs (responsabilidad de FASE 4)
- 🚫 NO DEBE modificar estructura YAML (solo completar campos semánticos)
- 🚫 NO DEBE generar reportes de errores (responsabilidad de FASE 4-5)
- 🚫 NO DEBE crear nuevos scripts de inferencia o módulos de vocabulario
- 🚫 NO DEBE usar vocabularios externos o sinónimos no documentados
- 🚫 NO DEBE mencionar capacidad de procesamiento, tokens o límites del modelo

---

**RESTRICCIÓN ESTRICTA SOBRE HEURÍSTICAS**

La FASE 3 (semantic-enricher) trabaja **exclusivamente mediante razonamiento lingüístico del LLM**.

Queda **estrictamente prohibido**:
- ❌ Ejecutar código Python, JavaScript o cualquier lenguaje de programación
- ❌ Generar código inline, temporal o auxiliar para realizar inferencias
- ❌ Seguir pseudocódigo como si fueran instrucciones ejecutables
- ❌ Aplicar algoritmos programáticos, bucles, condicionales o estructuras de control
- ❌ Simular funciones, métodos o procedimientos
- ❌ Procesar estructuras de datos (arrays, objetos, árboles) como si fueran objetos de un lenguaje de programación
- ❌ Utilizar lógica de AST programático o manipulación sintáctica basada en código

**Cualquier referencia a "heurísticas" en este documento debe interpretarse como**:
- Patrones de razonamiento semántico declarativo
- Reglas lingüísticas expresadas en lenguaje natural
- Criterios de decisión basados en análisis de significado textual
- Guías interpretativas para el análisis semántico del LLM

**Modelo conceptual de comprensión estructural**:
El agente debe aplicar un modelo conceptual de comprensión estructural basado **únicamente en análisis semántico del LLM**, NO en procesamiento programático de AST.

El enriquecimiento se realiza mediante:
1. Lectura del contenido textual del campo `descripcion`
2. Comparación semántica con términos del vocabulario SID
3. Selección del término más apropiado mediante razonamiento lingüístico
4. Asignación de confianza basada en claridad semántica del texto

---

### FASE 4 – 04-yaml-validator.md

**Responsabilidad única**: Validación semántica de archivos `.yaml` enriquecidos

**Entrada**:
- Ruta(s) a archivo(s) `.yaml` con SIDs generados
- Reglas de validación (`APS/LINTER_RULES.md`)
- Vocabulario SID (para verificar canonicidad)

**Salida**:
- Reportes de validación por archivo (`.md`)
- Código de salida:
  - `0`: Sin errores
  - `1`: Warnings (no bloqueante)
  - `2`: Errores críticos (bloquea integración)

**Herramientas autorizadas**:
- `aps-tooling/scripts/yaml_lint_v6_semantic.py` (ÚNICO validador permitido)
- Escritura de reportes individuales en `swarm/reports/validation/`

**Validaciones obligatorias**:
1. **Unicidad de SIDs**: Detectar duplicados dentro de cada archivo
2. **Canonicidad**: Verificar que `accion`, `relacion`, `nivel` existen en vocabulario v1.0
3. **Bloques obligatorios**: Entry Guard, Exit Strategy, State JSON Protocol
4. **Estructura**: Validar esquema YAML contra APS v3.5

**Criterios de éxito obligatorios**:
- ✅ Todos los archivos del lote validados (con o sin errores)
- ✅ Errores críticos detectados y documentados en reportes individuales
- ✅ Reportes auto-guardados con timestamp (`{nombre_archivo}_validation_{timestamp}.md`)
- ✅ Estadísticas de confianza (HIGH/MEDIUM/LOW) incluidas en cada reporte
- ✅ Códigos de salida correctos: 0 (OK), 1 (warnings), 2 (errores críticos)

**Prohibiciones explícitas**:
- 🚫 NO DEBE modificar archivos YAML (modo solo-lectura para archivos fuente)
- 🚫 NO DEBE consolidar reportes (responsabilidad de FASE 5)
- 🚫 NO DEBE corregir errores automáticamente
- 🚫 NO DEBE crear validadores personalizados o reglas no documentadas
- 🚫 NO DEBE mencionar limitaciones de procesamiento o volumen

---

### FASE 5 – 05-report-generator.md

**Responsabilidad única**: Consolidación de reportes de validación individuales

**Entrada**:
- Múltiples reportes individuales (`.md`) de validación
- Opcionalmente: estadísticas de enriquecimiento (fase 2)

**Salida**:
- Reporte consolidado final (`.md`) con:
  - Resumen ejecutivo global
  - Análisis por sublotes/archivos
  - Top N errores más frecuentes
  - Análisis de confianza (HIGH/MEDIUM/LOW)
  - Plan de corrección recomendado
  - Detalles por archivo

**Herramientas autorizadas**:
- Lectura de reportes individuales desde `swarm/reports/validation/`
- Agregación estadística y análisis de errores
- Generación de Markdown formateado

**Criterios de éxito obligatorios**:
- ✅ Reporte consolidado único generado con timestamp
- ✅ Estadísticas globales precisas (total errores, warnings, archivos procesados)
- ✅ Análisis de frecuencia de errores (Top N errores más comunes)
- ✅ Recomendaciones accionables de corrección
- ✅ Referencias explícitas a documentación APS (`APS/LINTER_RULES.md`, vocabulario)

**Prohibiciones explícitas**:
- 🚫 NO DEBE ejecutar validaciones (responsabilidad de FASE 4)
- 🚫 NO DEBE modificar reportes individuales originales
- 🚫 NO DEBE crear herramientas de análisis estadístico nuevas
- 🚫 NO DEBE generar reportes parciales antes del final de FASE 4
- 🚫 NO DEBE inventar métricas no derivadas de reportes existentes

---

## 🚀 Prompt Orquestador (Alias Reutilizable)

### Naturaleza del Orquestador

**El orquestador NO es un agente especializado**. Es un **prompt/alias** que:
- Coordina la ejecución secuencial de las 5 fases
- Se almacena como instrucción reutilizable en `.github/copilot-instructions.md` o como alias
- NO tiene archivo `.md` propio en `swarm/agents/yaml-pipeline/`
- El usuario lo invoca como un comando simplificado

### Especificación del Prompt Orquestador

```markdown
# Prompt: YAML Pipeline Orchestrator - APS v3.5

## Uso como Alias

Este prompt se invoca mediante alias de Copilot. El usuario ejecuta:

```
@yaml-pipeline <ruta-json> [modo]
```

Ejemplos:
- `@yaml-pipeline swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json`
- `@yaml-pipeline swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json completo`

## Objetivo del Prompt

Coordinar la ejecución secuencial y completa de las 5 fases del pipeline de procesamiento
de definiciones de agentes APS v3.5 desde JSON hasta reportes de validación.

## Entrada Obligatoria

**Opción A - Input único (recomendado)**:
- Ruta a archivo JSON de swarm (ej: `swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json`)
- Modo de operación: `completo` (5 fases desde JSON)

**Opción B - Input parcial**:
- Ruta(s) a archivo(s) `.md` o patrón glob (ej: `swarm/agents/J2C-v1-Swarm-v3-5/*.md`)
- Modo de operación: `desde-md` (4 fases desde MD) | `validacion-solo` (solo FASE 4) | `reporte-solo` (solo FASE 5)

## Flujo de Ejecución Normativo

**Importante**: El prompt orquestador carga secuencialmente las instrucciones de cada agente especializado (01-05) y ejecuta herramientas directamente. NO delega a subagentes.

### FASE 1: Extracción JSON → MD

**Agente a cargar**: `swarm/agents/yaml-pipeline/01-json-extractor.md`

**Acciones obligatorias**:
1. Leer archivo JSON de definición de swarm
2. Extraer TODOS los agentes definidos en el JSON
3. Generar archivos `.md` individuales numerados secuencialmente (01, 02, 03...)
4. Preservar contenido `goal` exactamente como aparece en JSON

**Condición de continuación**:
- ✅ N archivos `.md` generados = N agentes en JSON
- ✅ Todos los archivos tienen contenido `goal` válido

**Si falla**: DETENER pipeline inmediatamente, reportar estructura JSON inválida o archivo no encontrado.

---

### FASE 2: Conversión MD → YAML

**Agente a cargar**: `swarm/agents/yaml-pipeline/02-md2yaml-converter.md`

**Acciones obligatorias**:
1. Ejecutar script `aps-tooling/scripts/md2yaml.py` con TODOS los archivos `.md` del lote
2. **Conversión MECÁNICA únicamente**: Generar estructura YAML APS v3.5 con placeholders
3. **SIN INFERENCIA SEMÁNTICA**: Todos los campos `accion`, `relacion`, `nivel`, `sid` deben contener `<<PENDING_AI>>`
4. Verificar que el número de archivos `.yaml` generados es igual al número de `.md` procesados
5. Validar que todos los archivos `.yaml` son parseables por PyYAML

**Condición de continuación**:
- ✅ N archivos `.yaml` generados = N archivos `.md` procesados
- ✅ **TODOS** los campos semánticos contienen `<<PENDING_AI>>` (ninguno con valores inferidos)
- ✅ Cero errores de parsing YAML

**Si falla**: DETENER pipeline inmediatamente, reportar archivo problemático al usuario.

---

### FASE 3: Enriquecimiento Semántico

**Agente a cargar**: `swarm/agents/yaml-pipeline/03-semantic-enricher.md`

**Acciones obligatorias**:
1. Cargar vocabulario SID desde `aps-tooling/schemas/sid_vocabulary_v1.yaml`
2. Realizar enriquecimiento semántico mediante análisis lingüístico LLM de TODOS los archivos `.yaml` generados en FASE 2
3. Si el lote excede 10 archivos, subdividir en sublotes de 3 y procesar secuencialmente
4. Completar campos `accion`, `relacion`, `nivel`, `sid`, `confidence`, `justificacion` usando **únicamente razonamiento semántico**
5. **NO ejecutar código, scripts o funciones** durante el proceso de inferencia

**Condición de continuación**:
- ✅ Todos los placeholders `<<PENDING_AI>>` reemplazados en todos los archivos mediante análisis semántico
- ✅ Estadísticas de confianza generadas (conteo HIGH/MEDIUM/LOW)
- ✅ Ningún código, pseudocódigo o script generado durante el proceso

**Si falla**: CONTINUAR con warnings, documentar bloques no enriquecidos en FASE 5.

---

### FASE 4: Validación Semántica

**Agente a cargar**: `swarm/agents/yaml-pipeline/04-yaml-validator.md`

**Acciones obligatorias**:
1. Ejecutar `aps-tooling/scripts/yaml_lint_v6_semantic.py` en TODOS los archivos `.yaml` enriquecidos
2. Generar reporte individual por cada archivo en `swarm/reports/validation/`
3. Capturar códigos de salida (0=OK, 1=warnings, 2=errores críticos)

**Condición de continuación**:
- ✅ Todos los archivos validados (incluso si tienen errores críticos)
- ✅ Reportes individuales generados con timestamp

**Si falla**: CONTINUAR, reportar archivos no validables en FASE 5.

---

### FASE 5: Reporte Consolidado

**Agente a cargar**: `swarm/agents/yaml-pipeline/05-report-generator.md`

**Acciones obligatorias**:
1. Leer TODOS los reportes individuales generados en FASE 4
2. Consolidar estadísticas globales (errores totales, warnings, archivos procesados)
3. Identificar Top N errores más frecuentes (N≥5)
4. Generar plan de corrección con acciones específicas
5. Guardar reporte consolidado en `swarm/reports/validation/{nombre_lote}_CONSOLIDADO_FINAL_{timestamp}.md`

**Salida final obligatoria**:
- ✅ Reporte consolidado único con análisis completo
- ✅ Resumen ejecutivo mostrado al usuario (tabla + métricas clave)

**Si falla**: Reportar error al usuario, NO intentar generar reporte parcial.

---

## Gestión de Volumen en Modo BATCH

**Regla obligatoria**: TODAS las fases DEBEN procesar el lote completo antes de avanzar.

**Si el lote excede 10 archivos**:
1. FASE 1: Extracción de TODOS los agentes del JSON en una sola operación
2. FASE 2: Conversión de TODOS los archivos MD en un solo comando
3. FASE 3: Subdividir en sublotes de 3 archivos, procesar secuencialmente, completar TODA la fase
4. FASE 4: Validar TODOS los archivos en un bucle secuencial
5. FASE 5: Consolidar TODOS los reportes en uno solo

**ESTÁ PROHIBIDO**:
- Procesar 5 fases para archivo 1, luego 5 fases para archivo 2, etc.
- Generar reportes intermedios fuera de FASE 5
- Validar archivos antes de completar FASE 3 para todo el lote

---

## Comportamiento ante Errores

| Fase | Tipo de Error | Acción Obligatoria |
|------|---------------|---------------------|
| FASE 1 | JSON no encontrado o inválido | **DETENER** pipeline, reportar ruta esperada y estructura JSON |
| FASE 1 | Agentes sin campo `goal` | **DETENER** pipeline, reportar agentes problemáticos |
| FASE 2 | Conversión falla (parsing error) | **DETENER** pipeline, reportar archivo + línea del error |
| FASE 2 | Script no encontrado | **DETENER** pipeline, reportar ruta esperada del script |
| FASE 3 | Enriquecimiento parcial (bloques sin SID) | **CONTINUAR**, documentar bloques LOW confidence |
| FASE 3 | Vocabulario no encontrado | **DETENER** pipeline, reportar ruta esperada del vocabulario |
| FASE 4 | Validación detecta errores críticos | **CONTINUAR**, incluir errores en reportes |
| FASE 4 | Script validador no encontrado | **DETENER** pipeline, reportar ruta esperada |
| FASE 5 | Reportes individuales no encontrados | **DETENER**, reportar archivos esperados |
| FASE 5 | Error de consolidación | **DETENER**, reportar causa del error |

---

## Restricciones Globales del Orquestador

🚫 **PROHIBICIONES ABSOLUTAS**:
- NO DEBE delegar a subagentes, invocar otros agentes o crear nuevos contextos
- NO DEBE mencionar tokens, límites de contexto, capacidad del modelo u optimizaciones
- NO DEBE procesar archivos individualmente (archivo por archivo ejecutando 4 fases)
- NO DEBE generar reportes parciales antes de completar FASE 3
- NO DEBE crear scripts, módulos Python o herramientas nuevas
- NO DEBE modificar el orden de fases (1→2→3→4 es invariable)
- NO DEBE inventar modos de operación no especificados

✅ **OBLIGACIONES ABSOLUTAS**:
- DEBE ejecutar fases en orden estricto (1→2→3→4→5)
- DEBE validar condiciones de éxito antes de avanzar a siguiente fase
- DEBE detener pipeline si herramientas requeridas no existen
- DEBE procesar lotes completos por fase (batch processing)
- DEBE usar ÚNICAMENTE scripts existentes en `aps-tooling/scripts/`
- DEBE reportar al usuario si el volumen excede capacidad de procesamiento
```

---

## 🎯 Caso de Uso Principal: Input Único JSON

### Ejemplo de Invocación:

```
Usuario: "@yaml-pipeline swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json"
```

### Flujo Completo (5 fases):

```
1. FASE 1 (JSON→MD):
   - Lee J2C-v1-Swarm-v3-5.json
   - Extrae 11 agentes
   - Genera 01-J2Ci-Orchestrator.md ... 11-J2Ci-Greeter.md
   
2. FASE 2 (MD→YAML):
   - Ejecuta md2yaml.py en los 11 archivos .md
   - Genera 11 archivos .yaml con placeholders
   
3. FASE 3 (Enriquecimiento):
   - Carga vocabulario SID v1.0
   - Enriquece los 11 archivos .yaml (sublotes de 3)
   - Completa campos semánticos
   
4. FASE 4 (Validación):
   - Ejecuta yaml_lint_v6_semantic.py en los 11 archivos
   - Genera 11 reportes individuales
   
5. FASE 5 (Consolidación):
   - Consolida los 11 reportes
   - Genera reporte maestro con estadísticas
   - Presenta resumen ejecutivo al usuario
```

### Ventaja del Input Único:

**Con un solo comando y un solo archivo JSON**, el usuario obtiene:
- ✅ Agentes extraídos en formato Markdown
- ✅ Archivos YAML estructurados
- ✅ Metadatos semánticos enriquecidos
- ✅ Validación completa con detección de errores
- ✅ Reporte consolidado con plan de corrección

**Sin necesidad de**:
- ❌ Ejecutar múltiples comandos
- ❌ Gestionar archivos intermedios manualmente
- ❌ Conocer la estructura interna del pipeline

---

## 🎯 Beneficios de la Arquitectura Propuesta

### 1. **Especialización**
- Cada agente tiene una única responsabilidad (Single Responsibility Principle)
- Instrucciones focalizadas reducen ambigüedad y mejoran determinismo
- Menor superficie de error por agente

### 2. **Reutilización**
- Posibilidad de ejecutar fases individuales (ej: solo validación si los YAML ya existen)
- Independencia de herramientas permite testing aislado de cada fase
- Generadores de reportes reutilizables con otras fuentes de validación

### 3. **Mantenibilidad**
- Modificaciones en validación no afectan conversión ni enriquecimiento
- Adición de nuevas fases (ej: `05-yaml-optimizer.md`) sin impacto en existentes
- Reglas y restricciones centralizadas en un único archivo por agente

### 4. **Escalabilidad**
- Gestión de volumen mediante sublotes configurable
- Nuevas herramientas agregables a agentes especializados sin refactorización
- Lotes procesados completamente por fase (no por archivo)

### 5. **Claridad y Determinismo**
- Especificación del orquestador legible y modificable por humanos
- Flujo de ejecución explícito con condiciones de continuación documentadas
- Prohibiciones y obligaciones claramente definidas para cada fase

### 6. **Conformidad APS v3.5**
- Cada agente definido como archivo `.md` con estructura APS v3.5
- Posibilidad de asignar `sid`, `accion`, `relacion`, `nivel` a cada agente
- Cumplimiento estricto de restricciones anti-subagente y anti-delegación

---

## 🔄 Cómo Funciona en la Práctica (desde la perspectiva de Copilot)

### Usuario ejecuta:

```
"@pipeline-orchestrator procesa swarm/agents/J2C-v1-Swarm-v3-5/*.md en modo completo"
```

### Copilot internamente:

```
1. Leo 00-pipeline-orchestrator.md
2. Identifico que debo ejecutar 4 fases
3. Sigo las instrucciones definidas en 01-md2yaml-converter.md
   → Ejecuto conversión MD→YAML (herramientas Python)
4. Sigo las instrucciones definidas en 02-semantic-enricher.md
   → Ejecuto enriquecimiento semántico exclusivamente mediante razonamiento lingüístico (LLM-only), sin código, sin pseudocódigo, sin heurísticas programáticas.
5. Sigo las instrucciones definidas en 03-yaml-validator.md
   → Ejecuto validación (yaml_lint_v6_semantic.py)
6. Sigo las instrucciones definidas en 04-report-generator.md
   → Consolido reportes y genero reporte final
7. Muestro reporte al usuario
```

**Importante**: No estoy "llamando" a subagentes reales (no permitido), sino **cambiando mi contexto de instrucciones** secuencialmente. Soy un único agente (Copilot) con **4 modos de operación**.

---

## 📝 Plan de Implementación

### Paso 1: Crear Estructura de Directorios

```bash
mkdir -p swarm/agents/yaml-pipeline
```

### Paso 2: Crear Agentes Especializados (01-05)

Crear los 5 agentes especializados en `swarm/agents/yaml-pipeline/`:

- **01-json-extractor.md** (nueva funcionalidad de extracción)
- **02-md2yaml-converter.md** (extraído de yaml-pipeline monolítico)
- **03-semantic-enricher.md** (extraído de yaml-pipeline monolítico)
- **04-yaml-validator.md** (extraído de yaml-pipeline monolítico)
- **05-report-generator.md** (nueva funcionalidad de consolidación)

### Paso 3: Definir Prompt Orquestador como Alias

Crear archivo `.github/copilot-instructions.md` (o `.vscode/settings.json` para alias local) con:

```markdown
## @yaml-pipeline

Prompt orquestador para pipeline YAML APS v3.5.

**Instrucciones**:
1. Cargar y ejecutar secuencialmente swarm/agents/yaml-pipeline/01-json-extractor.md
2. Cargar y ejecutar secuencialmente swarm/agents/yaml-pipeline/02-md2yaml-converter.md
3. Cargar y ejecutar secuencialmente swarm/agents/yaml-pipeline/03-semantic-enricher.md
4. Cargar y ejecutar secuencialmente swarm/agents/yaml-pipeline/04-yaml-validator.md
5. Cargar y ejecutar secuencialmente swarm/agents/yaml-pipeline/05-report-generator.md

Procesar lotes completos por fase. No delegar. No mencionar tokens.
```

### Paso 4: Estructura APS Obligatoria por Agente

Cada archivo `.md` DEBE seguir esta estructura:

```markdown
# {Nombre del Agente}

## Metadata
- **sid**: `AGT.{accion}.{dominio}.{nivel}`
- **version**: `1.0.0`
- **dependencies**: [lista exacta de scripts/herramientas]

## GOAL
{Objetivo único y específico del agente}

## INPUT
{Especificación precisa de entrada: tipos, rutas, formatos}

## OUTPUT
{Especificación precisa de salida: tipos, rutas, formatos}

## INSTRUCTIONS
{Instrucciones paso a paso, sin ambigüedad}

## CONSTRAINTS
{Restricciones y prohibiciones explícitas}

## SUCCESS_CRITERIA
{Condiciones de éxito verificables}

## ERROR_HANDLING
{Comportamiento ante errores específicos}
```

### Paso 5: Estrategia de Migración

**Opción recomendada**: **Deprecar `yaml-pipeline.md` monolítico**

1. Mover `yaml-pipeline.md` a `deprecated/yaml-pipeline-monolithic.md`
2. Crear los 5 archivos especializados (01-05) en `swarm/agents/yaml-pipeline/`
3. Crear alias `@yaml-pipeline` en `.github/copilot-instructions.md`
4. Actualizar documentación para referenciar alias con input JSON
5. Mantener archivo monolítico durante 1 iteración para referencia

---

## 📜 Contrato General de Agentes APS v3.5

Esta sección establece restricciones universales que TODOS los agentes del pipeline DEBEN cumplir.

### Restricciones Absolutas (Aplicables a TODOS los Agentes)

#### 1. Prohibición de Subagentes y Delegación

- **NO DEBE** invocar otros agentes mediante sintaxis `@agent-name`
- **NO DEBE** delegar tareas a subagentes, contextos secundarios o procesos externos
- **NO DEBE** crear jerarquías de agentes o cadenas de invocación
- Cada agente ejecuta ÚNICAMENTE las instrucciones de su archivo `.md` correspondiente

#### 2. Prohibición de Cambio de Identidad

- **NO DEBE** "cambiar de contexto" o "activar modo X"
- **NO DEBE** "actuar como" otro agente
- **NO DEBE** simular comportamiento de otros agentes o fases
- La identidad del agente es fija y determinada por el archivo `.md` cargado

#### 3. Prohibición de Menciones a Capacidad del Modelo

- **NO DEBE** mencionar tokens, límites de contexto o ventana de atención
- **NO DEBE** hablar de "optimizaciones", "compresión" o "resumir por limitaciones"
- **NO DEBE** inventar estrategias de manejo de volumen no especificadas
- Si el volumen excede la capacidad, DEBE detenerse y reportar al usuario

#### 4. Prohibición de Creación de Herramientas y Ejecución de Código

- **NO DEBE** generar scripts Python, módulos, librerías o herramientas nuevas
- **NO DEBE** modificar scripts existentes en `aps-tooling/scripts/`
- **NO DEBE** crear vocabularios, esquemas o reglas de validación adicionales
- **NO DEBE** ejecutar código inline, temporal o auxiliar durante procesos de inferencia
- **NO DEBE** interpretar pseudocódigo como instrucciones ejecutables
- **NO DEBE** aplicar algoritmos programáticos, lógica de AST o heurísticas basadas en código
- Solo puede usar herramientas explícitamente listadas en sección "Herramientas autorizadas"
- Los procesos de inferencia semántica (FASE 3) deben ser **100% lingüísticos**, sin código

#### 5. Prohibición de Mezcla de Fases

- **NO DEBE** ejecutar operaciones de otras fases (ej: validar durante enriquecimiento)
- **NO DEBE** adelantar o retrasar fases en el pipeline
- **NO DEBE** procesar archivos individualmente ejecutando múltiples fases por archivo
- Cada fase se completa TOTALMENTE para el lote antes de avanzar

#### 6. Obligación de Procesamiento Batch por Fases

- **DEBE** procesar TODOS los archivos del lote en la fase actual antes de avanzar
- **DEBE** respetar el orden estricto: FASE 1 (todos) → FASE 2 (todos) → FASE 3 (todos) → FASE 4
- **DEBE** subdividir en sublotes si el volumen lo requiere, pero completando fase por fase
- **ESTÁ PROHIBIDO** procesar archivo por archivo con todas las fases

#### 7. Obligación de Uso de Input del Orquestador

- **DEBE** usar únicamente los archivos, rutas y parámetros proporcionados por el orquestador
- **NO DEBE** buscar archivos adicionales no especificados
- **NO DEBE** asumir rutas, nombres de archivo o estructuras de directorio
- Ante ambigüedad, DEBE solicitar clarificación al usuario

### Criterios de Fallo Obligatorios

Si un agente encuentra cualquiera de estas situaciones, DEBE detenerse inmediatamente:

1. Herramienta requerida no existe en la ruta especificada
2. Archivo de entrada no encontrado o inaccesible
3. Error de parsing irrecuperable (YAML inválido, sintaxis incorrecta)
4. Volumen de archivos excede capacidad reportable
5. Violación de restricciones de fase (ej: detecta que debe ejecutar fase no asignada)

### Formato de Reporte de Fallo

Cuando un agente se detiene por fallo, DEBE generar este reporte:

```
❌ FALLO EN FASE {N} – {Nombre Agente}

Causa: {Descripción específica del error}
Archivo problemático: {Ruta completa}
Línea/Bloque: {Si aplica}
Acción esperada: {Qué se intentó hacer}
Acción correctiva: {Qué debe hacer el usuario}

Archivos procesados exitosamente antes del fallo: {N}
Archivos pendientes: {M}
```

---

## 📚 Referencias Normativas

- **Metodología APS v3.5**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Reglas de Validación**: `APS/LINTER_RULES.md`
- **Vocabulario SID v1.0**: `aps-tooling/schemas/sid_vocabulary_v1.yaml`
- **Filosofía SWARM**: `Filosofia_funcional_SWARM_J2C.md`
- **Pipeline Monolítico (deprecated)**: `deprecated/yaml-pipeline-monolithic.md`

---

**Versión**: 1.0  
**Fecha**: 2025-11-20  
**Estado**: Especificación Normativa Aprobada  
**Próxima Revisión**: Tras implementación de los 5 agentes especializados
