# SWARM J2C - Pipeline de Agentes

Sistema automatizado para gestión de agentes SWARM con SIDs determinísticos, conversión Markdown→YAML y enriquecimiento semántico.

## 🚀 Quick Start

```bash
# Ver todos los comandos disponibles
make help

# Pipeline completo (regenerar todo)
make all

# Limpiar y regenerar desde cero
make rebuild

# Ver estadísticas
make stats
```

## 📋 Comandos Principales

### Pipeline Completo

```bash
make all          # SID → extract → enrich → lint
make rebuild      # clean + all (regeneración total)
make ci           # Pipeline para CI/CD (falla si lint no pasa)
```

### Pasos Individuales

```bash
make sids         # Asignar SIDs determinísticos a .md
make extract      # Convertir .md → .yaml
make enrich       # Enriquecer YAMLs con atributos semánticos
make lint         # Validar archivos .md
```

### Desarrollo

```bash
make single AGENT=02-migration-motives        # Regenerar un agente específico
make validate-single AGENT=02-migration-motives  # Validar un agente
make watch        # Auto-regenerar al detectar cambios (requiere fswatch)
make diff         # Verificar sincronización MD ↔ YAML
```

### Utilidades

```bash
make clean        # Eliminar todos los YAMLs generados
make check        # Verificar que scripts existan
make stats        # Estadísticas de agentes
make pre-commit   # Hook para pre-commit
```

## 🔄 Workflow de Desarrollo

### 1. Editar un Agente

```bash
# Editar el Markdown fuente
vim swarm/agents/02-migration-motives.md

# Regenerar solo ese agente
make single AGENT=02-migration-motives

# O regenerar todo el swarm
make all
```

### 2. Validar Cambios

```bash
# Validar antes de commit
make lint

# O validar un agente específico
make validate-single AGENT=02-migration-motives
```

### 3. Pre-Commit

```bash
# Ejecutar antes de commit
make pre-commit

# Añadir cambios a git
git add swarm/agents/*.md swarm/agents/*.yaml
git commit -m "feat: actualizar agente 02-migration-motives"
```

## 📁 Estructura de Archivos

```
swarm/agents/
├── 01-orchestrator.md          # Fuente Markdown
├── 01-orchestrator.yaml        # Generado automáticamente
├── 02-migration-motives.md
├── 02-migration-motives.yaml
└── ...

code/
├── md_sid_assign.py            # Asignador de SIDs determinísticos
├── md2yaml.py                  # Conversor MD→YAML
├── enrich_yaml_with_llm.py     # Enriquecedor semántico
└── md_lint.py                  # Validador
```

## 🏗️ Sistema de SIDs Determinísticos

### Formato de SID

```
<PREFIJO>_<SLUG>_<HASH4>

Ejemplo: G_CAPTURAR_MOTIVACIONES_7B3F
```

### Prefijos por Sección

- `G_` → GOALS
- `C_` → CONSTRAINTS
- `P_` → PROTOCOLS
- `K_` → KEYWORDS
- `H_` → HEURISTICS
- `POL_` → POLICIES
- `I_` → INSTRUCTIONS
- `V_` → VARIABLES
- `OUT_` → OUTPUT
- `BLK_` → BLOCKS
- `L_` → LOOPS

### Anotación en Markdown

```markdown
## GOALS
- <!--sid:G_CAPTURAR_MOTIVACIONES_7B3F sha1=7b3f9e21-->
  Capturar las motivaciones principales de la migración
  <!--/sid-->
```

### Características

- **Determinístico**: Mismo texto → mismo SID
- **Idempotente**: Ejecutar múltiples veces produce el mismo resultado
- **Legible**: El SID incluye slug descriptivo
- **Único**: Hash evita colisiones
- **Versionable**: SHA1 detecta cambios en contenido

## 🔍 Validación (Lint)

El linter valida:

- ✅ Unicidad de SIDs por archivo
- ✅ Bloques obligatorios presentes (Entry Guard, STATE_JSON, Loop Contract, etc.)
- ✅ Deny-terms no presentes
- ✅ STATE_JSON siempre oculto en comentarios HTML
- ✅ STATE_JSON ≤ 1 KB
- ✅ Coherencia SHA1 con contenido

### Bloques Obligatorios

Todo agente DEBE tener:

