# APS Tooling v2.0

Tooling centralizado para **APS v3.5** (Agent Prompt Standard).

Consolida todas las herramientas, bibliotecas y schemas para trabajar con agentes en formato Markdown y YAML siguiendo el estándar APS v3.5.

---

## 📂 Estructura

```
aps-tooling/
├── schemas/              # Schemas YAML y vocabulario
│   ├── aps_v3.5_rules.yaml
│   └── sid_vocabulary_v1.yaml
├── scripts/              # Scripts del pipeline
│   ├── md_sid_assign.py
│   ├── md2yaml.py
│   ├── enrich_yaml_with_llm.py
│   ├── yaml_lint_v2.py
│   ├── yaml_pipeline_cli.py
│   └── ...
├── lib/                  # Bibliotecas reutilizables
│   ├── vocabulary_loader.py
│   ├── confidence_system.py
│   ├── yaml_editor.py
│   └── schema_validator.py
├── tests/                # Tests unitarios
└── README.md             # Este archivo
```

---

## 🚀 Quick Start

### Uso básico del pipeline

```bash
# Pipeline completo (desde el raíz del proyecto)
make all

# Regenerar un agente específico
make single AGENT=02-migration-motives

# Validación
make lint
```

### Uso de bibliotecas en Python

```python
from aps_tooling.lib import VocabularyLoader, YAMLBlockEditor

# Cargar vocabulario
vocab = VocabularyLoader()
print(vocab.get_acciones_permitidas())

# Editar YAML con AST
editor = YAMLBlockEditor('agent.yaml')
editor.load()
editor.set_field('blocks.BLK-001.sid', 'verificar.control.guard')
editor.save()
```

---

## 📚 Bibliotecas (`lib/`)

### 1. `vocabulary_loader.py` - Gestión de Vocabulario SID

Carga y valida el vocabulario canónico de SIDs desde `sid_vocabulary_v1.yaml`.

**Características:**
- Carga automática del vocabulario versionado
- Métodos para acciones, relaciones y niveles (permitidos/deprecated)
- Mapping de sinónimos → forma canónica
- Validación completa de componentes SID

**Ejemplo:**

```python
from aps_tooling.lib.vocabulary_loader import VocabularyLoader

vocab = VocabularyLoader()

# Obtener acciones permitidas
acciones = vocab.get_acciones_permitidas()  # ['verificar', 'capturar', ...]

# Validar componentes
result = vocab.validate_sid_components('verificar', 'control', 'guard')
if result['errors']:
    print("Errores:", result['errors'])
if result['warnings']:
    print("Warnings:", result['warnings'])

# Mapping de sinónimos
canonical = vocab.get_canonical_accion('chequear')  # → 'verificar'

# Obtener sinónimos
sinonimos = vocab.get_sinonimos_accion('verificar')  # → ['chequear', 'validar']
```

**API completa:**
- `get_acciones_permitidas() → List[str]`
- `get_relaciones_permitidas() → List[str]`
- `get_niveles_permitidos() → List[str]`
- `is_accion_permitida(accion: str) → bool`
- `is_accion_deprecated(accion: str) → bool`
- `get_canonical_accion(accion: str) → Optional[str]`
- `get_sinonimos_accion(accion: str) → List[str]`
- `validate_sid_components(accion, relacion, nivel) → Dict`

---

### 2. `confidence_system.py` - Sistema de Confianza

Clasifica inferencias semánticas con niveles de confianza: **HIGH**, **MEDIUM**, **LOW**.

**Características:**
- Triple verificación: vocabulario → sinónimos → heurística
- Evaluación por componente y global
- Metadata para YAML (confidence, inference_method, inference_note)

**Ejemplo:**

