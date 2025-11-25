# Manipulación de YAML mediante AST (Dict) - Best Practice

## 🎯 Problema: String-Replace es Frágil

### Ejemplo del Problema

**YAML original:**
```yaml
Entry Guard:
  block_type: BLK
  accion: <<PENDING_AI>>
  sid: TEMP_BLK_001
  content: "Verificar control..."
```

**Intento de modificar con string-replace:**
```python
# ❌ FRÁGIL: Depende de formato exacto
replace_string_in_file(
    filePath="file.yaml",
    oldString="""Entry Guard:
  block_type: BLK
  accion: <<PENDING_AI>>
  sid: TEMP_BLK_001""",
    newString="""Entry Guard:
  block_type: BLK
  accion: verificar
  sid: BLK.verificar.control.active_agent.guard"""
)
```

**¿Qué pasa si el YAML se regenera así?**
```yaml
Entry Guard:
  sid: TEMP_BLK_001          # ← Orden diferente
  block_type: BLK
  accion: <<PENDING_AI>>
  content: "Verificar control..."
```

❌ **El replace falla** porque el patrón no coincide exactamente.

---

## ✅ Solución: Manipular como Dict (AST)

### Flujo Robusto

```python
import yaml

# PASO 1: Cargar YAML como estructura de datos
with open("file.yaml", 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# PASO 2: Recorrer bloques (dict)
blocks = data.get("agent", {}).get("blocks", {})

for block_name, block in blocks.items():
    # block es un dict con claves conocidas
    
    # PASO 3: Modificar campos directamente
    if block.get("accion") == "<<PENDING_AI>>":
        block["accion"] = "verificar"
        block["relacion"] = "control.active_agent"
        block["nivel"] = "guard"
        block["sid"] = "BLK.verificar.control.active_agent.guard"

# PASO 4: Volcar YAML actualizado
with open("file.yaml", 'w', encoding='utf-8') as f:
    yaml.safe_dump(data, f, 
                   default_flow_style=False,
                   allow_unicode=True,
                   sort_keys=False)  # ← Mantener orden
```

### Beneficios

| Aspecto | String-Replace | AST (Dict) |
|---------|---------------|------------|
| **Indentación** | Debe coincidir exacto | ✅ Inmune |
| **Orden de claves** | Debe coincidir exacto | ✅ Inmune |
| **Espacios/saltos** | Debe coincidir exacto | ✅ Inmune |
| **Regeneración YAML** | ❌ Rompe el patrón | ✅ Sigue funcionando |
| **Validación previa** | ❌ Difícil | ✅ Fácil (validar dict) |
| **Matches accidentales** | ⚠️ Riesgo | ✅ Solo modifica clave exacta |
| **Mantenibilidad** | ❌ Frágil | ✅ Robusto |

---

## 📋 Implementación en el Pipeline

### Función Auxiliar para Enriquecimiento

```python
def enrich_yaml_block(yaml_path: str, block_name: str, enrichments: dict) -> bool:
    """
    Enriquece un bloque YAML manipulando el dict directamente.
    
    Args:
        yaml_path: Ruta al archivo YAML
        block_name: Nombre del bloque a modificar
        enrichments: Dict con campos a actualizar {
            "accion": "verificar",
            "relacion": "control.active_agent",
            "nivel": "guard",
            "sid": "BLK.verificar.control.active_agent.guard",
            "confidence": "HIGH"
        }
    
    Returns:
        True si se modificó, False si no se encontró el bloque
    """
    # 1. Cargar YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # 2. Verificar estructura
    if "agent" not in data or "blocks" not in data["agent"]:
        raise ValueError(f"YAML malformado: falta estructura agent.blocks")
    
    blocks = data["agent"]["blocks"]
    
    # 3. Buscar bloque
    if block_name not in blocks:
        return False
    
    block = blocks[block_name]
    
    # 4. Validar antes de modificar
    validate_enrichments(block, enrichments)
    
    # 5. Aplicar enriquecimientos
    for field, value in enrichments.items():
        block[field] = value
    
    # 6. Metadata de auditoría
    block["enriched_at"] = datetime.now().isoformat()
    block["enriched_by"] = "@yaml-pipeline"
    
    # 7. Volcar YAML actualizado
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f,
                       default_flow_style=False,
                       allow_unicode=True,
                       sort_keys=False,
                       indent=2)
    
    return True


def validate_enrichments(block: dict, enrichments: dict):
    """Valida que los enriquecimientos sean válidos."""
    
    # 1. Verificar que el SID tenga formato correcto
    if "sid" in enrichments:
        sid = enrichments["sid"]
        if not re.match(r'^(BLK|INS|OUT|VAR|GOAL|CONST|REQ)\.[a-z0-9_\.]+$', sid):
            raise ValueError(f"SID inválido: {sid}")
    
    # 2. Verificar que la confianza sea válida
    if "confidence" in enrichments:
        conf = enrichments["confidence"]
        if conf not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError(f"Confianza inválida: {conf}")
    
    # 3. No sobrescribir campos críticos accidentalmente
    protected_fields = ["block_type", "content"]
    for field in protected_fields:
        if field in enrichments:
            raise ValueError(f"No se puede modificar campo protegido: {field}")
```

