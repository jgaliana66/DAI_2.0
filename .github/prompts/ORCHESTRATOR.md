# YAML Pipeline APS v4 - Orchestrator Instructions

**Version**: 4.0.0  
**Date**: 2025-11-21  
**Architecture**: Sequential 5-agent pipeline  
**Alias**: `@yaml-pipeline`

---

## 🚀 Quick Start - Copy & Paste Prompt

```markdown
Ejecuta el pipeline APS v4.0 completo sobre el archivo JSON adjunto/abierto:

**Instrucciones:**
1. Identifica el archivo JSON SwarmBuilder (abierto, adjunto, o ruta especificada)
2. Ejecuta las 5 fases secuencialmente en modo batch-by-phase:
   - FASE 1: Extrae goal → .md (carga .github/agents/01-json-extractor.agent.md)
   - FASE 2: Convierte .md → .yaml (carga 02-md2yaml-converter.agent.md)
   - FASE 3: Enriquece semánticamente (carga 03-semantic-enricher.agent.md) - 100% LLM
   - FASE 4: Valida YAMLs (carga 04-yaml-validator.agent.md)
   - FASE 5: Genera reporte maestro (carga 05-report-generator.agent.md)
3. Muestra resumen tras cada fase antes de continuar

**Restricciones:**
- ❌ NO subagentes ni delegación
- ❌ NO procesamiento file-by-file (batch completo por fase)
- ✅ Carga secuencial de instrucciones (uno por uno)
- ✅ FASE 3: 100% razonamiento lingüístico (NO código)

**Archivo JSON**: [especificar ruta o "detectar del contexto"]

Comienza con FASE 1.
```

**Ejemplo de uso**:
```
Ejecuta el pipeline APS v4.0 completo sobre swarm/swarm.json
[pegar prompt de arriba]
```

---

## Purpose

This orchestrator coordinates the execution of 5 specialized agents in strict sequential order to process SwarmBuilder JSON files through the complete APS v3.5 pipeline.

**NOT an agent file** - this is a **prompt/instruction set** for sequential agent loading.

---

## Architecture Overview

```
User Input (JSON file)
    ↓
FASE 1: JSON Goal Extractor (01-json-extractor.md)
    ↓ (ALL .md files created)
FASE 2: MD2YAML Converter (02-md2yaml-converter.md)
    ↓ (ALL .yaml files with placeholders)
FASE 3: Semantic Enricher (03-semantic-enricher.md)
    ↓ (ALL .yaml files with SIDs)
FASE 4: YAML Validator (04-yaml-validator.md)
    ↓ (ALL individual reports)
FASE 5: Report Generator (05-report-generator.md)
    ↓ (Consolidated master report)
User Output (Reports + enriched YAMLs)
```

---

## Orchestration Workflow

### Phase 1: Initialize

**User invokes orchestrator**:
```
@yaml-pipeline path/to/swarm.json
```

**Orchestrator response**:
```
🚀 APS v4 Pipeline Initiated

Input: path/to/swarm.json
Phases: 5 (JSON extraction → MD conversion → Semantic enrichment → Validation → Reporting)

Starting FASE 1...
```

---

### Phase 2: Sequential Agent Execution

**CRITICAL PRINCIPLES**:
- ❌ **NO subagents** or delegation mechanisms
- ❌ **NO context switching magic** between agents
- ✅ **Sequential loading** of agent instructions (one at a time)
- ✅ **Direct tool execution** by orchestrator following each agent's instructions
- ✅ **Batch-by-phase**: Complete ALL files in each phase before advancing

---

#### FASE 1: JSON Goal Extractor

**Load agent**: `.github/agents/01-json-extractor.md`

**Execute instructions**:
1. Detect JSON file from context (open file, attached, or user-provided path)
2. Validate JSON structure (`agents` field present)
3. Create folder: `swarm/agents/{base_name}/`
4. Copy JSON to new folder
5. Extract `goal` field from ALL agents → individual `.md` files
6. Generate summary (files created, count)

**Success criteria**:
- ✅ N `.md` files created = N agents in JSON
- ✅ Files in `swarm/agents/{base_name}/XX-AgentName.md`
- ✅ Each file contains ONLY goal text (no headers, no metadata)

**On completion**: Display summary, proceed to FASE 2.

---

#### FASE 2: MD2YAML Converter

**Load agent**: `.github/agents/02-md2yaml-converter.md`

**Execute instructions**:
1. Verify `aps-tooling/scripts/md2yaml.py` exists
2. Invoke script in batch mode:
   ```bash
   python3 aps-tooling/scripts/md2yaml.py swarm/agents/{base_name}/
   ```
