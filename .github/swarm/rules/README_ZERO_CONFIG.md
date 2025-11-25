# 🚀 yaml_lint_v5.py - Validación CERO CONFIGURACIÓN

## ¿Por qué v5?

**Problema con v4:** Requerir escribir reglas YAML manualmente es una barrera innecesaria.

**Solución v5:** El linter **aprende automáticamente** del SWARM existente. Sin configuración.

---

## 🎯 Tres modos de uso

### 1️⃣ MODO AUTO (Recomendado - SIN configuración)

```bash
# El linter aprende patrones del SWARM y valida
python3 aps-tooling/scripts/yaml_lint_v5.py swarm/agents/MySwarm/*.yaml
```

**Qué hace:**
- ✅ Analiza todos los agentes del SWARM
- ✅ Detecta patrones comunes automáticamente
- ✅ Aprende roles (Orchestrator/INPUT/HELPER)
- ✅ Infiere keywords requeridos por bloque
- ✅ Valida sin necesidad de configuración manual

**Ejemplo:**
```bash
$ python3 yaml_lint_v5.py swarm/agents/J2C-v1/*.yaml

🚀 MODO: AUTO (aprendizaje automático del SWARM)

🧠 Aprendiendo patrones del SWARM existente...
✅ Aprendizaje completo: 4 categorías detectadas

📄 VALIDANDO ARCHIVOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 01-orchestrator.yaml
✅ OK

📄 02-migration.yaml
⚠️  WARNING: Entry Guard no contiene keywords aprendidos

📊 RESUMEN: 0 errores, 1 warnings
```

---

### 2️⃣ MODO AI-ASSIST (Describe tu dominio en lenguaje natural)

```bash
# Describe qué quieres validar en lenguaje natural
python3 yaml_lint_v5.py agent.yaml --domain "validar pedidos de e-commerce con inventario"
```

**Qué hace:**
- ✅ Detecta el dominio por keywords ("e-commerce", "inventario", "pedidos")
- ✅ Carga plantilla de reglas pre-construida para ese dominio
- ✅ Valida usando reglas específicas del dominio

**Dominios soportados:**
- `ecommerce` → Keywords: inventory, stock, cart, payment, order
- `support` → Keywords: ticket, escalate, priority, sla, customer
- `devops` → Keywords: deploy, rollback, test, production, environment

**Ejemplo:**
```bash
$ python3 yaml_lint_v5.py agent.yaml --domain "validar tickets de soporte con escalación"

🤖 MODO: Generación AI-Assisted

✅ Dominio detectado: support

📄 VALIDANDO ARCHIVOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 agent.yaml
❌ ERROR: Ticket cerrado sin confirmación del usuario

📊 RESUMEN: 1 errores, 0 warnings
```

---

### 3️⃣ MODO MANUAL (Power users - usa archivo de reglas)

```bash
# Para casos avanzados: usa archivo de reglas custom
python3 yaml_lint_v5.py agent.yaml --rules swarm/rules/my_custom_rules.yaml
```

**Cuándo usar:**
- Necesitas validaciones muy específicas no cubiertas por AUTO o AI-ASSIST
- Quieres reutilizar reglas exactas entre proyectos
- Compliance o auditoría requiere reglas documentadas

---

## 🧠 Aprender y exportar reglas

Si quieres **guardar las reglas aprendidas** para reutilizarlas:

```bash
# Aprende del SWARM y exporta reglas a archivo
python3 yaml_lint_v5.py swarm/agents/MySwarm/*.yaml --learn-rules > my_learned_rules.yaml
```

**Luego úsalas en otro proyecto:**
```bash
python3 yaml_lint_v5.py other_swarm/agent.yaml --rules my_learned_rules.yaml
```

---

## 📊 Comparativa de versiones

| Característica | v4 (Rule-Based) | v5 (Zero-Config) |
|----------------|-----------------|------------------|
| **Configuración requerida** | Escribir YAML manualmente | **Ninguna** |
| **Barrera de entrada** | Media (conocer YAML + regex) | **Cero** |
| **Tiempo setup** | 10-30 minutos | **0 segundos** |
| **Aprendizaje automático** | No | **Sí** |
| **AI-Assisted** | No | **Sí** |
| **Casos avanzados** | Sí | Sí (modo manual) |

---

## 🎯 Casos de uso

### Caso 1: Desarrollador nuevo en el equipo

**Antes (v4):**
```bash
# 1. Leer README (10 min)
# 2. Copiar plantilla de reglas
cp swarm/rules/validation_rules_v1.yaml my_rules.yaml

# 3. Editar reglas (20 min)
# - ¿Qué patrones añadir?
# - ¿Qué keywords son obligatorios?
# - ¿Qué permisos por rol?

# 4. Validar
python3 yaml_lint_v4.py agent.yaml --rules my_rules.yaml
```

**Ahora (v5):**
```bash
# ¡Ya está!
python3 yaml_lint_v5.py swarm/agents/MySwarm/*.yaml
```

⏱️ **Ahorro: 30 minutos → 0 segundos**

---

### Caso 2: Validar SWARM de dominio conocido

