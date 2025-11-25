# 🤖 YAML Pipeline - Sistema de Validación APS v3.5

Sistema completo de conversión, validación y enriquecimiento semántico para agentes SWARM siguiendo el estándar APS v3.5.

---

## 🏛️ Contexto: Metodología APS v3.5

Este pipeline es la **implementación oficial** de la metodología APS v3.5 (Agent Prompt Specification).

**APS define**:
- Estructura de agentes (bloques obligatorios, políticas)
- Semántica de SIDs (identificadores semánticos)
- Gobierno de coherencia (antipatrones, contradicciones)
- Vocabulario controlado y versionado

**El pipeline compila y valida** que los agentes cumplan APS:

```
APS (concepto) → MD (texto) → YAML (estructura) → Validación → Agente válido
```

### 📚 Documentación Relacionada

- **Metodología completa**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md` (sección 15)
- **Reglas del linter**: `APS/LINTER_RULES.md`
- **Vocabulario SID**: `aps-tooling/schemas/sid_vocabulary_v1.yaml`
- **Roadmap**: `APS/ROADMAP.md`

> **Lee primero** `METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md` para entender el **por qué** detrás del pipeline.

---

## 📋 Descripción General

Este pipeline automatiza el flujo completo de trabajo con agentes SWARM:

```
Markdown (.md) → YAML (.yaml) → Enriquecimiento → Validación → Reporte
```

**Dos modos de operación:**
1. **Modo Interactivo**: Para desarrollo, con emojis, colores y feedback humano
2. **Modo CI/CD**: Para automatización, con JSON, exit codes claros y sin emojis

## 🚀 Quick Start

### Modo Desarrollo (Interactivo)

```bash
# Opción 1: Agente Copilot
@yaml-pipeline swarm/agents/J2C-v1-Swarm-v3-5/02-migration-motives.md

# Opción 2: Makefile
make agent-pipeline FILE=swarm/agents/J2C-v1-Swarm-v3-5/02-migration-motives.md
```

### Modo CI/CD (Batch)

```bash
# Procesar múltiples archivos
make agent-pipeline-batch PATTERN="swarm/agents/J2C-v1-Swarm-v3-5/*.md"

# O directamente con el CLI
python3 code/yaml_pipeline_cli.py --batch "swarm/agents/**/*.md" --ci-mode
```

## 📁 Estructura de Archivos

```
DAI Arquitectura/
├── code/
│   ├── md2yaml.py              # Conversión MD → YAML (con auto-numbering)
│   ├── yaml_lint.py            # Validación semántica (legacy: reglas hardcoded)
│   ├── yaml_lint_v2.py         # ⭐ Validación con reglas centralizadas
│   ├── enrich_yaml_with_llm.py # Enriquecimiento (requiere @sid-generator)
│   └── yaml_pipeline_cli.py    # ⭐ CLI batch para CI/CD
├── swarm/
│   ├── agents/
│   │   └── J2C-v1-Swarm-v3-5/
│   │       ├── *.md            # Archivos fuente
│   │       └── *.yaml          # Archivos generados
│   └── schemas/
│       └── aps_v3.5_rules.yaml # ⭐ FUENTE DE VERDAD CANÓNICA
├── .github/workflows/
│   └── yaml-pipeline-ci.yml    # ⭐ GitHub Actions workflow
├── Makefile                    # ⭐ Targets batch agregados
├── AGENTE_YAML_PIPELINE.md     # ⭐ Especificación completa del agente
├── MIGRATION_RULES_CENTRALIZATION.md  # ⭐ Guía de migración
└── YAML_PIPELINE_README.md     # Este archivo
```

### 🆕 Arquitectura Centralizada

**Antes (reglas dispersas):**
```
code/yaml_lint.py    → DENY_TERMS hardcoded
code/md2yaml.py      → Block types hardcoded  
code/enrich_yaml.py  → Vocabulario hardcoded
```

**Ahora (fuente de verdad única):**
```
aps-tooling/schemas/aps_v3.5_rules.yaml  ← Todas las reglas APS
         ↓