3. Verify output: count `.yaml` files = count `.md` files
4. Spot check 2-3 YAML files for placeholder integrity (`<<PENDING_AI>>`)
5. Generate summary (files converted, success rate)

**Success criteria**:
- ✅ All `.md` → `.yaml` conversion complete
- ✅ All semantic fields contain `<<PENDING_AI>>`
- ✅ Temporary SIDs: `TEMP_{block_type}_{NNN}`
- ✅ Exit code 0

**On completion**: Display summary, proceed to FASE 3.

---

#### FASE 3: Semantic Enricher (CRITICAL - 100% LLM)

**Load agent**: `.github/agents/03-semantic-enricher.md`

**Execute instructions**:
1. Load vocabulary: `aps-tooling/schemas/sid_vocabulary_v1.yaml`
2. For EACH `.yaml` file:
   - Read blocks with `<<PENDING_AI>>` placeholders
   - Analyze `content` field linguistically
   - Compare semantically with vocabulary terms
   - Select best match: `accion`, `relacion`, `nivel`
   - Generate SID: `{block_type}.{accion}.{relacion}.{nivel}`
   - Assign confidence: HIGH/MEDIUM/LOW
   - Document reasoning in `justificacion`
   - Update YAML file
3. Handle batches (sub-batches of 8-10 files if >20 total)
4. Generate statistics (total enriched, confidence distribution)

**Success criteria**:
- ✅ All placeholders `<<PENDING_AI>>` replaced
- ✅ SIDs follow convention: `{block_type}.{accion}.{relacion}.{nivel}`
- ✅ All blocks have `confidence` and `justificacion` fields
- ✅ NO code execution (100% linguistic reasoning)

**On completion**: Display enrichment statistics, proceed to FASE 4.

---

#### FASE 4: YAML Validator

**Load agent**: `.github/agents/04-yaml-validator.md`

**Execute instructions**:
1. Verify `aps-tooling/scripts/yaml_lint_v6_semantic.py` exists
2. For EACH enriched `.yaml` file:
   ```bash
   python3 aps-tooling/scripts/yaml_lint_v6_semantic.py \
     swarm/agents/{base_name}/{file}.yaml \
     --output swarm/reports/validation/{file}_validation_{timestamp}.md
   ```
3. Collect exit codes (0/1/2)
4. Verify report generation
5. Generate summary (files validated, exit code distribution, confidence aggregate)

**Success criteria**:
- ✅ All files validated (reports generated)
- ✅ Exit codes collected: 0 (PASSED), 1 (WARNINGS), 2 (FAILED)
- ✅ Individual reports in `swarm/reports/validation/`

**On completion**: Display validation summary, proceed to FASE 5.

---

#### FASE 5: Report Generator

**Load agent**: `.github/agents/05-report-generator.md`

**Execute instructions**:
1. Locate individual reports: `swarm/reports/validation/*_validation_*.md`
2. Parse each report (metrics, confidence, issues)
3. Aggregate global statistics
4. Identify top 5+ error/warning patterns
5. Analyze confidence distribution
6. Generate action plan (Priority 1/2/3)
7. Write consolidated report:
   `swarm/reports/validation/{batch}_CONSOLIDADO_FINAL_{timestamp}.md`
8. Display summary to user

**Success criteria**:
- ✅ Consolidated report generated with 6 sections
- ✅ Top N errors identified (N≥5)
- ✅ Actionable recommendations provided
- ✅ References to APS documentation

**On completion**: Display path to consolidated report, pipeline complete.

---

### Phase 3: Finalization

**Display final summary**:
```
✅ APS v4 Pipeline Completed

Batch: {base_name}
Files processed: {count}

Phase Results:
  FASE 1: {n} .md files extracted
  FASE 2: {n} .yaml files converted
  FASE 3: {n} blocks enriched (HIGH: {h}%, MEDIUM: {m}%, LOW: {l}%)
  FASE 4: {n} files validated (PASSED: {p}, WARNINGS: {w}, FAILED: {f})
  FASE 5: Consolidated report generated

📊 Final Report:
swarm/reports/validation/{batch}_CONSOLIDADO_FINAL_{timestamp}.md

📁 Output Files:
- Markdown goals: swarm/agents/{base_name}/*.md
- Enriched YAMLs: swarm/agents/{base_name}/*.yaml
- Validation reports: swarm/reports/validation/

Next Steps:
{action plan based on FASE 5 report}
```

---

## Error Handling

**If any FASE fails**:
1. **STOP** pipeline immediately
2. Display error message with:
   - Which FASE failed (1-5)
   - What error occurred
   - Which file caused the error (if applicable)
3. Provide troubleshooting guidance:
   - FASE 1: Check JSON structure, file path
   - FASE 2: Check md2yaml.py script, Python environment
   - FASE 3: Check vocabulary file, YAML parseability
   - FASE 4: Check validator script, rules files
   - FASE 5: Check individual reports exist

