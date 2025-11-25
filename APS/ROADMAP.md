# APS v3.5 - Roadmap de Mejoras y Estado

Este documento recoge el estado de implementación de mejoras en la metodología APS v3.5 y el YAML Pipeline, organizadas por prioridad.

---

## ✅ Implementado en v2.0

### Sistema de Confianza Semántica
**Estado**: ✅ **Completado**  
**Ubicación**: `APS/AGENTE_YAML_PIPELINE.md` (sección 4.3)

- Clasificación HIGH/MEDIUM/LOW para inferencias semánticas
- Triple verificación: Vocabulario + Heurística + Coherencia
- Reconocimiento de sinónimos
- Sugerencias para inferencias de baja confianza
- Metadatos: `confidence`, `inference_method`, `inference_note`

**Pendiente**: Implementar en código de `enrich_yaml_with_llm.py`

---

### DENY_TERMS Contextual
**Estado**: ✅ **Completado**  
**Ubicación**: `APS/AGENTE_YAML_PIPELINE.md` (sección 4.4)

- Detección contextual por tipo de bloque (EXAMPLE, ANTIPATTERN)
- Reconocimiento de patrones de negación ("NO hacer", "NUNCA", "❌")
- Severidad variable: INFO → WARNING → ERROR según contexto
- Prevención de falsos positivos al describir antipatrones

---

### Modo Batch CI/CD
**Estado**: ✅ **Completado**  
**Ubicación**: 
- `aps-tooling/scripts/yaml_pipeline_cli.py`
- `.github/workflows/yaml-pipeline-ci.yml`
- `APS/YAML_PIPELINE_README.md` (sección Modo Batch)

Características implementadas:
- Flag `--ci-mode` para salida JSON estructurada
- Exit codes bien definidos (0-5):
  - 0: Success
  - 1: Warnings
  - 2: Errors
  - 3: Validation failed
  - 4: Security violation
  - 5: Internal error
- GitHub Actions workflow funcional
- Makefile targets: `agent-pipeline-batch`

---

### Reglas Centralizadas
**Estado**: ✅ **Completado**  
**Ubicación**: 
- `swarm/schemas/aps_v3.5_rules.yaml` (fuente de verdad)
- `code/yaml_lint_v2.py` (linter actualizado)
- `APS/MIGRATION_RULES_CENTRALIZATION.md` (guía migración)

Características:
- Esquema centralizado versionado (APS v3.5)
- Secciones: required_blocks, antipatterns, vocabulary, heuristics, protocols
- Linter v2 lee desde esquema (no hardcoded)
- Backward compatibility con legacy rules
- Plan de migración en 4 fases

**Pendiente**: Migrar `md2yaml.py` y `enrich_yaml_with_llm.py` a leer del esquema

---

### Validación de Seguridad
**Estado**: ✅ **Completado**  
**Ubicación**: `APS/AGENTE_YAML_PIPELINE.md` (sección 4.5)

- Allowlist de scripts permitidos
- Allowlist de prefijos de rutas: `.github/agents/`, `aps-tooling/`
- Validación de path traversal con `Path.resolve()`
- `execute_safe_command()` con `subprocess.run`
- 6 vectores de ataque bloqueados

---

### Best Practice AST Manipulation
**Estado**: ✅ **Documentado**  
**Ubicación**: `APS/YAML_AST_BEST_PRACTICE.md`

- Documentación completa de manipulación YAML mediante AST
- Implementación de `YAMLBlockEditor` class
- Comparación string-replace vs AST
- Cuándo usar cada técnica
- Ejemplos prácticos con `enrich_yaml_block()`

**Pendiente**: Marcar string-replace como DEPRECATED oficialmente en todo el pipeline

---

## 🔴 Esencial Inmediato (DEBE implementarse)

### 1.1. Integrar AST como Mecanismo Oficial
**Prioridad**: 🔴 CRÍTICA  
**Estado**: ⚠️ Documentado pero no reforzado

**Problema**:
- La documentación explica AST, pero el pipeline/agente sigue mencionando `replace_string_in_file`
- Riesgo de inconsistencia: lectores pueden creer que string-replace sigue siendo válido
- Copilot puede regenerar lógica basada en string-replace

