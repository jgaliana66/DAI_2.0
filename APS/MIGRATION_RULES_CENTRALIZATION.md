# Migración: Reglas Hardcoded → Schema Centralizado

## 📋 Resumen

Este documento describe la migración de reglas APS v3.5 dispersas en código Python a una **fuente de verdad única** en `swarm/schemas/aps_v3.5_rules.yaml`.

### Problema Identificado

**Antes:**
```
code/yaml_lint.py        → DENY_TERMS hardcoded
code/md2yaml.py          → Block types hardcoded
code/enrich_yaml.py      → Vocabulario hardcoded
METODOLOGIA_*.md         → Reglas en prosa
```

❌ **Riesgo:** Al actualizar a APS v3.6:
- Tienes que modificar 4+ archivos diferentes
- Fácil olvidar actualizar alguno → inconsistencias
- Reglas duplicadas entre código y documentación
- No hay validación cruzada automática

**Después:**
```
swarm/schemas/aps_v3.5_rules.yaml  ← Fuente de verdad única
     ↓
code/yaml_lint.py       → Lee reglas del schema
code/md2yaml.py         → Lee reglas del schema
code/enrich_yaml.py     → Lee reglas del schema
```

✅ **Beneficio:** Al actualizar a APS v3.6:
- Modificas **UN SOLO archivo**: `aps_v3.6_rules.yaml`
- Todos los scripts se actualizan automáticamente
- Reglas versionadas (git diff claro)
- Validación automática del schema

---

## 🗂️ Archivos Creados

### 1. `swarm/schemas/aps_v3.5_rules.yaml`

**Fuente de verdad canónica** con todas las reglas:

```yaml
version: "3.5"
updated: "2025-11-19"

required_blocks:
  - name: "Entry Guard"
    patterns: [...]
    required_in: ["all"]

antipatterns:
  NO_AUTO_HANDOFF:
    patterns: ["handoff.*autom[áa]tic"]
    severity: "ERROR"
    rationale: "..."

vocabulary:
  actions:
    verificar:
      confidence: HIGH
      synonyms: ["comprobar", "validar"]
```

**Secciones:**
- `required_blocks`: Bloques obligatorios por tipo de agente
- `antipatterns`: DENY_TERMS con severidad y rationale
- `negation_patterns`: Contextos que indican descripción de antipatrón
- `exempt_block_types`: Tipos de bloque que no validan DENY_TERMS
- `vocabulary`: Vocabulario canónico para SIDs
- `heuristics`: Patrones de inferencia semántica
- `structural_validations`: Reglas estructurales (duplicados, formato SID)
- `state_json_protocol`: Protocolo de handoff
- `entry_guard`: Patrón de validación de entrada
- `loop_contract`: Política de recursión
- `reporting`: Configuración de reportes
- `compatibility`: Versionado y breaking changes
- `extensions`: Hooks para custom validators

### 2. `code/yaml_lint_v2.py`

**Linter refactorizado** que lee del schema:

```python
def load_aps_rules(schema_path: str = "swarm/schemas/aps_v3.5_rules.yaml") -> Dict:
    """Carga reglas APS desde el schema canónico."""
    with open(schema_path, 'r') as f:
        rules = yaml.safe_load(f)
    return rules

def validate_deny_terms(blocks: List[Dict], rules: Dict) -> List[str]:
    """Valida antipatrones usando reglas del schema."""
    antipatterns = rules.get('antipatterns', {})
    # ... usa antipatterns del schema
```

**Cambios clave:**
- `load_aps_rules()`: Carga schema al inicio
- Todas las funciones reciben `rules: Dict` como parámetro
- Fallback a `get_legacy_rules()` si schema no existe
- NO más reglas hardcoded

---

## 🔄 Plan de Migración

### Fase 1: Preparación (COMPLETADO ✅)

1. ✅ Crear `swarm/schemas/aps_v3.5_rules.yaml`
2. ✅ Crear `code/yaml_lint_v2.py` (lee del schema)
3. ✅ Documentar migración (este archivo)

### Fase 2: Testing (PENDIENTE)