**Do NOT**:
- ❌ Continue to next FASE after error
- ❌ Silently skip failed files
- ❌ Generate partial results without warning

---

## Constraints - CRITICAL

### Orchestrator Behavior

- ❌ **NO subagents**: Do NOT invoke agents as autonomous entities
- ❌ **NO delegation**: Do NOT transfer control to other agents
- ❌ **NO context switching**: Do NOT simulate multi-agent communication
- ❌ **NO magic**: Do NOT use unspecified coordination mechanisms

- ✅ **Sequential loading**: Load ONE agent's instructions, execute, move to next
- ✅ **Direct execution**: Orchestrator executes tools directly following agent instructions
- ✅ **Batch processing**: Complete ALL files per phase before advancing
- ✅ **Progress tracking**: Display phase completion and intermediate results

### Phase Isolation

Each FASE must complete for ALL files before advancing:
- FASE 1: ALL goals extracted → THEN advance
- FASE 2: ALL yamls converted → THEN advance
- FASE 3: ALL yamls enriched → THEN advance
- FASE 4: ALL yamls validated → THEN advance
- FASE 5: Consolidation complete → THEN finish

**NEVER**: Process file-by-file through all phases (prohibited in ESTRATEGIA).

---

## Usage Examples

### Example 1: Basic Invocation

```
User: @yaml-pipeline swarm/json/J2C-v1-Swarm-v3-5.json

Orchestrator:
🚀 APS v4 Pipeline Initiated
Input: swarm/json/J2C-v1-Swarm-v3-5.json

[FASE 1] Loading 01-json-extractor.md...
[FASE 1] Detecting JSON file...
[FASE 1] Creating folder swarm/agents/J2C-v1-Swarm-v3-5/...
[FASE 1] Extracting goals from 11 agents...
✅ [FASE 1] Complete: 11 .md files created

[FASE 2] Loading 02-md2yaml-converter.md...
[FASE 2] Executing md2yaml.py on 11 files...
✅ [FASE 2] Complete: 11 .yaml files generated

[FASE 3] Loading 03-semantic-enricher.md...
[FASE 3] Loading vocabulary (sid_vocabulary_v1.yaml)...
[FASE 3] Enriching 127 blocks across 11 files...
✅ [FASE 3] Complete: HIGH 70%, MEDIUM 24%, LOW 6%

[FASE 4] Loading 04-yaml-validator.md...
[FASE 4] Validating 11 files...
✅ [FASE 4] Complete: PASSED 7, WARNINGS 4, FAILED 0

[FASE 5] Loading 05-report-generator.md...
[FASE 5] Consolidating 11 validation reports...
✅ [FASE 5] Complete: Report generated

📊 Final Report: swarm/reports/validation/J2C-v1-Swarm-v3-5_CONSOLIDADO_FINAL_20251121_150000.md
```

### Example 2: Error Handling

```
User: @yaml-pipeline swarm/json/broken.json

Orchestrator:
🚀 APS v4 Pipeline Initiated
Input: swarm/json/broken.json

[FASE 1] Loading 01-json-extractor.md...
[FASE 1] Detecting JSON file...
❌ [FASE 1] ERROR: Invalid JSON structure

Details:
- File: swarm/json/broken.json
- Issue: Missing "agents" field
- Expected structure: {"agents": [...]}

Pipeline STOPPED at FASE 1.
Please fix the JSON file and retry.
```

---

## Integration with Copilot

**Alias setup** (in `.github/copilot-instructions.md` or workspace settings):

```markdown
## Custom Agent Aliases

### @yaml-pipeline

Execute the APS v4 specialized pipeline for SwarmBuilder JSON processing.

**Purpose**: Process SwarmBuilder JSON files through 5 specialized agents (extraction, conversion, enrichment, validation, reporting).

**Usage**: `@yaml-pipeline path/to/swarm.json`

**Behavior**: Load and execute agents sequentially from `.github/agents/` (01→02→03→04→05).

**Implementation**: Follow instructions in `.github/prompts/ORCHESTRATOR.md`.
```

---

## Version History

- **v4.0.0** (2025-11-21): Initial APS v4 specialized agents architecture
- **v3.2.0** (legacy): Monolithic yaml-pipeline.md (deprecated, see `.github/agents/legacy/`)

---

## References

- **Strategy Document**: `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md`
- **Methodology**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Agent Specs**: `.github/agents/01-05-*.agent.md`
- **Legacy Agent**: `.github/agents/legacy/yaml-pipeline-v3.2.0-monolithic.md`

---

**Status**: Production Ready  
**Tested**: Pending (see PASO 10)  
**Maintainer**: Architecture Team