code/yaml_lint_v2.py → Lee del schema
code/md2yaml.py      → Lee del schema (futuro)
code/enrich_yaml.py  → Lee del schema (futuro)
```

**Beneficios:**
- ✅ Actualizar APS v3.6 = modificar **1 solo archivo**
- ✅ Versionado claro (`aps_v3.5_rules.yaml` vs `aps_v3.6_rules.yaml`)
- ✅ No más desincronización entre código y documentación
- ✅ Extensible (custom rules por proyecto)

Ver `MIGRATION_RULES_CENTRALIZATION.md` para detalles.


## 🔑 Características Principales

### ✅ Completado

- **222/222 SIDs generados** en 11 agentes
- **Detección de duplicados**: Auto-numbering + linter
- **Detección de contradicciones**: DENY_TERMS con contexto
- **Sistema de confianza**: HIGH/MEDIUM/LOW con metadata
- **DENY_TERMS contextual**: Exempciones para [EXAMPLE] y [ANTIPATRÓN]
- **Validación de seguridad**: Path validation, command sanitization
- **Modo batch CI/CD**: JSON output, exit codes, sin emojis
- **GitHub Actions integration**: Workflow completo
- **Reglas centralizadas**: Fuente de verdad única en `aps_v3.5_rules.yaml`
- **Manipulación YAML robusta**: AST (dict) en lugar de string-replace

### 🎯 Mejoras Implementadas (v2.0)

1. **Sistema de Confianza Semántica**
   - Triple verificación: Vocabulario + Heurística + Coherencia
   - Metadata en YAML: `confidence: HIGH|MEDIUM|LOW`
   - Sugerencias para SIDs de baja confianza

2. **DENY_TERMS Contextual**
   - Tipos de bloque: EXAMPLE, ANTIPATTERN
   - Patrones de negación: "NO hacer", "NUNCA", "❌"
   - Severity: ERROR (prescriptivo) vs WARNING (negación) vs INFO (ejemplo)

3. **Seguridad**
   - Allowlist de scripts: solo 3 scripts autorizados
   - Path validation: solo `swarm/agents/` y `code/`
   - Command sanitization: `shlex.quote()` previene injection
   - Attack prevention: 6 vectores bloqueados

4. **Reglas Centralizadas (APS v3.5+)**
   - Fuente de verdad única: `aps-tooling/schemas/aps_v3.5_rules.yaml`
   - Actualizar APS v3.6 = modificar 1 archivo
   - Versionado claro, backward compatibility
   - Ver `MIGRATION_RULES_CENTRALIZATION.md`

5. **Manipulación YAML Robusta**
   - ✅ AST (dict) para campos semánticos
   - ❌ NO string-replace (frágil, dependiente de formato)
   - Inmune a cambios de indentación/orden
   - Ver `YAML_AST_BEST_PRACTICE.md`

## 📊 Exit Codes (Modo CI/CD)

| Code | Status | Descripción |
|------|--------|-------------|
| `0` | ✅ Success | Sin errores ni warnings |
| `1` | ⚠️ Warnings | LOW confidence SIDs, etc. |
| `2` | ❌ Errors | DENY_TERMS, duplicados |
| `3` | 💥 Validation Failed | yaml_lint.py falló |
| `4` | 🔒 Security Error | Path traversal, injection |
| `5` | 🐛 Internal Error | Exception no manejada |

## 🔧 Instalación

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd "DAI Arquitectura"

# 2. Instalar dependencias
pip install pyyaml

# 3. Hacer scripts ejecutables
chmod +x code/*.py

# 4. Verificar instalación
make check
```

## 📖 Uso Detallado

### 1. Pipeline Completo (Modo Interactivo)

```bash
# Ver especificación completa
cat AGENTE_YAML_PIPELINE.md

# Ejecutar con agente Copilot
@yaml-pipeline swarm/agents/J2C-v1-Swarm-v3-5/02-migration-motives.md
```

**Output esperado:**
```
🔄 Iniciando YAML Pipeline...
📄 FASE 1: Conversión MD → YAML ✅
🧠 FASE 2: Enriquecimiento Semántico ✅
🔍 FASE 3: Validación ✅
Estado: ✅ READY
```

### 2. Batch Processing (CI/CD)

```bash
# Procesar todos los agentes
python3 code/yaml_pipeline_cli.py \
  --batch "swarm/agents/J2C-v1-Swarm-v3-5/*.md" \
  --ci-mode > result.json

# Ver resumen
cat result.json | jq '.summary'

# Verificar exit code
echo $?
```

**Output esperado (JSON):**
```json
{
  "status": "success",
  "exit_code": 0,
  "summary": {
    "files_processed": 11,
    "files_success": 11,
    "files_warnings": 0,
    "files_errors": 0,
    "total_blocks": 242
  }
}
```

### 3. GitHub Actions

El workflow `.github/workflows/yaml-pipeline-ci.yml` se ejecuta automáticamente en:
- Push a `main`/`master` que modifique `swarm/agents/**/*.md`
- Pull requests que modifiquen archivos `.md`

**Features:**
- Ejecuta pipeline batch en modo CI
- Genera resumen en GitHub Step Summary
- Comenta en PRs si hay errores
- No falla en warnings (exit code 1)

### 4. Pre-commit Hook

```bash
# Crear hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔄 Validando YAMLs..."
MD_FILES=$(git diff --cached --name-only | grep '\.md$' | grep 'swarm/agents/')
for file in $MD_FILES; do
  python3 code/yaml_pipeline_cli.py --batch "$file" --ci-mode > /tmp/result.json
  exit_code=$(jq -r '.exit_code' /tmp/result.json)
  if [ $exit_code -ge 2 ]; then
    echo "❌ Validación falló para $file"
    jq -r '.files[0].errors[] | .message' /tmp/result.json
    exit 1
  fi
done
echo "✅ Validación completada"
EOF

chmod +x .git/hooks/pre-commit
```

## 🔍 Validaciones