**Acción**:
1. Actualizar `AGENTE_YAML_PIPELINE.md`:
   - Marcar explícitamente `replace_string_in_file` como **DEPRECATED**
   - Declarar AST (yaml.safe_load → dict → yaml.safe_dump) como **ESTÁNDAR OFICIAL**
   - String-replace solo permitido para: comentarios, placeholders textuales, casos edge
2. Actualizar `YAML_PIPELINE_README.md`:
   - Sección "Modificación de YAML: Solo AST"
   - Ejemplos de cómo NO usar string-replace
3. Crear sección "⚠️ DEPRECATED" en documentos legacy

**Resultado esperado**:
- Inequívoco que AST es el estándar para modificar campos YAML en APS v3.5+

---

### 1.3. Documento Unificado de Reglas del Linter
**Prioridad**: 🔴 CRÍTICA  
**Estado**: ❌ No existe (reglas dispersas)

**Problema**:
- Reglas del linter están en múltiples documentos (metodología, pipeline, notas)
- No hay punto único con TODAS las reglas condensadas
- Difícil revisar coherencia o evolucionar a APS v3.6

**Acción**:
Crear `APS/LINTER_RULES.md` con:

1. **Reglas Estructurales**:
   - Claves obligatorias por tipo de bloque
   - Formato SID: `<TYPE>.<accion>.<relacion>.<nivel>`
   - Coincidencia `block_type` ↔ `TYPE` del SID
   - No duplicidad de SIDs dentro del archivo

2. **Reglas de Contenido**:
   - DENY_TERMS (lista completa con regex)
   - Bloques obligatorios APS v3.5:
     - Entry Guard
     - Política NO-SALTO-AUTOMÁTICO
     - STATE_JSON Protocol
     - Loop Contract
   - Agentes exentos (one-shot, helpers)

3. **Severidad y Códigos de Error**:
   - `ERROR` / `WARNING` / `INFO`
   - Semántica de cada código:
     - `SID_DUPLICATE`
     - `AUTO_NUMBERED_BLOCK`
     - `DENY_TERM`
     - `MISSING_REQUIRED_BLOCK`
     - `INVALID_SID_FORMAT`
     - `BLOCK_TYPE_MISMATCH`

4. **Políticas de Detección Contextual**:
   - Exenciones por tipo de bloque (EXAMPLE, ANTIPATTERN)
   - Patrones de negación
   - Umbral de confianza para warnings

**Resultado esperado**:
- Visión única y clara de todas las reglas del linter
- Base estable para versiones futuras (APS v3.6, v4.0)
- Referencia rápida para desarrolladores

---

### 1.4. Versionado Formal del Vocabulario SID
**Prioridad**: 🔴 CRÍTICA  
**Estado**: ❌ Vocabulario implícito, no formalizado

**Problema**:
- Vocabulario SID existe pero no está versionado ni centralizado
- Riesgo de términos nuevos sin control
- Divergencia semántica entre agentes o versiones
- Dificultad para trazar cambios entre APS v3.5 → v3.6

**Acción**:
Crear `aps-tooling/schemas/sid_vocabulary_v1.yaml`:

```yaml
version: "1.0"
aps_version: "3.5"
description: "Vocabulario canónico de SIDs para APS v3.5"

acciones:
  permitidas:
    - verificar
    - capturar
    - generar
    - detectar
    - prohibir
    - delegar
    - confirmar
    - evaluar
    - validar
    - informar
  deprecated: []
  
relaciones:
  permitidas:
    - control.active_agent
    - control.estado
    - usuario.confirmacion
    - state_json
    - handoff.confirm
    - recursion.limit
    - loop.prevention
  deprecated: []

niveles:
  permitidos:
    - guard
    - workflow
    - protocol
    - template
    - policy
    - constraint
    - heuristic
  deprecated: []

politica_evolucion:
  agregar_termino:
    - "Pull request con justificación semántica"
    - "Revisión por arquitecto APS"
    - "Actualización de versión (1.0 → 1.1)"
  
  deprecar_termino:
    - "Mover a lista deprecated"
    - "Mantener 2 versiones para backward compatibility"
    - "Eliminar en versión mayor (1.x → 2.0)"

changelog:
  - version: "1.0"
    date: "2025-11-19"
    changes: "Versión inicial para APS v3.5"
```

**Resultado esperado**:
- Coherencia global de SIDs en todo el SWARM
- Trazabilidad de evolución semántica
- Base para validación automática de vocabulario

