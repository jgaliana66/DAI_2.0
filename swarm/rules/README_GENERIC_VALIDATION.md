# 🎯 Validación Semántica Genérica con yaml_lint_v4.py

## 📋 Índice

- [¿Qué es yaml_lint_v4?](#qué-es-yaml_lint_v4)
- [Diferencias con v3](#diferencias-con-v3)
- [Arquitectura basada en reglas](#arquitectura-basada-en-reglas)
- [Cómo usar](#cómo-usar)
- [Cómo personalizar para tu SWARM](#cómo-personalizar-para-tu-swarm)
- [Ejemplos de personalización](#ejemplos-de-personalización)
- [Integración en pipeline](#integración-en-pipeline)

---

## ¿Qué es yaml_lint_v4?

`yaml_lint_v4.py` es un **validador semántico configurable mediante reglas externas** para SWARMs que siguen la metodología APS v3.5.

### ✅ Ventajas sobre yaml_lint_v3

| Aspecto | v3 (hardcoded) | v4 (rule-based) |
|---------|----------------|-----------------|
| **Patrones** | Hardcoded en Python | Definidos en YAML externo |
| **Personalización** | Requiere editar código | Solo editar archivo de reglas |
| **Multi-dominio** | Específico para J2C | Genérico + dominios custom |
| **Mantenibilidad** | Baja (cambios→recompilar) | Alta (cambios→reload YAML) |
| **Curva aprendizaje** | Requiere Python | Solo YAML/regex |
| **Extensibilidad** | Moderada | Alta |

### ⚡ Mejoras Clave

1. **Reglas externalizadas** en `validation_rules_v1.yaml`
2. **Soporte multi-dominio**: generic, j2c, custom
3. **Patrones configurables** sin modificar código
4. **Reportes customizables** (detailed, summary, json)
5. **Fácil integración** en pipelines existentes

---

## Diferencias con v3

### yaml_lint_v3.py (Ad-hoc)

```python
# ❌ Patrones hardcoded en código Python
SUSPICIOUS_PATTERNS = {
    'entry_guard': {
        'always_active': [r'SIEMPRE\s+activarse', ...],
        # ...más patrones hardcoded
    }
}

# Para cambiar un patrón → editar código Python
# Para añadir nueva regla → recompilar
# Para otro dominio → duplicar archivo
```

### yaml_lint_v4.py (Genérico)

```yaml
# ✅ Patrones configurables en archivo YAML externo
suspicious_patterns:
  entry_guard:
    always_active:
      - pattern: "SIEMPRE\\s+activarse"
        severity: error
        message: "Entry Guard configurado para activarse siempre"

# Para cambiar un patrón → editar YAML
# Para añadir nueva regla → nueva entrada en YAML
# Para otro dominio → nuevo archivo de reglas
```

---

## Arquitectura basada en reglas

### Componentes

```
📦 Sistema de Validación v4
│
├── 🐍 yaml_lint_v4.py
│   ├── RuleEngine: Carga y parsea reglas desde YAML
│   ├── ValidationRule: Representa una regla individual
│   └── SemanticValidator: Aplica reglas a archivos YAML
│
└── 📄 validation_rules_v1.yaml
    ├── suspicious_patterns: Regex patterns a detectar
    ├── required_keywords: Keywords obligatorios por bloque
    ├── role_permissions: Permisos por rol (Orchestrator/INPUT/HELPER)
    ├── structural_requirements: Bloques obligatorios
    ├── semantic_validators: Validaciones avanzadas
    └── custom_rules: Reglas específicas del dominio
```

### Flujo de Validación

```
┌──────────────┐
│ agent.yaml   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ yaml_lint_v4.py              │
│  1. Carga archivo de reglas  │
│  2. Parsea agent.yaml        │
│  3. Determina rol del agente │
└──────┬───────────────────────┘
       │
       ├─► Para cada bloque:
       │    ├─ Aplicar suspicious_patterns
       │    ├─ Verificar required_keywords
       │    └─ Validar role_permissions
       │
       ▼
┌──────────────────────────────┐
│ Reporte de validación        │
│  - Errores (exit code 1)     │
│  - Warnings (exit code 0)    │
└──────────────────────────────┘
```

---

## Cómo usar

### 1. Uso Básico (reglas por defecto)

```bash
python3 aps-tooling/scripts/yaml_lint_v4.py swarm/agents/MySwarm/01-agent.yaml
```

**Output:**
```
📋 Reglas cargadas desde: swarm/rules/validation_rules_v1.yaml
📄 Validando: swarm/agents/MySwarm/01-agent.yaml

❌ ERRORES: 2
  ❌ ERROR en 'Entry Guard': Entry Guard debe verificar 'active_agent'
  ❌ ERROR en 'Instrucciones': Agente INPUT no puede modificar 'covered.*'

⚠️  WARNINGS: 1
  ⚠️  WARNING en 'Exit Strategy': No menciona devolución de control

📊 RESUMEN: 2 errores, 1 warnings
```

### 2. Uso con Reglas Custom

```bash
# Crear tu archivo de reglas personalizado
cp swarm/rules/validation_rules_v1.yaml swarm/rules/my_rules.yaml

# Editar my_rules.yaml según tu dominio...

# Validar usando tus reglas
python3 aps-tooling/scripts/yaml_lint_v4.py agent.yaml --rules swarm/rules/my_rules.yaml
```

### 3. Output Formato JSON

```bash
python3 aps-tooling/scripts/yaml_lint_v4.py agent.yaml --format json
```

**Output:**
```json
{
  "file": "agent.yaml",
  "errors": 2,
  "warnings": 1,
  "issues": [
    {
      "location": "Entry Guard",
      "severity": "error",
      "message": "Entry Guard debe verificar 'active_agent'"
    },
    ...
  ]
}
```

---

## Cómo personalizar para tu SWARM

### Paso 1: Copiar plantilla de reglas

```bash
cp swarm/rules/validation_rules_v1.yaml swarm/rules/my_swarm_rules.yaml
```

### Paso 2: Modificar metadata

```yaml
version: "1.0"
metadata:
  description: "Reglas de validación para MI-SWARM"
  domain: "custom"  # Cambiar de "generic" a tu dominio
  author: "Tu Nombre"
  last_updated: "2025-11-19"
```

### Paso 3: Personalizar patrones sospechosos

#### Ejemplo: Dominio de e-commerce

```yaml
suspicious_patterns:
  # Patrones específicos de e-commerce
  inventory_check:
    missing_stock_validation:
      - pattern: "crear.*pedido.*sin.*verificar.*stock"
        severity: error
        message: "Pedido creado sin validación de inventario"
    
    negative_quantity:
      - pattern: "cantidad\\s*<\\s*0"
        severity: error
        message: "Cantidad negativa detectada"
  
  payment_processing:
    no_validation:
      - pattern: "procesar.*pago.*sin.*validar"
        severity: error
        message: "Procesamiento de pago sin validación previa"
```

### Paso 4: Definir keywords requeridos

#### Ejemplo: Sistema de notificaciones

```yaml
required_keywords:
  notification_block:
    must_contain_any:
      - "enviar_notificacion"
      - "send_email"
      - "push_notification"
    message: "Bloque de notificación debe especificar método de envío"
    severity: error
  
  retry_logic:
    must_contain_any:
      - "retry"
      - "reintentar"
      - "max_attempts"
    message: "Lógica de reintento debe estar definida"
    severity: warning
```

### Paso 5: Configurar permisos por rol

#### Ejemplo: Roles custom (READER, WRITER, ADMIN)

```yaml
role_permissions:
  READER:
    can_modify:
      - "meta\\.last_read"
      - "metrics\\.views"
    cannot_modify:
      - "data\\..*"
      - "state\\..*"
    can_activate_agents: false
  
  WRITER:
    can_modify:
      - "data\\.content"
      - "meta\\.last_modified"
    cannot_modify:
      - "data\\.permissions"
      - "state\\.phase"
    can_activate_agents: false
  
  ADMIN:
    can_modify:
      - ".*"  # Todo
    can_activate_agents: true
```

### Paso 6: Validar con tus reglas custom

```bash
python3 aps-tooling/scripts/yaml_lint_v4.py \
  swarm/agents/MySwarm/01-agent.yaml \
  --rules swarm/rules/my_swarm_rules.yaml
```

---

## Ejemplos de personalización

### Ejemplo 1: SWARM de Soporte Técnico

**Archivo:** `support_swarm_rules.yaml`

```yaml
suspicious_patterns:
  ticket_handling:
    auto_close:
      - pattern: "cerrar.*ticket.*automáticamente.*sin.*confirmar"
        severity: error
        message: "Ticket cerrado sin confirmación del usuario"
    
    missing_priority:
      - pattern: "crear.*ticket.*sin.*prioridad"
        severity: warning
        message: "Ticket creado sin asignar prioridad"

required_keywords:
  escalation_block:
    must_contain_any:
      - "escalar_a"
      - "nivel_soporte"
      - "supervisor"
    message: "Bloque de escalación debe definir siguiente nivel"
    severity: error

role_permissions:
  AGENT_L1:
    can_modify:
      - "ticket\\.status"
      - "ticket\\.notes"
    cannot_modify:
      - "ticket\\.priority"
      - "ticket\\.assigned_team"
  
  AGENT_L2:
    can_modify:
      - "ticket\\..*"
    cannot_modify:
      - "ticket\\.sla_override"
```

**Uso:**
```bash
python3 aps-tooling/scripts/yaml_lint_v4.py \
  support_agents/01-triage.yaml \
  --rules support_swarm_rules.yaml
```

---

### Ejemplo 2: SWARM de Aprobación de Créditos

**Archivo:** `credit_approval_rules.yaml`

```yaml
suspicious_patterns:
  credit_check:
    skip_validation:
      - pattern: "aprobar.*sin.*verificar.*score"
        severity: error
        message: "Aprobación sin verificar score crediticio"
    
    manual_override:
      - pattern: "override.*automático"
        severity: warning
        message: "Override manual requiere justificación"

required_keywords:
  approval_block:
    must_contain_any:
      - "verificar_ingresos"
      - "check_credit_score"
      - "validar_documentos"
    message: "Bloque de aprobación debe validar requisitos"
    severity: error

role_permissions:
  ANALYST:
    can_modify:
      - "application\\.status"
      - "application\\.notes"
    cannot_modify:
      - "application\\.approved_amount"
  
  MANAGER:
    can_modify:
      - "application\\..*"
    cannot_modify:
      - "system\\.audit_log"
```

---

### Ejemplo 3: SWARM de Automatización DevOps

**Archivo:** `devops_swarm_rules.yaml`

```yaml
suspicious_patterns:
  deployment:
    no_rollback:
      - pattern: "deploy.*producción.*sin.*rollback"
        severity: error
        message: "Deployment sin plan de rollback definido"
    
    skip_tests:
      - pattern: "deploy.*sin.*tests"
        severity: error
        message: "Deployment sin ejecutar tests previos"

required_keywords:
  deployment_block:
    must_contain_any:
      - "run_tests"
      - "backup_database"
      - "health_check"
    message: "Deployment debe incluir validaciones pre-deploy"
    severity: error

role_permissions:
  DEVELOPER:
    can_modify:
      - "code\\..*"
      - "config\\.dev"
    cannot_modify:
      - "config\\.prod"
      - "deploy\\.trigger"
  
  DEVOPS_ENGINEER:
    can_modify:
      - "config\\..*"
      - "deploy\\..*"
    cannot_modify:
      - "security\\.keys"
```

---

## Integración en pipeline

### Opción 1: Integración en Makefile

```makefile
# swarm/Makefile

YAML_LINTER = aps-tooling/scripts/yaml_lint_v4.py
RULES_FILE = swarm/rules/validation_rules_v1.yaml

validate-semantic:
	@echo "🔍 Validando semántica de agentes..."
	@for yaml in swarm/agents/$(SWARM)/*.yaml; do \
		echo "  Validando $$yaml..."; \
		python3 $(YAML_LINTER) "$$yaml" --rules $(RULES_FILE) || exit 1; \
	done
	@echo "✅ Validación semántica completa"

# Integrar en pipeline completo
pipeline-full: md2yaml enrich validate-semantic
	@echo "🎉 Pipeline completo ejecutado exitosamente"
```

**Uso:**
```bash
make validate-semantic SWARM=MySwarm
```

---

### Opción 2: Integración en script bash

```bash
#!/bin/bash
# validate_swarm.sh

SWARM_DIR="swarm/agents/$1"
RULES_FILE="${2:-swarm/rules/validation_rules_v1.yaml}"

echo "🔍 Validando SWARM: $1"
echo "📋 Reglas: $RULES_FILE"

errors=0
warnings=0

for yaml_file in "$SWARM_DIR"/*.yaml; do
    echo ""
    echo "📄 Validando: $(basename $yaml_file)"
    
    output=$(python3 aps-tooling/scripts/yaml_lint_v4.py "$yaml_file" --rules "$RULES_FILE" 2>&1)
    exit_code=$?
    
    echo "$output"
    
    if [ $exit_code -ne 0 ]; then
        ((errors++))
    fi
done

echo ""
echo "═══════════════════════════════════════"
echo "📊 RESUMEN TOTAL"
echo "  Archivos con errores: $errors"
echo "═══════════════════════════════════════"

exit $errors
```

**Uso:**
```bash
chmod +x validate_swarm.sh
./validate_swarm.sh MySwarm
./validate_swarm.sh MySwarm swarm/rules/custom_rules.yaml
```

---

### Opción 3: Integración en GitHub Actions

```yaml
# .github/workflows/validate-swarm.yml

name: Validate SWARM Semantics

on:
  pull_request:
    paths:
      - 'swarm/agents/**/*.yaml'
      - 'swarm/rules/**/*.yaml'

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install pyyaml
      
      - name: Run semantic validation
        run: |
          for yaml in swarm/agents/*/*.yaml; do
            echo "Validating $yaml..."
            python3 aps-tooling/scripts/yaml_lint_v4.py \
              "$yaml" \
              --rules swarm/rules/validation_rules_v1.yaml
          done
```

---

## 🎓 Guía rápida de personalización

### 1. ¿Qué patrones añadir?

**Pregúntate:**
- ¿Qué errores comunes comete mi equipo?
- ¿Qué anti-patterns son críticos en mi dominio?
- ¿Qué validaciones haría en code review manualmente?

**Ejemplo:** Si tu SWARM es de e-commerce y frecuentemente olvidan validar stock:

```yaml
suspicious_patterns:
  order_creation:
    no_stock_check:
      - pattern: "crear_pedido.*sin.*verificar_stock"
        severity: error
        message: "Pedido creado sin validar inventario"
```

### 2. ¿Qué keywords son obligatorios?

**Pregúntate:**
- ¿Qué palabras clave DEBEN aparecer en ciertos bloques?
- ¿Qué funciones son mandatorias?
- ¿Qué validaciones mínimas requiere mi dominio?

**Ejemplo:** Todos los bloques de autenticación deben mencionar "verify_token":

```yaml
required_keywords:
  authentication_block:
    must_contain_any:
      - "verify_token"
      - "check_auth"
      - "validate_session"
    message: "Bloque de autenticación debe verificar token"
    severity: error
```

### 3. ¿Qué permisos por rol?

**Pregúntate:**
- ¿Qué roles existen en mi SWARM?
- ¿Qué puede modificar cada rol?
- ¿Qué está prohibido para ciertos roles?

**Ejemplo:** Solo ADMIN puede modificar permisos:

```yaml
role_permissions:
  USER:
    cannot_modify:
      - "permissions\\..*"
      - "roles\\..*"
  
  ADMIN:
    can_modify:
      - ".*"
```

---

## 📚 Recursos adicionales

- **Archivo de reglas genérico:** `swarm/rules/validation_rules_v1.yaml`
- **Código del linter:** `aps-tooling/scripts/yaml_lint_v4.py`
- **Ejemplos de defectos:** `swarm/agents/J2C-TEST-Defects-v1/`
- **Reporte de análisis:** `swarm/agents/J2C-TEST-Defects-v1/DEFECT_ANALYSIS_REPORT.md`

---

## 🆘 FAQ

### ¿Puedo usar regex complejos?

Sí, cualquier regex válido en Python es aceptado. Ejemplo:

```yaml
suspicious_patterns:
  complex_validation:
    - pattern: "(?i)(?:password|secret)\\s*=\\s*[\"'][^\"']{1,5}[\"']"
      severity: error
      message: "Contraseña demasiado corta detectada"
```

### ¿Cómo desactivo ciertas validaciones?

Comenta la regla en el YAML:

```yaml
suspicious_patterns:
  entry_guard:
    # always_active:  # DESACTIVADO temporalmente
    #   - pattern: "SIEMPRE\\s+activarse"
    #     severity: error
```

O crea un archivo de reglas custom sin esas validaciones.

### ¿Puedo tener múltiples archivos de reglas?

Sí, crea un archivo por dominio:

```
swarm/rules/
├── validation_rules_v1.yaml       # Genérico
├── j2c_migration_rules.yaml       # Migración J2C
├── ecommerce_rules.yaml           # E-commerce
└── support_ticket_rules.yaml      # Soporte técnico
```

Usa `--rules` para especificar cuál usar:

```bash
python3 yaml_lint_v4.py agent.yaml --rules swarm/rules/ecommerce_rules.yaml
```

### ¿Cómo testeo mis reglas custom?

1. Crea un agente de prueba con defectos conocidos
2. Valida con tus reglas
3. Verifica que detecta los defectos esperados

```bash
# 1. Crear test_agent.yaml con defecto intencional
echo '...' > test_agent.yaml

# 2. Validar
python3 yaml_lint_v4.py test_agent.yaml --rules my_rules.yaml

# 3. Verificar que detecta el defecto
# Esperado: "ERROR en 'Entry Guard': ..."
```

---

**Última actualización:** 2025-11-19  
**Versión:** 1.0  
**Autor:** APS v3.5 Validation Team