```python
from aps_tooling.lib.confidence_system import ConfidenceSystem, ConfidenceLevel

cs = ConfidenceSystem()

# Evaluar acción
confidence, method, note = cs.evaluate_accion('verificar', 'Verificar el estado')
print(f"Confianza: {confidence.value}")  # → HIGH

# Evaluar SID completo
evaluation = cs.evaluate_sid_complete(
    accion='verificar',
    relacion='control.active_agent',
    nivel='guard',
    content='Verificar que el agente activo es correcto',
    block_type='BLK'
)

print(f"Confianza global: {evaluation['overall_confidence'].value}")
print(f"¿Requiere revisión? {evaluation['should_review']}")

# Formatear para metadata YAML
metadata = cs.format_metadata(evaluation)
# → {'confidence': 'HIGH', 'inference_method': 'vocabulary'}
```

**API completa:**
- `evaluate_accion(accion, content) → (ConfidenceLevel, str, Optional[str])`
- `evaluate_relacion(relacion, content) → (ConfidenceLevel, str, Optional[str])`
- `evaluate_nivel(nivel, block_type) → (ConfidenceLevel, str, Optional[str])`
- `evaluate_sid_complete(...) → Dict`
- `format_metadata(evaluation) → Dict`

---

### 3. `yaml_editor.py` - Editor YAML basado en AST

**⚠️ REEMPLAZO OFICIAL DE**: `replace_string_in_file` (DEPRECATED)

Editor YAML que usa Abstract Syntax Tree para manipulación semántica segura.

**Ventajas:**
- ✅ Preserva estructura YAML
- ✅ Evita corrupciones por indentación
- ✅ Manipulación semántica segura
- ✅ Validación automática
- ✅ Backups automáticos

**Ejemplo:**

```python
from aps_tooling.lib.yaml_editor import YAMLBlockEditor

# Editar un archivo
editor = YAMLBlockEditor('agent.yaml')
editor.load()

# Obtener campo
sid = editor.get_field('blocks.BLK-001.sid')

# Modificar campo
editor.set_field('blocks.BLK-001.sid', 'verificar.control.guard')

# Añadir bloque
editor.add_block('BLK-002', {
    'sid': 'capturar.input.task',
    'content': 'Capturar datos'
})

# Guardar (con backup automático)
editor.save(backup=True)  # Crea agent.yaml.bak
```

**API completa:**
- `load() → Dict`
- `save(backup: bool = True) → None`
- `get_field(path: str) → Any`
- `set_field(path: str, value: Any) → None`
- `delete_field(path: str) → bool`
- `add_block(block_id: str, block_data: Dict) → None`
- `get_all_blocks() → Dict[str, Dict]`
- `update_block_sid(block_id: str, new_sid: str) → bool`
- `get_blocks_by_sid_pattern(pattern: str) → List[str]`
- `validate_structure() → List[str]`

**Editor por lotes:**

```python
from aps_tooling.lib.yaml_editor import YAMLBatchEditor

batch = YAMLBatchEditor(['agent1.yaml', 'agent2.yaml'])
batch.apply_to_all(lambda editor: editor.set_field('version', '3.5'))
batch.save_all()
```

---

### 4. `schema_validator.py` - Validador de Schemas

Valida archivos YAML contra schemas JSON Schema y realiza validaciones específicas APS.

**Características:**
- Validación contra schema JSON Schema (Draft 7)
- Validación de SIDs únicos
- Validación de componentes en vocabulario
- Reportes detallados con rutas JSON
- Modo batch para múltiples archivos

**Ejemplo básico:**

```python
from aps_tooling.lib.schema_validator import SchemaValidator

validator = SchemaValidator()  # Usa aps_agent_schema_v1.yaml por defecto

# Validar archivo
report = validator.validate_with_report('agent.yaml')
if report['valid']:
    print("✅ VÁLIDO")
else:
    print(f"❌ {report['error_count']} errores")
    for error in report['formatted_errors']:
        print(f"  - {error}")
```

**Validación APS completa:**