### Uso en el Agente

```python
# FASE 2: Enriquecimiento Semántico
enrichments = analyze_block_semantics(block_content)

# ✅ CORRECTO: Modificar dict
success = enrich_yaml_block(
    yaml_path="swarm/agents/.../file.yaml",
    block_name="Entry Guard",
    enrichments={
        "accion": "verificar",
        "relacion": "control.active_agent",
        "nivel": "guard",
        "sid": "BLK.verificar.control.active_agent.guard",
        "confidence": "HIGH",
        "inference_method": "vocabulary"
    }
)

# ❌ EVITAR: String-replace
# replace_string_in_file(...)  # ← Frágil
```

---

## 🔍 Cuándo Usar String-Replace (Casos Excepcionales)

Solo en situaciones muy específicas:

### 1. Comentarios YAML
```python
# Añadir cabecera al archivo
replace_string_in_file(
    filePath="file.yaml",
    oldString="agent:",
    newString="# Generated by @yaml-pipeline v1.0.0\n# Date: 2025-11-19\nagent:"
)
```

### 2. Placeholders Globales
```python
# Reemplazar TODOS los placeholders (sin estructura)
replace_string_in_file(
    filePath="file.yaml",
    oldString="<<PENDING_AI>>",
    newString="[ENRIQUECIMIENTO REQUERIDO]"
)
```

### 3. Patcheos Textuales Sin Semántica
```python
# Corregir typo en contenido libre
replace_string_in_file(
    filePath="file.yaml",
    oldString="content: \"Verfiicar\"",
    newString="content: \"Verificar\""
)
```

**Regla general:** Si estás modificando **campos semánticos** (accion, sid, relacion, nivel), usa **AST (dict)**. Solo usa string-replace para texto no estructurado.

---

## 🛡️ Ventajas Adicionales del Enfoque AST

### 1. Validación Antes de Modificar
```python
# Verificar unicidad de SID
all_sids = [block["sid"] for block in blocks.values() if "sid" in block]
if new_sid in all_sids:
    raise ValueError(f"SID duplicado: {new_sid}")
```

### 2. Operaciones Complejas
```python
# Renumerar SIDs temporales
for i, (block_name, block) in enumerate(blocks.items(), start=1):
    if block.get("sid", "").startswith("TEMP_"):
        block["sid"] = f"TEMP_BLK_{i:03d}"
```

### 3. Estadísticas y Reportes
```python
# Contar bloques por tipo
from collections import Counter
block_types = Counter(block["block_type"] for block in blocks.values())
print(f"BLK: {block_types['BLK']}, INS: {block_types['INS']}")
```

### 4. Rollback Automático
```python
# Backup antes de modificar
import shutil
shutil.copy("file.yaml", "file.yaml.backup")

try:
    enrich_yaml_block(...)
except Exception as e:
    # Restaurar backup si algo falla
    shutil.copy("file.yaml.backup", "file.yaml")
    raise
```

