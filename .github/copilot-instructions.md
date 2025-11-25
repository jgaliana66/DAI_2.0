# GitHub Copilot - Instrucciones Personalizadas del Proyecto

## Contexto del Repositorio

Este repositorio implementa el **SWARM J2C** (Journey to Cloud) con el **pipeline APS v4.0**, un sistema de 5 agentes especializados secuenciales para procesar archivos SwarmBuilder JSON y generar especificaciones YAML compatibles con APS v3.5.

## Alias y Comandos Disponibles

### @yaml-pipeline

Ejecuta el pipeline completo APS v4.0 de 5 fases secuenciales.

**Uso**: `@yaml-pipeline swarm/json/J2C-v1-Swarm-v3-5.json`

**Proceso**:
1. FASE 1: Extrae goals desde SwarmBuilder JSON → archivos `.md`
2. FASE 2: Convierte `.md` → `.yaml` mecánicamente con placeholders
3. FASE 3: Enriquece YAMLs semánticamente usando 100% razonamiento LLM (sin ejecutar código)
4. FASE 4: Valida YAMLs contra reglas APS v3.5
5. FASE 5: Genera reporte consolidado maestro

**Salida esperada**:
- Goals en `swarm/agents/{batch}/*.md`
- YAMLs en `swarm/agents/{batch}/*.yaml`
- Reporte en `swarm/reports/validation/{batch}_CONSOLIDADO_FINAL_{timestamp}.md`

## Principios del Pipeline APS v4.0

Cuando trabajes con este repositorio, sigue estas reglas:

1. **Metodología APS v3.5**: Todos los agentes siguen la especificación APS v3.5 documentada en `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`. Consulta este documento para entender la estructura de bloques obligatorios.

2. **Agentes Especializados Secuenciales**: El pipeline usa 5 agentes especializados que DEBEN ejecutarse en orden estricto (FASE 1 → 2 → 3 → 4 → 5). NUNCA saltees fases ni las ejecutes en paralelo.

3. **Procesamiento Batch-by-Phase**: Completa TODOS los archivos en cada fase antes de avanzar a la siguiente. NUNCA proceses archivo por archivo a través de todas las fases.

4. **FASE 3 es 100% LLM**: El enriquecimiento semántico DEBE hacerse con razonamiento lingüístico puro del modelo. NO ejecutes scripts Python ni uses herramientas externas en esta fase.

5. **Pipeline Determinístico**: El mismo JSON de entrada debe producir la misma estructura de salida. No introduzcas efectos colaterales ni variabilidad.

6. **NO Subagentes ni Delegación**: El orquestador carga las instrucciones de cada agente secuencialmente y las ejecuta directamente. No uses mecanismos de subagentes autónomos ni transferencias de control.

7. **Bloques Obligatorios en YAMLs**: Cada YAML generado DEBE incluir:
   - Entry Guard (precondiciones)
   - Exit Strategy (postcondiciones)
   - State JSON (estado embebido en YAML)
   - SID (identificador semántico)

## Estructura del Proyecto

- **Agentes**: `.github/agents/` contiene 5 agentes especializados (formato `.agent.md`)
- **Prompts**: `.github/prompts/` contiene el orquestador y prompts standalone (formato `.prompt.md`)
- **Documentación APS**: `APS/` contiene metodología, estrategia y guías técnicas
- **Tooling**: `aps-tooling/scripts/` contiene scripts de conversión y validación
- **Schemas**: `aps-tooling/schemas/` contiene vocabulario semántico y reglas de validación

## Herramientas del Pipeline

- `md2yaml.py`: Conversión mecánica MD → YAML (FASE 2)
- `yaml_lint_v6_semantic.py`: Validador contra APS v3.5 (FASE 4)
- `sid_vocabulary_v1.yaml`: Vocabulario semántico para enriquecimiento (FASE 3)

## Políticas de Entorno Python

**CRÍTICO**: Cuando ejecutes código Python en este proyecto:

1. **SIEMPRE usa `python3`**, NUNCA uses `python`
   ```bash
   # ✅ CORRECTO
   python3 aps-tooling/scripts/md2yaml.py
   
   # ❌ INCORRECTO
   python aps-tooling/scripts/md2yaml.py
   ```

2. **SIEMPRE usa un entorno virtual** antes de ejecutar scripts
   ```bash
   # Activar entorno virtual (si existe)
   source venv/bin/activate
   
   # O crear uno nuevo si no existe
   python3 -m venv venv
   source venv/bin/activate
   
   # Luego ejecutar scripts
   python3 aps-tooling/scripts/extract_goals_from_json.py
   ```

3. **Instalar dependencias en el entorno virtual**
   ```bash
   # Activar entorno virtual primero
   source venv/bin/activate
   
   # Instalar dependencias
   pip install -r aps-tooling/requirements.txt
   ```

**Razones**:
- `python` puede apuntar a Python 2.x en algunos sistemas
- Entornos virtuales evitan conflictos de dependencias
- Aislamiento del sistema global de Python

## Convenciones de Código

- Usa nombres descriptivos en español para archivos de agentes (ej: `01-J2Ci-Orchestrator.yaml`)
- Los SIDs siguen el formato: `{block_type}.{accion}.{relacion}.{nivel}`
- Todos los commits deben seguir Conventional Commits (feat, fix, chore, refactor, etc.)
- Los reportes de validación usan formato Markdown con métricas agregadas

## Políticas de Control de Versiones

**IMPORTANTE**: 
- ❌ **NUNCA hagas commit automáticamente**
- ✅ **SIEMPRE pregunta antes** de hacer commit o push
- ✅ Muestra un resumen de los cambios y espera confirmación del usuario
- ✅ Solo procede con `git commit` y `git push` después de aprobación explícita

## Cómo Ejecutar el Pipeline

Para ejecutar el pipeline completo:
1. Menciona `@yaml-pipeline` seguido de la ruta al archivo JSON
2. El sistema cargará `.github/prompts/yaml-pipeline.prompt.md`
3. Seguirá las instrucciones secuenciales para ejecutar las 5 fases
4. Mostrará un resumen después de cada fase antes de continuar

## Documentación de Referencia

- **Estrategia v4.0**: `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md`
- **Metodología APS v3.5**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Guía del Pipeline**: `APS/YAML_PIPELINE_README.md`
- **Orchestrator completo**: `.github/prompts/ORCHESTRATOR.md` (referencia detallada)

## Versión

- **Pipeline**: APS v4.0
- **Metodología**: APS v3.5
- **Última actualización**: 2025-11-21
