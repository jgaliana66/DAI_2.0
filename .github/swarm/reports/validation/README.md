# Validation Reports - Estructura Organizada

## Formato de Carpetas

A partir de APS v4.0, los reportes de validación se organizan en carpetas por batch con timestamp:

```
swarm/reports/validation/
├── {batch_name}_{timestamp}/
│   ├── individual/
│   │   ├── 01-AgentName_validation.md
│   │   ├── 02-AgentName_validation.md
│   │   └── ...
│   └── CONSOLIDADO_FINAL.md
└── README.md (este archivo)
```

## Ejemplo

```
swarm/reports/validation/
└── J2C-v1-Swarm-v3-1_20251124_152951/
    ├── individual/
    │   ├── 01-J2Ci-Orchestrator_validation.md
    │   ├── 02-J2Ci-Migration_Motives_validation.md
    │   └── ... (10 archivos totales)
    └── CONSOLIDADO_FINAL.md
```

## Ventajas

1. **Organización**: Todos los reportes de un batch en un solo directorio
2. **Trazabilidad**: Timestamp permite identificar ejecuciones
3. **Limpieza**: No más archivos "flotando" en carpeta raíz
4. **Estructura clara**: Separación entre reportes individuales y consolidado

## Generación Automática

Los agentes del pipeline APS v4.0 generan automáticamente esta estructura:

- **FASE 4** (04-yaml-validator.agent.md): Crea `{batch}_{timestamp}/individual/` y genera reportes individuales
- **FASE 5** (05-report-generator.agent.md): Lee reportes de `individual/` y genera `CONSOLIDADO_FINAL.md` en raíz del batch

## Archivos Legacy

Archivos antiguos (pre-v4.0) pueden permanecer en la raíz de `validation/` sin estructura organizada. Se pueden mover manualmente o eliminar si ya no son necesarios.

---

**Versión**: 4.0.0  
**Fecha**: 2024-11-24