```bash
# 1. Regenerar YAMLs de prueba
make extract

# 2. Probar linter v2 con reglas centralizadas
python3 code/yaml_lint_v2.py swarm/agents/J2C-v1-Swarm-v3-5/01-orchestrator.yaml

# 3. Comparar outputs v1 vs v2
python3 code/yaml_lint.py archivo.yaml > output_v1.txt
python3 code/yaml_lint_v2.py archivo.yaml > output_v2.txt
diff output_v1.txt output_v2.txt

# 4. Validar que los resultados sean idénticos
```

### Fase 3: Migración de Scripts (PENDIENTE)

**Actualizar cada script para leer del schema:**

#### `code/md2yaml.py`
```python
# ANTES (hardcoded)
BLOCK_TYPES = {
    'EXAMPLE': ['[EXAMPLE]', '[EJEMPLO]'],
    'ANTIPATTERN': ['[ANTIPATRÓN]', '[ANTIPATTERN]']
}

# DESPUÉS (desde schema)
def load_block_type_markers():
    rules = load_aps_rules()
    return rules.get('block_type_markers', {})
```

#### `code/enrich_yaml_with_llm.py`
```python
# ANTES (hardcoded)
VOCABULARY = {
    'verificar': {'synonyms': ['comprobar', 'validar']},
    'detectar': {'synonyms': ['identificar']}
}

# DESPUÉS (desde schema)
def load_vocabulary():
    rules = load_aps_rules()
    return rules['vocabulary']['actions']
```

### Fase 4: Extensiones Personalizadas (FUTURO)

Permitir overrides en `swarm/schemas/custom_vocabulary.yaml`:

```yaml
# Extiende aps_v3.5_rules.yaml
extends: "aps_v3.5_rules.yaml"

# Override/añadir vocabulario custom
vocabulary:
  actions:
    # Nuevo verbo específico del proyecto
    sincronizar:
      confidence: HIGH
      synonyms: ["sync", "actualizar"]
```

---

## 📊 Comparación: Antes vs Después

### Actualizar Regla DENY_TERMS

**ANTES (disperso):**
```python
# 1. Modificar code/yaml_lint.py
DENY_TERMS = [
    r'handoff.*autom[áa]tic',
    r'nuevo_antipatron'  # ← AÑADIR AQUÍ
]

# 2. Modificar METODOLOGIA_SWARM_*.md
## Antipatrones
- NO hacer handoff automático
- NO usar nuevo_antipatron  # ← DOCUMENTAR AQUÍ

# 3. Modificar tests (si existen)
def test_deny_terms():
    assert detect('nuevo_antipatron') == True  # ← AÑADIR TEST

# 4. Actualizar CHANGELOG.md
# v3.6.0
- Añadido antipatrón: nuevo_antipatron  # ← DOCUMENTAR CAMBIO
```

**DESPUÉS (centralizado):**
```yaml
# swarm/schemas/aps_v3.6_rules.yaml
antipatterns:
  NO_AUTO_HANDOFF:
    patterns: ["handoff.*autom[áa]tic"]
    severity: "ERROR"
  
  # ← SOLO AÑADIR AQUÍ
  NUEVO_ANTIPATRON:
    patterns: ["nuevo_antipatron"]
    severity: "ERROR"
    rationale: "Explicación de por qué está prohibido"
```

✅ **Resultado:**
- 1 solo archivo modificado
- Autodocumentado (rationale incluido)
- Git diff claro: `+4 lines` en `aps_v3.6_rules.yaml`
- Todos los scripts se actualizan automáticamente

---

## 🔧 Herramientas de Validación

### Validar Schema

```bash
# Verificar que el schema es YAML válido
python3 -c "import yaml; yaml.safe_load(open('swarm/schemas/aps_v3.5_rules.yaml'))"

# Validar contra JSON Schema (futuro)
python3 scripts/validate_aps_schema.py swarm/schemas/aps_v3.5_rules.yaml
```

### Diff entre Versiones

```bash
# Comparar APS v3.5 vs v3.6
diff swarm/schemas/aps_v3.5_rules.yaml swarm/schemas/aps_v3.6_rules.yaml

# Ver qué cambió
git diff v3.5..v3.6 -- swarm/schemas/aps_v3.*.yaml
```

---

## 🎯 Beneficios Concretos

### 1. Versionado Claro
```bash
swarm/schemas/
├── aps_v3.3_rules.yaml
├── aps_v3.4_rules.yaml
├── aps_v3.5_rules.yaml
└── aps_v3.6_rules.yaml  # Futuro
```