---

## 🟡 Esencial Corto Plazo (SHOULD completarse)

### 1.2. Esquema YAML Formal Completo
**Prioridad**: 🟡 ALTA  
**Estado**: ⚠️ Parcial (`aps_v3.5_rules.yaml` existe pero incompleto)

**Problema**:
- `aps_v3.5_rules.yaml` tiene estructura parcial
- Falta esquema formal tipo JSON Schema para validación automática
- Sin esquema, claves mal escritas o tipadas pueden colarse

**Acción**:
1. Expandir `aps-tooling/schemas/aps_v3.5_rules.yaml` o crear `aps_agent_schema.yaml`:

```yaml
# Esquema completo de estructura de agente APS v3.5
version: "3.5"
schema_version: "1.0"

agent_structure:
  required:
    - agent
    - blocks
  
  agent:
    required: [name, version, profile]
    optional: [description, dependencies]
    
  blocks:
    type: map
    structure:
      required: [block_type, sid, content]
      optional: [accion, relacion, nivel, confidence, metadata]
      
      block_type:
        type: enum
        values: [BLK, GOAL, POL, OUT, CST, HEU, PROT, INP]
        
      sid:
        type: string
        pattern: "^[A-Z]+\\.[a-z_]+\\.[a-z_\\.]+\\.[a-z_]+$"
        
      accion:
        type: string
        vocabulary_ref: "sid_vocabulary_v1.yaml#acciones"
        
      relacion:
        type: string
        vocabulary_ref: "sid_vocabulary_v1.yaml#relaciones"
        
      nivel:
        type: string
        vocabulary_ref: "sid_vocabulary_v1.yaml#niveles"
        
      confidence:
        type: enum
        values: [HIGH, MEDIUM, LOW]
        
      content:
        type: string
        min_length: 10
```

2. Implementar validador automático:
   - Script `validate_schema.py`
   - Integración en `yaml_lint_v2.py`
   - Validación en CI/CD

**Resultado esperado**:
- Validación determinista y robusta
- Detección temprana de errores estructurales
- Contrato YAML claro y auditable

---

### 1.5. Enlazar Metodología APS ↔ Pipeline YAML
**Prioridad**: 🟡 ALTA  
**Estado**: ⚠️ Relación existe pero no explícita

**Problema**:
- Metodología APS (conceptual) y Pipeline YAML (implementación) están alineados
- Pero la relación formal no está documentada
- Lectores pueden ver como cosas separadas

**Acción**:

1. **En `METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`**:
   Añadir sección nueva:
   
   ```markdown
   ## 16. Implementación de APS vía YAML Pipeline
   
   La metodología APS v3.5 no es solo teoría: se materializa en agentes
   YAML validables a través del **YAML Pipeline**.
   
   ### Flujo de Materialización
   
   ```
   Concepto APS → Markdown (.md) → YAML estructurado → Validación → Agente válido
   ```
   
   1. **Concepto APS**: Principios, políticas, bloques obligatorios
   2. **Markdown**: Expresión humana del agente (fuente de verdad)
   3. **YAML**: Estructura validable generada por `md2yaml.py`
   4. **Validación**: Linter verifica coherencia APS (`yaml_lint_v2.py`)
   5. **Agente válido**: Listo para orquestación
   
   ### Herramientas Oficiales
   
   - **Pipeline completo**: Ver `APS/YAML_PIPELINE_README.md`
   - **Agente automatizado**: `@yaml-pipeline` en Copilot
   - **Reglas centralizadas**: `swarm/schemas/aps_v3.5_rules.yaml`
   - **Validador**: `code/yaml_lint_v2.py`
   
   APS sin pipeline = metodología sin ejecución.  
   Pipeline sin APS = herramienta sin gobierno.
   ```

2. **En `YAML_PIPELINE_README.md`**:
   Añadir al inicio:
   
   ```markdown
   ## 🏛️ Contexto: Metodología APS v3.5
   
   Este pipeline es la **implementación oficial** de la metodología APS v3.5
   (Agent Prompt Specification).
   
   APS define:
   - Estructura de agentes (bloques obligatorios, políticas)
   - Semántica de SIDs (identificadores semánticos)
   - Gobierno de coherencia (antipatrones, contradicciones)
   
   El pipeline **compila** y **valida** que los agentes cumplan APS.
   
   📖 **Leer primero**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
   ```

