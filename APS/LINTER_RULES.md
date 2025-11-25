# APS v3.5 - Reglas del Linter (Documentación Unificada)

Este documento centraliza TODAS las reglas de validación del linter APS v3.5, sus severidades, códigos de error y políticas de detección.

---

## 📋 Índice

1. [Reglas Estructurales](#reglas-estructurales)
2. [Reglas de Contenido](#reglas-de-contenido)
3. [Códigos de Error y Severidades](#códigos-de-error-y-severidades)
4. [Políticas de Detección Contextual](#políticas-de-detección-contextual)
5. [Agentes Exentos](#agentes-exentos)
6. [Evolución de Reglas](#evolución-de-reglas)

---

## 1. Reglas Estructurales

### 1.1. Formato de SID

**Regla**: Todo SID debe seguir el patrón `<TYPE>.<accion>.<relacion>.<nivel>`

**Patrón regex**:
```regex
^[A-Z]+\.[a-z_]+\.[a-z_\.]+\.[a-z_]+$
```

**Ejemplos válidos**:
```
BLK.verificar.control.active_agent.guard
GOAL.capturar.usuario.motivacion.workflow
POL.prohibir.handoff.automatico.policy
OUT.generar.state_json.template
```

**Ejemplos inválidos**:
```
BLK.Verificar.control.guard          # Acción con mayúscula
blk.verificar.control.guard          # TYPE en minúscula
BLK.verificar_control_guard          # Faltan separadores
BLK                                  # Incompleto
```

**Código de error**: `INVALID_SID_FORMAT`  
**Severidad**: ERROR

---

### 1.2. Coincidencia block_type ↔ SID TYPE

**Regla**: El primer componente del SID (`TYPE`) debe coincidir con `block_type`

**Mapeo**:
```yaml
block_type: BLK    → SID: BLK.*
block_type: GOAL   → SID: GOAL.*
block_type: POL    → SID: POL.*
block_type: OUT    → SID: OUT.*
block_type: CST    → SID: CST.*
block_type: HEU    → SID: HEU.*
block_type: PROT   → SID: PROT.*
block_type: INP    → SID: INP.*
```

**Ejemplo válido**:
```yaml
blocks:
  entry_guard:
    block_type: BLK
    sid: BLK.verificar.control.active_agent.guard  # ✅ Coincide
```

**Ejemplo inválido**:
```yaml
blocks:
  entry_guard:
    block_type: BLK
    sid: GOAL.verificar.control.guard  # ❌ No coincide
```

**Código de error**: `BLOCK_TYPE_MISMATCH`  
**Severidad**: ERROR

---

### 1.3. Unicidad de SIDs

**Regla**: Dentro de un mismo archivo YAML, no puede haber dos bloques con el mismo SID

**Alcance**: 
- Por archivo (implementado)
- Global (recomendado futuro)

**Ejemplo inválido**:
```yaml
blocks:
  bloque1:
    sid: BLK.verificar.control.guard
  bloque2:
    sid: BLK.verificar.control.guard  # ❌ Duplicado
```

**Código de error**: `SID_DUPLICATE`  
**Severidad**: ERROR

---

### 1.4. Claves Obligatorias por Bloque

**Regla**: Todo bloque debe tener las claves mínimas requeridas

**Campos obligatorios**:
```yaml
blocks:
  <nombre_bloque>:
    block_type: <requerido>
    sid: <requerido>
    content: <requerido>
```

**Campos opcionales**:
```yaml
    accion: <opcional>
    relacion: <opcional>
    nivel: <opcional>
    confidence: <opcional>
    metadata: <opcional>
```

**Código de error**: `MISSING_REQUIRED_FIELD`  
**Severidad**: ERROR

---

### 1.5. Vocabulario Controlado

**Regla**: Los valores de `accion`, `relacion`, `nivel` deben estar en el vocabulario oficial

**Fuente de verdad**: `aps-tooling/schemas/sid_vocabulary_v1.yaml`

**Validación**:
- Si el término está en `permitidas` → ✅ OK
- Si el término está en `deprecated` → ⚠️ WARNING (con sugerencia de reemplazo)
- Si el término no está en ninguna lista → ℹ️ INFO (nuevo término, revisar)

**Código de error**: 
- `DEPRECATED_TERM` (severidad: WARNING)
- `UNKNOWN_TERM` (severidad: INFO)

---

## 2. Reglas de Contenido

### 2.1. DENY_TERMS - Términos Prohibidos

**Regla**: El contenido (`content`) no debe contener términos que violen políticas APS

**Términos prohibidos** (regex patterns):

```regex
# Handoff automático sin confirmación
(devuelve|retorna|transfiere|deriva).*control.*automáticamente
(auto-handoff|auto-transfer|automatic.*handoff)

# Bypass de validación
(skip|bypass|ignore|omit).*(validation|verificación|control)

# Saltos sin control
(salta|skip|bypass).*directamente

# Política NO-SALTO-AUTOMÁTICO violada
devuelve.*control.*al.*cumplir.*(heurística|condición)
transfiere.*sin.*confirmación
```

**Fuente completa**: `aps-tooling/schemas/aps_v3.5_rules.yaml` → `antipatterns.deny_terms`

**Código de error**: `DENY_TERM`  
**Severidad**: ERROR (por defecto, salvo detección contextual)

**Ver**: [Políticas de Detección Contextual](#políticas-de-detección-contextual) para excepciones

---

### 2.2. Bloques Obligatorios APS v3.5

**Regla**: Todo agente APS v3.5 debe contener los bloques estructurales mínimos

**Bloques requeridos**:

1. **Entry Guard** (`BLK.verificar.control.active_agent.guard`)
   - Verifica que el agente es quien debe ejecutar
   - Evita ejecución fuera de contexto

2. **Política NO-SALTO-AUTOMÁTICO** (`POL.prohibir.handoff.automatico.policy`)
   - Prohibición explícita de handoff sin confirmación
   - Garantiza control humano en transferencias

3. **STATE_JSON Protocol** (`PROT.generar.state_json.template`)
   - Protocolo de estado estructurado
   - Formato JSON en comentario o sección dedicada

4. **Loop Contract** (`BLK.prohibir.recursion.directa.constraint`)
   - Prevención de bucles infinitos
   - Límite de recursión o iteración

**Código de error**: `MISSING_REQUIRED_BLOCK`  
**Severidad**: ERROR

**Excepciones**: Ver [Agentes Exentos](#agentes-exentos)

---

### 2.3. Bloques Auto-numerados

**Regla**: Los bloques con nombres auto-numerados indican posible duplicación o falta de semántica

**Patrón detectado**:
```
Bloque (2)
Bloque (3)
Goal Item (4)
```

**Código de error**: `AUTO_NUMBERED_BLOCK`  
**Severidad**: WARNING

**Acción recomendada**:
- Refactorizar el MD original para dar nombres semánticos
- Consolidar bloques duplicados
- Revisar si el contenido es realmente distinto

---

## 3. Códigos de Error y Severidades

### 3.1. Severidades

| Severidad | Significado | Acción | Exit Code |
|-----------|-------------|--------|-----------|
| **ERROR** | Violación crítica de APS | Bloquea integración | 2 |
| **WARNING** | Problema no crítico, requiere revisión | Permite continuar | 1 |
| **INFO** | Información para conocimiento | No bloquea | 0 |

---

### 3.2. Catálogo de Códigos de Error

#### Errores Estructurales (ERROR)

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| `INVALID_SID_FORMAT` | SID no cumple formato `TYPE.accion.relacion.nivel` | `BLK.verificar` (incompleto) |
| `BLOCK_TYPE_MISMATCH` | `block_type` no coincide con SID TYPE | `block_type: BLK` + `sid: GOAL.*` |
| `SID_DUPLICATE` | SID repetido dentro del archivo | Dos bloques con `BLK.verificar.control.guard` |
| `MISSING_REQUIRED_FIELD` | Falta campo obligatorio (`block_type`, `sid`, `content`) | Bloque sin `sid` |
| `MISSING_REQUIRED_BLOCK` | Falta bloque obligatorio APS v3.5 | Sin Entry Guard |

#### Errores de Contenido (ERROR)

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| `DENY_TERM` | Contenido usa término prohibido | "devuelve control automáticamente" |
| `ANTIPATTERN_DETECTED` | Antipatrón APS detectado | Handoff sin confirmación |

#### Advertencias (WARNING)

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| `AUTO_NUMBERED_BLOCK` | Nombre de bloque auto-numerado | `Bloque (2)`, `Goal (3)` |
| `DEPRECATED_TERM` | Término en vocabulario deprecated | Acción marcada como obsoleta |
| `LOW_CONFIDENCE_SID` | SID inferido con confianza baja | `confidence: LOW` |

#### Información (INFO)

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| `UNKNOWN_TERM` | Término no en vocabulario (posiblemente nuevo) | Nueva acción no catalogada |
| `CONTEXTUAL_EXEMPTION` | DENY_TERM exento por contexto | En bloque ANTIPATTERN |

---

## 4. Políticas de Detección Contextual

### 4.1. Exención por Tipo de Bloque

**Regla**: Bloques que describen ejemplos o antipatrones NO deben activar DENY_TERMS como ERROR

**Tipos exentos**:
```yaml
block_type: EXAMPLE      # Ejemplos educativos
block_type: ANTIPATTERN  # Descripción de antipatrones
```

**Comportamiento**:
- DENY_TERM detectado en bloque EXAMPLE → Severidad: **INFO**
- DENY_TERM detectado en bloque ANTIPATTERN → Severidad: **INFO**
- DENY_TERM detectado en otros bloques → Severidad: **ERROR**

**Ejemplo**:
```yaml
blocks:
  ejemplo_malo:
    block_type: ANTIPATTERN
    sid: BLK.ejemplo.antipatron.handoff_automatico
    content: |
      ❌ NO HACER: "Devuelve control automáticamente al cumplir heurística"
      
      # ℹ️ INFO (no ERROR) porque es un ANTIPATTERN
```

---

### 4.2. Detección de Negación

**Regla**: Expresiones que niegan un antipatrón NO deben tratarse como violación

**Patrones de negación detectados**:
```regex
(NO|NUNCA|JAMÁS)\s+(hacer|devolver|transferir|usar)
❌.*
🚫.*
\[PROHIBIDO\]
\[NO HACER\]
```

**Comportamiento**:
- Si se detecta negación + DENY_TERM → Severidad: **WARNING** (no ERROR)
- El linter reconoce que se está prescribiendo el comportamiento correcto

**Ejemplo**:
```yaml
blocks:
  politica:
    block_type: POL
    sid: POL.prohibir.handoff.automatico.policy
    content: |
      ❌ NUNCA devuelvas control automáticamente sin confirmación
      
      # ⚠️ WARNING (no ERROR) porque se detecta negación
```

---

### 4.3. Sistema de Confianza

**Regla**: SIDs inferidos con baja confianza generan WARNING adicional

**Niveles de confianza**:

| Nivel | Criterio | Acción |
|-------|----------|--------|
| **HIGH** | Término exacto en vocabulario canónico | ✅ OK |
| **MEDIUM** | Sinónimo reconocido o patrón heurístico | ✅ OK |
| **LOW** | Inferencia semántica sin match directo | ⚠️ WARNING |

**Código de error**: `LOW_CONFIDENCE_SID`  
**Severidad**: WARNING

**Metadata sugerida**:
```yaml
blocks:
  bloque_incierto:
    sid: BLK.procesar.datos.workflow
    confidence: LOW
    inference_method: "semantic_similarity"
    inference_note: "No hay match exacto en vocabulario. Revisar."
```

---

## 5. Agentes Exentos

### 5.1. Criterios de Exención

**Regla**: Algunos agentes pueden estar exentos de bloques obligatorios

**Categorías exentas**:

1. **One-shot agents** (ejecutan tarea puntual sin handoff)
   - Ejemplo: Generadores de reportes
   - Exención: No requieren Entry Guard ni Loop Contract

2. **Helper agents** (utilidades internas)
   - Ejemplo: Validadores, transformadores
   - Exención: No requieren STATE_JSON ni política handoff

3. **Test agents** (agentes de prueba)
   - Ejemplo: Mocks, fixtures
   - Exención: Pueden omitir todos los bloques obligatorios

**Marcado de exención**:
```yaml
agent:
  name: ReportGenerator
  exemption: one-shot
  reason: "Agente one-shot sin capacidad de handoff"
```

**Validación**:
- Si `exemption` está presente → omitir validación de bloques obligatorios
- Si `exemption` no está presente → aplicar todas las reglas

---

## 6. Evolución de Reglas

### 6.1. Versionado de Reglas

**Fuente de verdad**: `aps-tooling/schemas/aps_v3.5_rules.yaml`

**Versión actual**: APS v3.5 (schema version 1.0)

**Política de cambios**:

| Tipo de cambio | Versionado | Ejemplo |
|----------------|------------|---------|
| Añadir regla nueva (compatible) | Minor bump (1.0 → 1.1) | Nuevo DENY_TERM |
| Modificar severidad (WARNING → ERROR) | Minor bump (1.0 → 1.1) | Endurecer validación |
| Eliminar regla | Major bump (1.x → 2.0) | Remover validación deprecated |
| Cambiar formato SID | Major bump (APS v3.5 → v3.6) | Estructura semántica nueva |

---

### 6.2. Añadir Nueva Regla

**Procedimiento**:

1. **Propuesta**:
   - Issue en GitHub con justificación
   - Ejemplos de violación
   - Impacto en agentes existentes

2. **Revisión**:
   - Aprobación de arquitecto APS
   - Verificación de no-regresión

3. **Implementación**:
   - Actualizar `aps_v3.5_rules.yaml`
   - Actualizar este documento (LINTER_RULES.md)
   - Actualizar `sid_vocabulary_v1.yaml` si aplica

4. **Testing**:
   - Validar todos los agentes existentes
   - Verificar que pasan o se documentan excepciones

5. **Release**:
   - Bump de versión (schema_version)
   - Actualizar CHANGELOG
   - Comunicar cambios

---

### 6.3. Deprecar Regla

**Procedimiento**:

1. Marcar regla como `deprecated` en `aps_v3.5_rules.yaml`
2. Cambiar severidad ERROR → WARNING durante 1 versión
3. Eliminar completamente en próxima major version

**Ejemplo**:
```yaml
# aps_v3.5_rules.yaml
antipatterns:
  deprecated_rules:
    - id: OLD_DENY_TERM_123
      pattern: "antigua.*expresion"
      deprecated_since: "1.1"
      remove_in: "2.0"
      replacement: "Usar nueva expresión X"
```

---

## 7. Referencias

### Documentos relacionados

- **Esquema centralizado**: `aps-tooling/schemas/aps_v3.5_rules.yaml`
- **Vocabulario SID**: `aps-tooling/schemas/sid_vocabulary_v1.yaml`
- **Metodología APS**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Pipeline YAML**: `APS/YAML_PIPELINE_README.md`
- **Roadmap**: `APS/ROADMAP.md`

### Implementación

- **Linter v2**: `aps-tooling/scripts/yaml_lint_v2.py` (lee reglas desde schema)
- **Linter legacy**: `deprecated/code_old/yaml_lint.py` (reglas hardcoded, DEPRECATED)

---

## 8. FAQ

**P: ¿Qué pasa si mi agente necesita violar una regla justificadamente?**  
R: Usar campo `exemption` con `reason` documentado. Si es sistemático, proponer nueva categoría de exención.

**P: ¿Puedo añadir un término nuevo al vocabulario sin aprobación?**  
R: Sí, pero generará WARNING `UNKNOWN_TERM`. Para evitarlo, hacer PR a `sid_vocabulary_v1.yaml`.

**P: ¿Cómo sé si un DENY_TERM es falso positivo?**  
R: Revisar si el bloque es EXAMPLE/ANTIPATTERN o usa patrones de negación. Si no, probablemente es violación real.

**P: ¿Qué diferencia hay entre WARNING y ERROR?**  
R: ERROR bloquea integración (exit code 2). WARNING permite continuar pero requiere revisión (exit code 1).

**P: ¿Cómo evoluciono las reglas para APS v3.6?**  
R: Copiar `aps_v3.5_rules.yaml` → `aps_v3.6_rules.yaml`, modificar versión, actualizar linter para leer v3.6.

---

**Versión**: 1.0  
**Fecha**: 2025-11-19  
**APS Version**: v3.5  
**Próxima revisión**: Sprint 1 completado
