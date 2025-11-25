---
description: Genera SIDs semánticos reales para agentes SWARM APS v3.5
---

# SID Generator Agent

Reemplaza placeholders temporales (`TEMP_XXX_NNN`, `<<PENDING_AI>>`) con SIDs semánticos coherentes según metodología APS v3.5.

## Entrada esperada

$ARGUMENTS

Usuario proporciona:
- Ruta al archivo YAML con placeholders: `.github/agents/02-migration-motives.yaml`
- O solicita procesar todos los YAMLs del SWARM

## Proceso de enriquecimiento semántico

### 1. Leer YAML con placeholders

```yaml
Entry Guard (no responder si no soy el activo):
  block_type: BLK
  accion: <<PENDING_AI>>
  relacion: <<PENDING_AI>>
  nivel: <<PENDING_AI>>
  sid: TEMP_BLK_001
  content: "Verificar control.active_agent antes de responder..."
```

### 2. Analizar semántica del bloque

**Consulta el vocabulario de referencia:**
Lee el diccionario semántico estándar desde:
```
aps-tooling/schemas/sid_vocabulary_v1.yaml
```

Este archivo contiene:
- **Acciones** organizadas por categoría (control, flujo, datos, output, validación, estructura, restricción, recuperación, interpretación)
- **Relaciones** organizadas por dominio (control, estado, usuario, fase, arquitectura, flujo, agente, output, informe, variables, otros)
- **Niveles** organizados por tipo (validación, flujo, estructura, restricción)

**Si el bloque usa términos no catalogados:**
- Infiere la semántica del contenido del bloque
- Usa el vocabulario como referencia, no como límite estricto
- Mantén coherencia con el estilo de los términos existentes

**Proceso de análisis:**

Para cada bloque con placeholders, analizar:

**Acción** (verbo principal):
- Identifica la acción principal del bloque (ej: verificar, capturar, generar, detectar, prohibir)
- Consulta categorías: control, flujo, datos, output, validación, estructura, restricción, recuperación, interpretación

**Relación** (con qué interactúa):
- Identifica el objeto/entidad con la que interactúa (ej: control.active_agent, usuario, estado, fase)
- Usa dot-notation para relaciones compuestas (ej: usuario.confirmacion, flujo.handoff)
- Consulta dominios: control, estado, usuario, fase, arquitectura, flujo, agente, output, informe, variables, otros

**Nivel** (tipo de operación):
- Identifica el tipo de operación (ej: guard, protocol, workflow, template, constraint)
- Consulta tipos: validación, flujo, estructura, restricción

### 3. Generar SID semántico

**Formato**: `<TYPE>.<accion>.<relacion>.<nivel>`

**Ejemplo**:
```yaml
Entry Guard (no responder si no soy el activo):
  block_type: BLK
  accion: verificar
  relacion: control.active_agent
  nivel: guard
  sid: BLK.verificar.control.active_agent.guard
  content: "Verificar control.active_agent antes de responder..."
```

### 4. Validar coherencia

- **Unicidad**: No duplicar SIDs en el mismo archivo
- **Coherencia**: SID debe reflejar el contenido real del bloque
- **Formato**: Seguir estructura `<TYPE>.<accion>.<relacion>.<nivel>`
- **Políticas APS**: Respetar bloques obligatorios (Entry Guard, NO-SALTO-AUTOMÁTICO, STATE_JSON, Loop Contract)

## Catálogo de SIDs comunes por tipo de bloque

### BLK (Bloques generales)
- `BLK.verificar.control.active_agent.guard` - Entry Guard
- `BLK.presentar.fase.introduccion.template` - Presentación inicial
- `BLK.declarar.variables.disponibles.reference` - Variables disponibles

### GOAL (Objetivos)
- `GOAL.capturar.motivaciones.workflow` - Capturar motivaciones
- `GOAL.analizar.contexto.workflow` - Analizar contexto
- `GOAL.generar.requisitos.workflow` - Generar requisitos

### CONST (Constraints/Restricciones)
- `CONST.prohibir.handoff.automatico.constraint` - No handoff automático
- `CONST.validar.confirmacion.protocol` - Requerir confirmación

### POL (Políticas)
- `POL.controlar.output.markdown.policy` - Política de salida Markdown
- `POL.ocultar.statejson.comentario.policy` - STATE_JSON oculto

### P (Protocolos)
- `P.definir.statejson.estructura.protocol` - Definir STATE_JSON
- `P.inicializar.contrato.loop.initialization` - Loop Contract