**Resultado esperado**:
- Claridad de que APS = metodología + toolchain
- Narrativa coherente entre concepto e implementación
- Punto de entrada claro para nuevos desarrolladores

---

## 🟢 Mejoras Recomendadas (COULD/NICE-TO-HAVE)

### 2.1. Unicidad Global de SIDs
**Prioridad**: 🟢 MEDIA  
**Estado**: ❌ Solo unicidad por archivo

**Mejora**:
- Comando opcional para verificar duplicados entre TODOS los agentes
- Puede ser: script separado, modo linter, o comando Makefile
- Ejemplo: `make check-global-sids` o `python3 aps-tooling/scripts/check_global_sids.py`

**Beneficio**:
- Evitar colisiones semánticas a escala SWARM
- Facilitar navegación y trazabilidad global

---

### 2.2. Política de Bloques Auto-numerados
**Prioridad**: 🟢 BAJA  
**Estado**: ⚠️ Se detectan pero gestión no clara

**Mejora**:
Documentar en `LINTER_RULES.md`:
- Qué es un `AUTO_NUMBERED_BLOCK`
- Qué debe hacer el usuario (refactorizar, renombrar)
- Cuándo podría ser ERROR vs WARNING

**Beneficio**:
- Reduce ambigüedad operacional
- Expectativas claras sobre limpieza del MD

---

### 2.3. Implementar Confianza en Código
**Prioridad**: 🟢 MEDIA  
**Estado**: ✅ Documentado, ❌ No implementado en `enrich_yaml_with_llm.py`

**Mejora**:
- Añadir lógica de confianza HIGH/MEDIUM/LOW en el script de enriquecimiento
- Campo `confidence` en el YAML generado
- Reportar en linter cuántos SIDs tienen confianza baja

**Beneficio**:
- Priorizar revisión humana de inferencias inciertas
- Transparencia en la "magia" semántica

---

### 2.4. Ajuste Fino DENY_TERMS (Ya implementado parcialmente)
**Prioridad**: 🟢 BAJA  
**Estado**: ✅ Detección contextual existe

**Mejora adicional**:
- Permitir flag explícito `example: true` en bloques para eximir validación
- Documentar mejor en `LINTER_RULES.md` cómo escribir ejemplos sin romper reglas

---

## 📅 Cronograma Sugerido

### Sprint 1 (Inmediato - 1 semana)
- ✅ Crear `APS/ROADMAP.md` (este documento)
- 🔴 1.1: Actualizar docs para marcar AST como oficial
- 🔴 1.3: Crear `APS/LINTER_RULES.md`
- ✅ 1.4: Crear `aps-tooling/schemas/sid_vocabulary_v1.yaml`

### Sprint 2 (Corto plazo - 2 semanas)
- 🟡 1.2: Expandir esquema YAML formal completo
- 🟡 1.5: Enlazar Metodología APS ↔ Pipeline
- 🟢 2.3: Implementar confianza en `enrich_yaml_with_llm.py`

### Sprint 3 (Mejoras - 1 mes)
- 🟢 2.1: Unicidad global de SIDs
- 🟢 2.2: Documentar política bloques auto-numerados
- 🟢 2.4: Ajustes finos DENY_TERMS

---

## 📊 Resumen de Estado

| Categoría | Total | Completado | En Progreso | Pendiente |
|-----------|-------|------------|-------------|-----------|
| Implementado v2.0 | 6 | 5 | 1 | 0 |
| Esencial Inmediato | 3 | 0 | 0 | 3 |
| Esencial Corto Plazo | 2 | 0 | 0 | 2 |
| Mejoras Recomendadas | 4 | 1 | 1 | 2 |
| **TOTAL** | **15** | **6** | **2** | **7** |

**Progreso global**: 40% completado, 53% pendiente

---

## 🎯 Objetivo Final

Con estas mejoras, APS v3.5 evolucionará de:

**Hoy**: Metodología muy sólida + pipeline funcional + algunas inconsistencias documentales

**Futuro**: Sistema documental y de tooling plenamente robusto, mantenible, extensible y con gobierno semántico completo

---

**Versión**: 1.0  
**Fecha**: 2025-11-19  
**Estado**: 🟢 Activo  
**Próxima revisión**: Sprint 1 completado
