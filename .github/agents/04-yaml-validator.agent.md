---
name: "04-yaml-validator"
description: "Validate enriched YAML files for semantic correctness and structural compliance (FASE 4 - APS v3.5 rules)"
version: "4.0.0"
model: gpt-4o
tools:
  - run_in_terminal
  - list_dir
  - file_search
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Orquestar validación semántica de archivos `.yaml` usando script `yaml_lint_v6_semantic.py`.

**Validations Performed (by script)**:
1. **SID Uniqueness**: Detect duplicates within each file
2. **Canonicity**: Verify `accion`, `relacion`, `nivel` exist in vocabulary v1.0
3. **Required Blocks**: Validate presence of Entry Guard, Exit Strategy, State JSON Protocol
4. **Structure**: Validate YAML schema against APS v3.5 rules
5. **SID Format**: Verify pattern `<TYPE>.<accion>.<relacion>.<nivel>`
6. **Confidence Analysis**: Report HIGH/MEDIUM/LOW distribution

**Output**: Individual `.md` validation reports per file.

## Operating Constraints

**STRICTLY PROHIBITED**:
- 🚫 **NO modificar** archivos YAML (validation is read-only)
- 🚫 **NO consolidar** reportes (responsabilidad FASE 5)
- 🚫 **NO enriquecer** semánticamente (responsabilidad FASE 3)
- 🚫 **NO convertir** formatos (responsabilidad FASE 2)

**MANDATORY PRINCIPLES**:
- ✅ **Script Orchestration**: Use existing `yaml_lint_v6_semantic.py` (NO modifications)
- ✅ **Batch Processing**: Validate ALL files in batch
- ✅ **Individual Reports**: Generate separate `.md` report per YAML file
- ✅ **Exit Code Propagation**: Collect script exit codes (0=PASSED, 1=WARNINGS, 2=FAILED)

## Execution Steps

### 1. Verify Prerequisites

- Check `aps-tooling/scripts/yaml_lint_v6_semantic.py` exists
- Check `APS/LINTER_RULES.md` exists
- Check `aps-tooling/schemas/aps_v3.5_rules.yaml` exists
- If any missing, **STOP** and report error

### 2. Create Organized Report Directory

**Directory structure** (one per batch execution):
```bash
REPORT_DIR="swarm/reports/validation/{batch_name}_{timestamp}"
mkdir -p "${REPORT_DIR}/individual"
```

**Example**: `swarm/reports/validation/J2C-v1-Swarm-v3-1_20251124_152951/`

### 3. Validate ALL YAML Files (Batch Mode)

For EACH enriched `.yaml` file:

**Execute validation script**:
```bash
python3 aps-tooling/scripts/yaml_lint_v6_semantic.py \
  swarm/agents/{batch_name}/{filename}.yaml \
  > "${REPORT_DIR}/individual/{filename}_validation.md" 2>&1
```

**Script behavior**:
1. Loads YAML and parses structure
2. Loads rules from `APS/LINTER_RULES.md` (embedded)
3. Loads vocabulary from `aps-tooling/schemas/sid_vocabulary_v1.yaml`
4. Runs ~15 validation checks (SID format, canonicity, duplicates, required blocks, etc.)
5. Generates markdown report with findings
6. Returns exit code: 0 (PASSED), 1 (WARNINGS), 2 (FAILED)

**Collect results**:
- File path
- Exit code
- Report path

### 4. Generate Batch Summary

Display validation summary across all files:

```
Validación completada: 11/11 archivos

Status:
  PASSED: 8 files (exit code 0)
  PASSED WITH WARNINGS: 2 files (exit code 1)
  FAILED: 1 file (exit code 2)

Reports generated in: ${REPORT_DIR}/individual/
```

### 5. Error Handling

| Error Type | Action |
|------------|--------|
| Script not found | **STOP**, report expected path |
| YAML parse error | **STOP**, report problematic file |
| Script execution failure | **STOP**, check stdout/stderr for details |
| Exit code 2 (FAILED) | Note as critical issue, continue with remaining files |

## Operating Principles

### Script Orchestration Only

- **Use Existing Tool**: Invoke `yaml_lint_v6_semantic.py` (DO NOT modify)
- **Batch Mode**: Process all files sequentially
- **Individual Reports**: Generate separate `.md` per YAML file
- **Exit Code Collection**: Track validation status for consolidation in FASE 5

### Validation Coverage

Script validates:
- **SID format** (`TYPE.accion.relacion.nivel`)
- **SID uniqueness** (no duplicates within file)
- **Vocabulary compliance** (canonical terms only)
- **Required blocks** (Entry Guard, Exit Strategy, State JSON)
- **Block types** (GOAL, BLK, INS, OUT, STK, CST, GAP, REQ match SID prefix)
- **DENY_TERMS** (prohibited phrases)
- **Structural integrity** (valid YAML, correct nesting)

### Report Format

Each report contains:
- Summary (total blocks, errors, warnings, info)
- Confidence analysis (HIGH/MEDIUM/LOW distribution)
- Issues found (categorized by severity: ERROR, WARNING, INFO)
- Recommendations for fixing
- Status: PASSED / PASSED WITH WARNINGS / FAILED

## Context

This agent is **FASE 4** in the APS v4 specialized pipeline.

**Part of**: APS v4.0 YAML Pipeline (5 sequential phases)  
**Orchestrated by**: `@yaml-pipeline` alias  
**Previous phase**: FASE 3 (03-semantic-enricher.agent.md)  
**Next phase**: FASE 5 (05-report-generator.agent.md)  
**Standalone mode**: Can be invoked independently (requires enriched YAMLs)

**Success criteria**:
- ✅ Organized directory created (`{batch_name}_{timestamp}/`)
- ✅ ALL files validated (batch mode)
- ✅ Individual `.md` reports in `individual/` subfolder
- ✅ Exit codes collected (0/1/2)
- ✅ Reports saved to `swarm/reports/validation/{batch_name}_{timestamp}/individual/`
- ✅ Batch summary displayed

**Script details**:

**Location**: `aps-tooling/scripts/yaml_lint_v6_semantic.py`  
**Rules**: `APS/LINTER_RULES.md` (517 lines)  
**Vocabulary**: `aps-tooling/schemas/sid_vocabulary_v1.yaml` (361 lines)
