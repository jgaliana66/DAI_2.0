# SWARM J2C — Agentes y Versionado

Este directorio contiene los agentes del SWARM J2C con pipeline automatizado y versionado semántico.

## 📁 Estructura

```
swarm/
├── agents/           # Agentes en .md (fuente) y .yaml (generado)
├── CHANGELOG.md      # Historial de cambios
├── VERSION           # Versión actual del SWARM
└── README.md         # Este archivo
```

## 🔄 Workflow

1. **Edición**: Modifica archivos `.md` en `agents/`
2. **Regeneración**: `make single AGENT=nombre` o `make rebuild`
3. **Validación**: `make lint`
4. **Versionado**: `python3 scripts/version_bump.py --level [major|minor|patch]`
5. **Commit**: Con mensaje tipo Conventional Commits

## 📦 Versionado Semántico

El SWARM usa versionado semántico (`MAJOR.MINOR.PATCH`):

```bash
# Incrementar versión patch (0.1.0 → 0.1.1)
python3 scripts/version_bump.py --level patch

# Incrementar versión minor (0.1.1 → 0.2.0)
python3 scripts/version_bump.py --level minor

# Incrementar versión major (0.2.0 → 1.0.0)
python3 scripts/version_bump.py --level major
```

El script actualiza automáticamente:
- `swarm/VERSION` - Número de versión actual
- `swarm/CHANGELOG.md` - Añade entrada con fecha actual

## 📝 Conventional Commits

Usa prefijos estándar en commits:

- `feat:` - Nueva funcionalidad → MINOR bump
- `fix:` - Corrección de bug → PATCH bump
- `docs:` - Solo documentación → PATCH bump
- `refactor:` - Refactorización → PATCH bump
- `BREAKING CHANGE:` - Cambio incompatible → MAJOR bump

## 🔗 Documentación

Ver documentación completa en el directorio raíz:
- `PIPELINE_README.md` - Pipeline técnico
- `CONTRIBUTING.md` - Guía de contribución
- `README.md` - Visión general del proyecto

