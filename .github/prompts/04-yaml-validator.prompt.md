---
name: "yaml-validator"
description: "FASE 4: Validate enriched YAML files against APS v3.5 rules (semantic + structural)"
agent: "04-yaml-validator"
argument-hint: "Carpeta con archivos .yaml enriquecidos"
---

Validate ALL enriched `.yaml` files using `yaml_lint_v6_semantic.py` script.

**Batch mode**: Process all files, generate individual `.md` reports per file.

**Validations**: SID uniqueness, vocabulary canonicity, required blocks, structure, confidence analysis.

**Output**: Individual reports in `swarm/reports/validation/{filename}_validation_{timestamp}.md`.