### Detección de Duplicados
```yaml
# md2yaml.py auto-numera duplicados
- block: "Bloque Repetido"
- block: "Bloque Repetido (2)"
- block: "Bloque Repetido (3)"

# yaml_lint.py detecta:
⚠️ WARNING: Bloque auto-numerado detectado: "Bloque Repetido (2)"
```

### DENY_TERMS Contextual
```yaml
# ❌ ERROR: Uso prescriptivo
- block: "Proceso"
  instructions: "Hacer handoff automático cuando..."

# ⚠️ WARNING: Contexto de negación
- block: "Política NO-SALTO"
  instructions: "❌ NUNCA hacer handoff automático"

# ℹ️ INFO: Ejemplo o antipatrón
- block: "[EXAMPLE] Mal uso"
  instructions: "handoff automático (antipatrón)"
```

### Sistema de Confianza
```yaml
# HIGH confidence (vocabulario exacto)
sid: BLK.verificar.estado.contexto.validacion
confidence: HIGH
inference_method: vocabulary

# MEDIUM confidence (sinónimo reconocido)
sid: BLK.comprobar.estado.contexto.heuristic
confidence: MEDIUM
inference_method: heuristic
note: "usar 'verificar' para HIGH confidence"

# LOW confidence (inferencia)
sid: BLK.evaluar.contexto.suficiencia.heuristic
confidence: LOW
inference_method: inferred
suggestions:
  - BLK.verificar.estado.completitud.heuristic
  - BLK.detectar.contexto.insuficiente.heuristic
```

## 🔒 Seguridad

### Inputs Bloqueados

```bash
# ❌ Path traversal
swarm/agents/../../etc/passwd
→ ERROR: Ruta fuera del workspace

# ❌ Shell injection
test.md; rm -rf .
→ ERROR: Archivo no encontrado (shlex.quote neutraliza)

# ❌ Scope escape
/tmp/malicious.md
→ ERROR: Ruta fuera de scope permitido

# ✅ Input válido
swarm/agents/J2C-v1-Swarm-v3-5/02-migration-motives.md
→ Procesado correctamente
```

### Allowlists

**Scripts permitidos:**
- `code/md2yaml.py`
- `code/enrich_yaml_with_llm.py`
- `code/yaml_lint.py`

**Paths permitidos:**
- `swarm/agents/`
- `code/`

**Extensiones permitidas:**
- `.md`, `.yaml`, `.py`

## 📈 Estadísticas del Proyecto

```bash
# Ver estadísticas
make stats
```

**Output:**
```
Estadísticas de Agentes SWARM J2C
════════════════════════════════════════
Archivos Markdown: 11
Archivos YAML: 11
Total bloques: 242
SIDs generados: 242
Confianza: HIGH (210), MEDIUM (28), LOW (4)
```

## 🐛 Troubleshooting

### Problema: "Script no permitido"
```bash
ERROR: Script no permitido: code/custom.py
```
**Solución**: Añadir script a `ALLOWED_SCRIPTS` en `yaml_pipeline_cli.py`

### Problema: "Path fuera de scope"
```bash
ERROR: Ruta fuera de scope permitido: other/file.md
```
**Solución**: Mover archivo a `swarm/agents/` o añadir path a `ALLOWED_PREFIXES`

### Problema: "DENY_TERM detectado en ejemplo"
```bash
ERROR: Término prohibido: handoff.*autom[áa]tic
```
**Solución**: Marcar bloque como `[EXAMPLE]` o `[ANTIPATRÓN]` en el .md

## 📚 Documentación Completa

- **AGENTE_YAML_PIPELINE.md**: Especificación completa del agente (1500+ líneas)
- **METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md**: Metodología APS v3.5
- **PIPELINE_README.md**: Pipeline original (pre-batch)

## 🎓 Ejemplos de Casos de Uso

### CI/CD en GitLab
```yaml
# .gitlab-ci.yml
yaml-pipeline:
  stage: validate
  image: python:3.11
  script:
    - pip install pyyaml
    - python3 code/yaml_pipeline_cli.py --batch "swarm/agents/**/*.md" --ci-mode > result.json
    - cat result.json | jq '.summary'
  artifacts:
    paths:
      - result.json
```

### Pre-release Validation
```bash
# Validar antes de release
make agent-pipeline-batch PATTERN="swarm/agents/**/*.md"

# Si exit code = 0, tag release
if [ $? -eq 0 ]; then
  git tag v3.5.0
  git push --tags
fi
```

## 🛠️ Makefile Targets

```bash
make help                    # Mostrar ayuda
make check                   # Verificar scripts
make agent-pipeline FILE=... # Modo interactivo (recordatorio)
make agent-pipeline-batch PATTERN=... # Modo batch CI/CD
make stats                   # Estadísticas del proyecto
```

## 📞 Contacto y Contribución

Para reportar bugs o sugerir mejoras, ver `CONTRIBUTING.md`.

---

**Versión**: 2.0 (Modo Batch + CI/CD)  
**Última actualización**: 2025-11-19  
**Estado**: ✅ Production Ready