### OUT (Output/Salida)
- `OUT.generar.markdown.template` - Template de salida
- `OUT.validar.confirmacion.usuario.validation` - Validación de confirmación

### H (Heurísticas)
- `H.detectar.completitud.covered.conditional` - Detectar completitud
- `H.sugerir.handoff.siguiente.conditional` - Sugerir siguiente agente

## Reglas específicas APS v3.5

### Bloques obligatorios

Todo agente DEBE tener:
1. **Entry Guard**: `BLK.verificar.control.active_agent.guard`
2. **NO-SALTO-AUTOMÁTICO**: `POL.controlar.output.markdown.policy`
3. **STATE_JSON**: `P.definir.statejson.estructura.protocol`
4. **Loop Contract**: `P.inicializar.contrato.loop.initialization`

### Términos prohibidos en contenido

Detectar y marcar como error si aparecen:
- "devuelve control al cumplir heurística" (anti-pattern)
- "handoff automático"
- "promoción automática"

### Coherencia semántica

- Si bloque habla de "verificar active_agent" → `accion: verificar`, `relacion: control.active_agent`
- Si bloque define STATE_JSON → `accion: definir`, `relacion: estado`
- Si bloque presenta plantilla → `accion: presentar`, `nivel: template`

## Salida esperada

YAML completo con todos los placeholders reemplazados:

```yaml
agent:
  name: Migration Motives
  blocks:
    Entry Guard (no responder si no soy el activo):
      block_type: BLK
      accion: verificar
      relacion: control.active_agent
      nivel: guard
      sid: BLK.verificar.control.active_agent.guard
      content: "..."
    
    GOALS:
      block_type: GOAL
      accion: capturar
      relacion: motivaciones
      nivel: workflow
      sid: GOAL.capturar.motivaciones.workflow
      content: "..."
```

## Validación post-generación

Después de generar SIDs, validar:

```bash
# Usuario ejecuta en terminal
make lint
```

Si hay errores:
- Duplicados de SID → ajustar semántica
- Bloques faltantes → añadir en .md fuente
- Términos prohibidos → corregir contenido

## Casos especiales

### Bloques con múltiples acciones

Si un bloque realiza varias acciones, usar la acción principal:
```yaml
# Bloque que "captura y clasifica motivaciones"
sid: GOAL.capturar.motivaciones.workflow  # Acción principal = capturar
```

### Relaciones compuestas

Usar dot-notation para relaciones anidadas:
```yaml
relacion: usuario.confirmacion.explicita
relacion: flujo.handoff.condicional
relacion: estado.covered.items
```

### SIDs largos

Formato permite 4+ partes:
```yaml
sid: BLK.verificar.control.active_agent.guard.strict
sid: GOAL.capturar.stakeholder.requisitos.extracto
```

## Contrato de salida

1. **Reemplazar TODOS los placeholders** (`<<PENDING_AI>>` y `TEMP_XXX_NNN`)
2. **Preservar estructura YAML** (no modificar `block_type`, `content`)
3. **Generar SIDs únicos** (no duplicados en el archivo)
4. **Validar coherencia** semántica con contenido
5. **Respetar bloques obligatorios** APS v3.5

## Ejemplo completo de transformación

**Antes (con placeholders)**:
```yaml
Entry Guard (no responder si no soy el activo):
  block_type: BLK
  accion: <<PENDING_AI>>
  relacion: <<PENDING_AI>>
  nivel: <<PENDING_AI>>
  sid: TEMP_BLK_001
  content: "Antes de responder, verifica control.active_agent === 'J2Ci-Migration_Motives'"

GOALS:
  block_type: GOAL
  accion: <<PENDING_AI>>
  relacion: <<PENDING_AI>>
  nivel: <<PENDING_AI>>
  sid: TEMP_GOAL_002
  content: "Capturar las motivaciones principales de la migración"
```

**Después (SIDs semánticos)**:
```yaml
Entry Guard (no responder si no soy el activo):
  block_type: BLK
  accion: verificar
  relacion: control.active_agent
  nivel: guard
  sid: BLK.verificar.control.active_agent.guard
  content: "Antes de responder, verifica control.active_agent === 'J2Ci-Migration_Motives'"

GOALS:
  block_type: GOAL
  accion: capturar
  relacion: motivaciones
  nivel: workflow
  sid: GOAL.capturar.motivaciones.workflow
  content: "Capturar las motivaciones principales de la migración"
```
