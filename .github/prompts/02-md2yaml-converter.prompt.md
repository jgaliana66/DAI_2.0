---
name: "md2yaml-converter"
description: "FASE 2: Convert .md files → .yaml with placeholders (mechanical conversion, NO semantic inference)"
agent: "02-md2yaml-converter"
argument-hint: "Carpeta o patrón glob de archivos .md"
---

Convert ALL `.md` files in the specified directory to `.yaml` structure with APS v3.5 schema.

**Batch mode**: Process entire directory or glob pattern in single invocation.

**Script**: Uses `aps-tooling/scripts/md2yaml.py` for mechanical conversion.

**Output**: `.yaml` files with `<<PENDING_AI>>` placeholders for all semantic fields.