---

## 📊 Comparación Práctica

### Escenario: Actualizar 10 bloques con SIDs

**String-Replace (frágil):**
```python
for block_name, new_sid in updates.items():
    # ❌ 10 llamadas a replace_string_in_file
    # ❌ Cada una depende de formato exacto
    # ❌ Si falla una, estado inconsistente
    replace_string_in_file(
        filePath="file.yaml",
        oldString=f"{block_name}:\n  sid: TEMP_...",
        newString=f"{block_name}:\n  sid: {new_sid}"
    )
```

**AST (robusto):**
```python
# ✅ 1 carga, 10 modificaciones, 1 volcado
data = yaml.safe_load(open("file.yaml"))
blocks = data["agent"]["blocks"]

for block_name, new_sid in updates.items():
    if block_name in blocks:
        blocks[block_name]["sid"] = new_sid

yaml.safe_dump(data, open("file.yaml", "w"), sort_keys=False)
```

**Resultado:**
- AST: 1 read + 1 write = **2 operaciones I/O**
- String-replace: 10 reads + 10 writes = **20 operaciones I/O**
- AST: **10x más eficiente** y **100% robusto**

---

## 🎓 Guía de Decisión

```
┌─────────────────────────────────────┐
│ ¿Qué quiero modificar?              │
└─────────────────────────────────────┘
           │
           ├─ Campos semánticos (accion, sid, relacion, nivel)
           │  → ✅ Usar AST (dict)
           │
           ├─ Estructura YAML (añadir/quitar bloques)
           │  → ✅ Usar AST (dict)
           │
           ├─ Validaciones complejas
           │  → ✅ Usar AST (dict)
           │
           ├─ Comentarios o cabeceras
           │  → ⚠️ String-replace (excepcional)
           │
           └─ Placeholders globales sin semántica
              → ⚠️ String-replace (excepcional)
```

---

## 📚 Implementación Recomendada

```python
# code/yaml_ast_utils.py

import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class YAMLBlockEditor:
    """Editor robusto de bloques YAML usando AST."""
    
    def __init__(self, yaml_path: str):
        self.path = Path(yaml_path)
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Carga YAML como dict."""
        with open(self.path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _save(self):
        """Guarda dict como YAML."""
        with open(self.path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.data, f,
                          default_flow_style=False,
                          allow_unicode=True,
                          sort_keys=False,
                          indent=2)
    
    def get_block(self, block_name: str) -> Dict:
        """Obtiene un bloque por nombre."""
        blocks = self.data.get("agent", {}).get("blocks", {})
        return blocks.get(block_name)
    
    def update_block(self, block_name: str, fields: Dict[str, Any]):
        """Actualiza campos de un bloque."""
        block = self.get_block(block_name)
        if not block:
            raise ValueError(f"Bloque no encontrado: {block_name}")
        
        # Validar cambios
        self._validate_fields(block, fields)
        
        # Aplicar cambios
        block.update(fields)
        
        # Metadata
        block["last_modified"] = datetime.now().isoformat()
    
    def list_blocks(self) -> List[str]:
        """Lista nombres de todos los bloques."""
        blocks = self.data.get("agent", {}).get("blocks", {})
        return list(blocks.keys())
    
    def commit(self):
        """Guarda cambios al disco."""
        self._save()
    
    def _validate_fields(self, block: Dict, fields: Dict):
        """Valida que los campos sean válidos."""
        # Implementar validaciones aquí
        pass


# USO:
editor = YAMLBlockEditor("file.yaml")

# Modificar varios bloques
editor.update_block("Entry Guard", {
    "accion": "verificar",
    "sid": "BLK.verificar.control.active_agent.guard"
})

editor.update_block("State JSON", {
    "accion": "generar",
    "sid": "BLK.generar.state_json.protocol"
})

# Commit una sola vez
editor.commit()
```

---

**Conclusión:** El enfoque AST es **la mejor práctica** para manipular YAML estructurado. String-replace debe reservarse solo para casos excepcionales sin semántica.