1. `P_ENTRY_GUARD*` - Verificar active_agent
2. `POL_NO_SALTO*` - Política de OUTPUT (NO-SALTO-AUTOMÁTICO)
3. `P_STATEJSON*` - STATE_JSON en comentario HTML
4. `L_LOOP_CONTRACT*` - Loop Contract

### Deny-Terms

Términos prohibidos que el linter detecta:

- "cumplir heurística devolver" (anti-pattern)
- "handoff automático"
- "promoción automática"

## 📊 Enriquecimiento Semántico (YAML)

Cada bloque en el YAML generado incluye:

```yaml
Entry Guard (no responder si no soy el activo):
  block_type: BLK
  accion: verificar              # ← Atributo semántico
  relacion: control.active_agent # ← Atributo semántico
  nivel: guard                   # ← Atributo semántico
  sid: BLK.verificar.control.active_agent.guard  # ← SID generado
  content: "..."
```

### Atributos Semánticos

- **accion**: Verbo principal (verificar, capturar, generar, etc.)
- **relacion**: Con qué interactúa (usuario, control, estado, output, etc.)
- **nivel**: Tipo de operación (guard, protocol, workflow, template, etc.)
- **sid**: Identificador único semántico

## 🔧 Scripts Python

### `md_sid_assign.py`

Asigna SIDs determinísticos a ítems en Markdown.

```bash
# Un archivo
python3 code/md_sid_assign.py swarm/agents/02-migration-motives.md

# Batch
python3 code/md_sid_assign.py --batch "swarm/agents/*.md"

# Dry-run (simular sin escribir)
python3 code/md_sid_assign.py --dry-run swarm/agents/02-migration-motives.md
```

### `md2yaml.py`

Convierte Markdown a YAML estructurado.

```bash
python3 code/md2yaml.py swarm/agents/02-migration-motives.md swarm/agents/02-migration-motives.yaml
```

### `enrich_yaml_with_llm.py`

Enriquece YAMLs con atributos semánticos.

```bash
# Un archivo
python3 code/enrich_yaml_with_llm.py swarm/agents/02-migration-motives.yaml

# Batch
python3 code/enrich_yaml_with_llm.py --batch "swarm/agents/*.yaml"
```

### `md_lint.py`

Valida archivos Markdown.

```bash
# Un archivo
python3 code/md_lint.py swarm/agents/02-migration-motives.md

# Batch
python3 code/md_lint.py --batch "swarm/agents/*.md"

# Strict mode (warnings = errores)
python3 code/md_lint.py --strict --batch "swarm/agents/*.md"
```

## 🔄 Integración CI/CD

### GitHub Actions Ejemplo

```yaml
name: SWARM Pipeline

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Run CI pipeline
        run: make ci
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
make pre-commit || exit 1
```

## 📈 Estadísticas

```bash
make stats
```

Muestra:
- Total de archivos Markdown
- Total de archivos YAML
- Tamaño de cada YAML generado

## 🛠️ Troubleshooting

### Problema: "Script no encontrado"

```bash
make check  # Verifica que todos los scripts existan
chmod +x code/*.py
```

### Problema: "Lint falla"

```bash
# Ver errores específicos
python3 code/md_lint.py --batch "swarm/agents/*.md"

# Validar un agente específico
make validate-single AGENT=02-migration-motives
```

### Problema: "SIDs duplicados"

Los SIDs son determinísticos basados en hash del contenido. Si dos ítems tienen el mismo texto, el script añade sufijos `_A`, `_B`, etc.

### Problema: "YAML no sincronizado con MD"

```bash
# Verificar
make diff

# Regenerar
make extract
```

## 🎯 Mejores Prácticas

1. **Editar siempre el .md**, nunca el .yaml directamente
2. **Ejecutar `make all`** después de cambios importantes
3. **Validar con `make lint`** antes de commit
4. **Usar `make single`** para cambios en un solo agente (más rápido)
5. **Revisar `make diff`** para verificar sincronización
6. **Ejecutar `make pre-commit`** antes de git commit

## 📚 Recursos

- [Documento Maestro SWARM J2C](documento_maestro_j2c_swarm.md)
- [Decisiones Arquitectónicas](DECISIONES_ARQUITECTONICAS/)
- [Diagramas](DIAGRAMAS/)

---

**Última actualización**: 28 de octubre de 2025  
**Versión Pipeline**: 1.0.0