### 2. Backward Compatibility
```python
# Soportar múltiples versiones simultáneamente
rules_v35 = load_aps_rules("swarm/schemas/aps_v3.5_rules.yaml")
rules_v36 = load_aps_rules("swarm/schemas/aps_v3.6_rules.yaml")

# Validar YAML legacy con reglas antiguas
lint_yaml_file("old_agent.yaml", rules=rules_v35)
```

### 3. Extensibilidad
```yaml
# Proyecto interno puede extender reglas base
# swarm/schemas/internal_rules.yaml
extends: "aps_v3.5_rules.yaml"

antipatterns:
  # Regla específica del proyecto
  NO_DB_DIRECT:
    patterns: ["query.*database.*direct"]
    severity: "ERROR"
```

### 4. Testing Automatizado
```python
def test_all_antipatterns_have_rationale():
    """Verifica que todos los antipatrones estén documentados."""
    rules = load_aps_rules()
    for name, config in rules['antipatterns'].items():
        assert 'rationale' in config, f"Antipatrón {name} sin rationale"
        assert len(config['rationale']) > 0
```

---

## 📚 Próximos Pasos

### Inmediato (cuando regeneres YAMLs)

1. **Probar linter v2:**
   ```bash
   python3 code/yaml_lint_v2.py swarm/agents/**/*.yaml
   ```

2. **Comparar con v1:**
   ```bash
   diff <(python3 code/yaml_lint.py file.yaml) \
        <(python3 code/yaml_lint_v2.py file.yaml)
   ```

3. **Si son idénticos → migrar:**
   ```bash
   mv code/yaml_lint.py code/yaml_lint_legacy.py
   mv code/yaml_lint_v2.py code/yaml_lint.py
   ```

### Corto Plazo

1. **Migrar md2yaml.py** para leer block_types del schema
2. **Migrar enrich_yaml_with_llm.py** para leer vocabulario del schema
3. **Crear schema validator** (JSON Schema o custom)

### Largo Plazo

1. **APS v3.6 planning:**
   - Copiar `aps_v3.5_rules.yaml` → `aps_v3.6_rules.yaml`
   - Modificar solo el nuevo archivo
   - Mantener v3.5 para backward compatibility

2. **Custom extensions:**
   - Permitir `custom_vocabulary.yaml` por proyecto
   - Merge strategy configurable

3. **CI/CD integration:**
   - Validar schema en cada commit
   - Detectar breaking changes automáticamente

---

## ⚠️ Advertencias

### Riesgo de Desincronización

**Problema:** Si alguien modifica `code/yaml_lint.py` directamente (hardcoded) en lugar de actualizar el schema.

**Solución:**
```python
# Añadir check al inicio de cada script
def check_rules_source():
    """Verifica que no haya reglas hardcoded."""
    if HARDCODED_RULES_DETECTED:
        raise DeprecationWarning(
            "⚠️ Este script tiene reglas hardcoded.\n"
            "Migrar a swarm/schemas/aps_v3.5_rules.yaml"
        )
```

### Legacy Code

Mantener `get_legacy_rules()` para:
- Backward compatibility si el schema no existe
- Debugging (comparar old vs new)
- Tests que validen migración

---

## 📖 Referencias

- **Schema canónico:** `swarm/schemas/aps_v3.5_rules.yaml`
- **Linter v2:** `code/yaml_lint_v2.py`
- **Metodología APS:** `METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Pipeline docs:** `AGENTE_YAML_PIPELINE.md`

---

## ✅ Checklist de Migración

- [x] Crear schema canónico (`aps_v3.5_rules.yaml`)
- [x] Refactorizar linter para leer del schema
- [x] Documentar migración (este archivo)
- [ ] Testing: Comparar yaml_lint v1 vs v2
- [ ] Migrar md2yaml.py
- [ ] Migrar enrich_yaml_with_llm.py
- [ ] Crear schema validator
- [ ] Actualizar CI/CD para validar schema
- [ ] Deprecar reglas hardcoded
- [ ] Documentar en README principal

---

**Versión**: 1.0  
**Fecha**: 2025-11-19  
**Estado**: 🚧 En progreso (pendiente testing)