```python
from aps_tooling.lib.schema_validator import APSValidator

aps_validator = APSValidator()

# Validación completa: schema + SIDs + vocabulario
report = aps_validator.validate_full('agent.yaml')

print(f"✅ Válido: {report['valid']}")
print(f"Schema errors: {len(report['schema_errors'])}")
print(f"SIDs duplicados: {len(report['duplicate_sids'])}")
print(f"Errores vocabulario: {len(report['vocabulary_errors'])}")

# Validar por lotes
reports = aps_validator.validate_batch(['agent1.yaml', 'agent2.yaml'])
for report in reports:
    aps_validator.print_validation_report(report)
```

**API completa:**
- `load_schema() → Dict`
- `validate_data(data: Dict) → List[Dict]`
- `validate_file(filepath: str) → List[Dict]`
- `validate_with_report(filepath: str) → Dict`
- `validate_batch(filepaths: List[str]) → List[Dict]`
- `print_validation_report(report: Dict) → None`

**APSValidator adicional:**
- `validate_sids_unique(data: Dict) → List[str]`
- `validate_sid_components(data: Dict) → List[Dict]`
- `validate_full(filepath: str) → Dict`

---

## 🛠️ Scripts (`scripts/`)

### 1. `md_sid_assign.py` - Asignación de SIDs

Asigna SIDs determinísticos a bloques Markdown.

**Uso:**
```bash
# Asignar SIDs a un archivo
python3 aps-tooling/scripts/md_sid_assign.py agent.md

# Modo batch
python3 aps-tooling/scripts/md_sid_assign.py --batch ".github/agents/*.md"
```

**Algoritmo:** `slugify(contenido) + SHA1(contenido)[:8]`

---

### 2. `md2yaml.py` - Conversión MD → YAML

Convierte archivos Markdown a YAML estructurado.

**Uso:**
```bash
python3 aps-tooling/scripts/md2yaml.py input.md output.yaml
```

**Extrae:**
- Metadata YAML (frontmatter)
- Bloques de código con SIDs
- Estructura jerárquica

---

### 3. `enrich_yaml_with_llm.py` - Enriquecimiento Semántico

Añade atributos semánticos (SIDs, confidence, inference_method) usando heurística.

**Uso:**
```bash
# Enriquecer un archivo
python3 aps-tooling/scripts/enrich_yaml_with_llm.py agent.yaml

# Modo batch
python3 aps-tooling/scripts/enrich_yaml_with_llm.py --batch ".github/agents/*.yaml"
```

**Añade:**
- `sid`: Identificador semántico (accion.relacion.nivel)
- `confidence`: HIGH | MEDIUM | LOW
- `inference_method`: vocabulary | synonym_mapping | heuristic_pattern | semantic_similarity
- `inference_note`: Notas explicativas

---

### 4. `yaml_lint_v2.py` - Validación YAML

Valida estructura, SIDs, bloques obligatorios y deny-terms.

**Uso:**
```bash
# Validar un archivo
python3 aps-tooling/scripts/yaml_lint_v2.py agent.yaml

# Modo batch
python3 aps-tooling/scripts/yaml_lint_v2.py --batch ".github/agents/*.yaml"

# Salida JSON
python3 aps-tooling/scripts/yaml_lint_v2.py agent.yaml --json
```

**Valida:**
- ✅ Estructura YAML válida
- ✅ SIDs únicos
- ✅ Componentes SID en vocabulario
- ✅ Bloques obligatorios presentes
- ✅ Ausencia de deny-terms
- ✅ Referencias válidas

---

### 5. `yaml_pipeline_cli.py` - Pipeline Unificado

CLI que ejecuta todo el pipeline: SID assignment → MD→YAML → Enrich → Lint

**Uso:**
```bash
# Pipeline completo para un archivo
python3 aps-tooling/scripts/yaml_pipeline_cli.py agent.md

# Modo batch
python3 aps-tooling/scripts/yaml_pipeline_cli.py --batch ".github/agents/*.md"

# Modo CI (salida JSON)
python3 aps-tooling/scripts/yaml_pipeline_cli.py --batch ".github/agents/*.md" --ci-mode
```

