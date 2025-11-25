---
name: "report-generator"
description: "FASE 5: Consolidate validation reports → master report with statistics and action plan"
agent: "05-report-generator"
argument-hint: "Carpeta con reportes de validación individuales"
---

Consolidate ALL individual validation reports into a master report with:
- Executive summary (overall status, key metrics)
- File-by-file analysis (tabular)
- Top N most frequent errors/warnings (frequency analysis)
- Confidence distribution (LOW blocks for manual review)
- Prioritized action plan (CRITICAL → WARNING → REVIEW)

**Input**: Individual `.md` reports from `swarm/reports/validation/`

**Output structure**:
1. Create folder: `swarm/reports/validation/{SWARM_NAME}_{YYYYMMDD_HHMMSS}/`
2. Move all individual validation reports to this folder
3. Generate master report: `{SWARM_NAME}_CONSOLIDADO_FINAL_{YYYYMMDD_HHMMSS}.md` inside the same folder

Where:
- `{SWARM_NAME}`: Name extracted from input JSON file (e.g., J2C-v1-Swarm-v3-1)
- `{YYYYMMDD_HHMMSS}`: Timestamp of analysis start (format: 20251124_125052)

**Example output structure**:
```
swarm/reports/validation/J2C-v1-Swarm-v3-1_20251124_125052/
├── J2C-v1-Swarm-v3-1_01-Orchestrator_validation_20251124_125052.md
├── J2C-v1-Swarm-v3-1_02_validation_20251124_125100.md
├── ...
└── J2C-v1-Swarm-v3-1_CONSOLIDADO_FINAL_20251124_125101.md
```