**Antes (v4):**
```bash
# Buscar plantilla de e-commerce en README
# Copiar 200 líneas de YAML
# Editar según tu caso específico
```

**Ahora (v5):**
```bash
python3 yaml_lint_v5.py agent.yaml --domain "e-commerce con pagos"
```

---

### Caso 3: CI/CD Pipeline

**Antes (v4):**
```yaml
# .github/workflows/validate.yml
- name: Setup rules
  run: cp swarm/rules/validation_rules_v1.yaml .
  
- name: Validate
  run: python3 yaml_lint_v4.py agent.yaml --rules validation_rules_v1.yaml
```

**Ahora (v5):**
```yaml
# .github/workflows/validate.yml
- name: Validate
  run: python3 yaml_lint_v5.py swarm/agents/*/*.yaml
```

---

## 💡 ¿Cuándo usar cada modo?

### Usa MODO AUTO si:
- ✅ Es tu primer SWARM
- ✅ Quieres validación rápida sin configurar
- ✅ Confías en que el SWARM existente sigue buenas prácticas
- ✅ No tienes requisitos específicos de compliance

### Usa MODO AI-ASSIST si:
- ✅ Tu SWARM es de un dominio conocido (e-commerce, support, devops)
- ✅ Quieres validaciones específicas del dominio
- ✅ Necesitas detectar anti-patterns comunes del dominio

### Usa MODO MANUAL si:
- ✅ Compliance requiere reglas documentadas y auditables
- ✅ Necesitas validaciones muy específicas no cubiertas por plantillas
- ✅ Quieres compartir reglas exactas entre equipos
- ✅ Tienes un SWARM maduro con reglas bien definidas

---

## 🚀 Migración desde v4

Si ya tienes reglas v4 escritas:

```bash
# Opción 1: Seguir usando v4
python3 yaml_lint_v4.py agent.yaml --rules my_v4_rules.yaml

# Opción 2: Usar v5 en modo manual (compatible con v4)
python3 yaml_lint_v5.py agent.yaml --rules my_v4_rules.yaml

# Opción 3: Dejar que v5 aprenda automáticamente
python3 yaml_lint_v5.py swarm/agents/MySwarm/*.yaml
# (olvídate de my_v4_rules.yaml)
```

**Recomendación:** Prueba v5 en modo AUTO. Si funciona bien, elimina reglas manuales.

---

## 📖 Ejemplos completos

### Ejemplo 1: Proyecto nuevo

```bash
# Tienes un SWARM nuevo, quieres validarlo
cd my-project/
python3 aps-tooling/scripts/yaml_lint_v5.py swarm/agents/v1/*.yaml

# ✅ Listo. Sin configuración.
```

### Ejemplo 2: SWARM de e-commerce

```bash
# Describes tu dominio en lenguaje natural
python3 yaml_lint_v5.py cart_agent.yaml \
  --domain "validar carritos de compra con inventario y pagos"

# El linter detecta "ecommerce" y aplica reglas específicas
```

### Ejemplo 3: Aprender y compartir reglas

```bash
# Equipo A aprende reglas de su SWARM maduro
python3 yaml_lint_v5.py swarm/agents/production/*.yaml \
  --learn-rules > shared_rules.yaml

# Equipo A commitea shared_rules.yaml al repo

# Equipo B usa las mismas reglas
git pull
python3 yaml_lint_v5.py my_agent.yaml --rules shared_rules.yaml
```

---

## ❓ FAQ

### ¿Qué tan preciso es el aprendizaje automático?

**MODO AUTO aprende:**
- ✅ Roles de agentes (Orchestrator/INPUT/HELPER)
- ✅ Keywords usados frecuentemente en cada tipo de bloque
- ✅ Campos que modifica cada rol

**Limitaciones:**
- ⚠️ No detecta anti-patterns específicos del dominio (usa AI-ASSIST para eso)
- ⚠️ Necesita al menos 3-4 agentes para aprender patrones significativos

### ¿Puedo combinar modos?

**Sí. Workflow recomendado:**

1. Primera validación → MODO AUTO
2. Si detecta dominio conocido → MODO AI-ASSIST
3. Si necesitas custom → Aprende reglas con `--learn-rules` y editlas

### ¿v5 reemplaza a v4?

**No completamente:**
- Para casos comunes → v5 es mejor (cero config)
- Para compliance/auditoría → v4 puede ser preferible (reglas explícitas documentadas)

**v5 incluye v4 como "modo manual"**, así que puedes usarlo para ambos casos.

---

## 🎓 Conclusión

**yaml_lint_v5.py elimina la barrera de entrada:**

| Antes (v4) | Ahora (v5) |
|------------|------------|
| "Necesito leer el README y escribir reglas YAML" | "Ejecuto un comando y ya está" |
| 30 minutos de setup | 0 segundos |
| Requiere conocer regex | No requiere configuración |
| Solo para power users | **Para todos** |

**Inicio rápido:**

```bash
# ¡Pruébalo ahora!
python3 aps-tooling/scripts/yaml_lint_v5.py swarm/agents/MySwarm/*.yaml
```

**Sin configuración. Sin complicaciones. Solo validación.**