**Exit codes:**
- `0` - Éxito
- `1` - Warnings (no falla en CI)
- `2` - Errores
- `4` - Errores de seguridad (deny-terms)

---

## 📋 Schemas (`schemas/`)

### 1. `sid_vocabulary_v1.yaml` - Vocabulario SID

Vocabulario canónico versionado con 35 acciones, 24 relaciones y 13 niveles.

**Estructura:**
```yaml
version: "1.0"
aps_version: "3.5"

acciones:
  permitidas:
    - verificar
    - capturar
    - generar
    # ...
  
  sinonimos:
    verificar: [chequear, validar, comprobar]
    # ...
  
  deprecated:
    - auto-transfer

relaciones:
  permitidas:
    - control
    - input
    - output
    # ...

niveles:
  permitidos:
    - guard
    - task
    - loop
    # ...
```

**Changelog interno:** Registra cambios entre versiones.

---

### 2. `aps_v3.5_rules.yaml` - Reglas APS v3.5

Reglas centralizadas de validación:
- Bloques obligatorios
- Deny-terms
- Patrones de validación
- Severidades (ERROR, WARNING, INFO)

**Referencia completa:** Ver `APS/LINTER_RULES.md`

---

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests
python3 -m pytest aps-tooling/tests/

# Con cobertura
python3 -m pytest aps-tooling/tests/ --cov=aps-tooling
```

### Estructura de tests

```
aps-tooling/tests/
├── test_vocabulary_loader.py
├── test_confidence_system.py
├── test_yaml_editor.py
└── test_schema_validator.py
```

---

## 📖 Documentación Adicional

- **Metodología APS v3.5**: `../APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Pipeline README**: `../APS/YAML_PIPELINE_README.md`
- **Especificación del Agente**: `../APS/AGENTE_YAML_PIPELINE.md`
- **Reglas del Linter**: `../APS/LINTER_RULES.md`
- **Best Practice YAML**: `../APS/YAML_AST_BEST_PRACTICE.md`
- **Roadmap de mejoras**: `../APS/ROADMAP.md`

---

## 🔄 Migración desde versión anterior

Si vienes de la estructura anterior (`code/`, `swarm/`), lee esta sección:

### Cambios de rutas

| Antiguo | Nuevo |
|---------|-------|
| `code/*.py` | `aps-tooling/scripts/*.py` |
| `swarm/schemas/*.yaml` | `aps-tooling/schemas/*.yaml` |
| `swarm/agents/*` | `.github/agents/*` |

### Cambios de API

#### ❌ DEPRECATED: `replace_string_in_file`

```python
# ❌ NO USAR
replace_string_in_file('agent.yaml', 'old_sid', 'new_sid')
```

#### ✅ USAR: `YAMLBlockEditor` (AST)

```python
# ✅ MÉTODO OFICIAL
from aps_tooling.lib.yaml_editor import YAMLBlockEditor

editor = YAMLBlockEditor('agent.yaml')
editor.load()
editor.set_field('blocks.BLK-001.sid', 'new_sid')
editor.save()
```

### Actualizar imports

```python
# ❌ Antiguo
from code.some_script import helper

# ✅ Nuevo
from aps_tooling.scripts.some_script import helper
from aps_tooling.lib import VocabularyLoader, YAMLBlockEditor
```

---

## 🤝 Contribuir

1. Edita solo archivos `.md` en `.github/agents/`
2. Ejecuta `make single AGENT=nombre` o `make rebuild`
3. Valida con `make lint`
4. Commit con `make pre-commit`

Ver `../CONTRIBUTING.md` para detalles completos.

---

## 📞 Soporte

- **Documentación completa**: `../APS/README.md`
- **Issues**: Abre un issue en GitHub
- **Bitácora histórica**: `../APS/history/BITACORA_APS_v3.5.md`

---

**Versión**: 2.0.0  
**APS Version**: 3.5  
**Última actualización**: 19/11/2025
