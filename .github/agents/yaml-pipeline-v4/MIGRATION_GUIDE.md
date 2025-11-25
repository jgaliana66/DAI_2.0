# Migration Guide: APS v3.x → v4.0

**Date**: 2025-11-21  
**From**: Monolithic yaml-pipeline v3.2.0  
**To**: Specialized agents pipeline v4.0

---

## Overview

APS v4 replaces the monolithic `yaml-pipeline.md` agent with **5 specialized sequential agents** for better modularity, maintainability, and clarity.

---

## Key Changes

### Architecture

| Aspect | v3.2.0 (Monolithic) | v4.0 (Specialized) |
|--------|---------------------|-------------------|
| **Agent count** | 1 monolithic agent | 5 specialized agents |
| **Lines of code** | 1531 lines (single file) | ~2200 lines (distributed) |
| **Execution model** | All phases in one context | Sequential phase-by-phase |
| **Semantic enrichment** | Embedded heuristics | 100% LLM linguistic reasoning |
| **Validation** | Inline checks | Dedicated validation agent + script |
| **Reporting** | Single summary | Individual + consolidated reports |

### Agent Mapping

| v3.2.0 Section | v4.0 Agent |
|----------------|-----------|
| JSON extraction | `01-json-extractor.md` (FASE 1) |
| MD → YAML conversion | `02-md2yaml-converter.md` (FASE 2) |
| Semantic enrichment | `03-semantic-enricher.md` (FASE 3) |
| Validation | `04-yaml-validator.md` (FASE 4) |
| Reporting | `05-report-generator.md` (FASE 5) |

---

## Breaking Changes

### 1. Invocation Method

**v3.2.0**:
```
@yaml-pipeline (single agent loaded)
```

**v4.0**:
```
@yaml-pipeline (orchestrator loads 5 agents sequentially)
```

**Action required**: Update aliases/instructions to reference orchestrator (`.github/prompts/yaml-pipeline-v4/ORCHESTRATOR.md`).

---

### 2. Semantic Enrichment

**v3.2.0**: Embedded heuristics in agent code (programmatic inference)

**v4.0**: 100% LLM linguistic reasoning (NO code execution)

**Impact**:
- More transparent reasoning (documented in `justificacion` field)
- Confidence scoring (HIGH/MEDIUM/LOW)
- Manual review workflow for LOW confidence blocks

**Action required**: Review LOW confidence blocks in FASE 5 consolidated report.

---

### 3. Output Structure

**v3.2.0**: Single summary output

**v4.0**: Multi-tier reporting
- Individual validation reports per file
- Consolidated master report with action plan
- Confidence analysis and error frequency analysis

**Action required**: Update downstream processes to consume new report format.

---

### 4. Batch Processing

**v3.2.0**: Could process file-by-file through all phases

**v4.0**: **MUST** process batch-by-phase (all files per phase)

**Action required**: Ensure workflows process entire batches, not individual files.

---

## Migration Steps

### Step 1: Backup Current Setup

```bash
# Backup existing agent (already done in feat/aps-v4-specialized-agents branch)
cp .github/agents/yaml-pipeline.md .github/agents/legacy/yaml-pipeline-v3.2.0-monolithic.md
```

### Step 2: Update Agent Directory

```bash
# No action needed - v4 agents are in separate directory
# .github/agents/yaml-pipeline-v4/
```

### Step 3: Update Invocation

**Option A**: Keep alias `@yaml-pipeline`, update implementation
- Update `.github/copilot-instructions.md` to reference `.github/prompts/yaml-pipeline-v4/ORCHESTRATOR.md`

**Option B**: Create new alias `@yaml-pipeline-v4`
- Keep old alias for backward compatibility
- Gradually migrate workflows

### Step 4: Test Pipeline

Run test case (see `TEST_CASE.md`):
```bash
@yaml-pipeline swarm/json/J2C-v1-Swarm-v3-5.json
```

Verify outputs:
- ✅ 11 `.md` files in `swarm/agents/J2C-v1-Swarm-v3-5/`
- ✅ 11 `.yaml` files enriched with SIDs
- ✅ 11 validation reports in `swarm/reports/validation/`
- ✅ 1 consolidated report

### Step 5: Review Confidence Analysis

Check consolidated report section "Confidence Analysis":
- Review blocks with LOW confidence
- Manually refine ambiguous descriptions
- Re-run FASE 3 if needed

### Step 6: Update Documentation

- Update README to reference v4 pipeline
- Update team workflows
- Add v4 to CHANGELOG

---

## Rollback Procedure

If issues encountered with v4:

```bash
# Restore monolithic agent
cp .github/agents/legacy/yaml-pipeline-v3.2.0-monolithic.md .github/agents/yaml-pipeline.md

# Revert alias to v3 implementation
# Edit .github/copilot-instructions.md
```

---

## Compatibility

### Scripts

| Script | v3.2.0 | v4.0 | Notes |
|--------|--------|------|-------|
| `md2yaml.py` | ✅ Used | ✅ Used | No changes |
| `yaml_lint_v6_semantic.py` | ✅ Used | ✅ Used | No changes |
| `enrich_yaml_with_llm.py` | ✅ Used | ❌ **Replaced** | v4 uses pure LLM (FASE 3) |

### Schemas

| Schema | v3.2.0 | v4.0 | Notes |
|--------|--------|------|-------|
| `aps_v3.5_rules.yaml` | ✅ | ✅ | No changes |
| `sid_vocabulary_v1.yaml` | ✅ | ✅ | No changes |

### Documentation

| Doc | v3.2.0 | v4.0 | Notes |
|-----|--------|------|-------|
| `LINTER_RULES.md` | ✅ | ✅ | No changes |
| `ESTRATEGIA_*.md` | ❌ | ✅ | New in v4 |

---

## FAQ

### Q: Can I use v3 and v4 in parallel?

**A**: Yes, during transition period. Keep both:
- v3: `.github/agents/yaml-pipeline.md`
- v4: `.github/agents/yaml-pipeline-v4/`

Use different aliases (`@yaml-pipeline` vs `@yaml-pipeline-v4`).

### Q: What happens to my existing YAML files?

**A**: v4 can re-process existing YAML files:
- Re-run FASE 3 (semantic enricher) to add `confidence` + `justificacion` fields
- Re-run FASE 4-5 (validator + report) for updated reports

### Q: Why did semantic enrichment change?

**A**: To comply with ESTRATEGIA constraint: FASE 3 must be 100% LLM linguistic reasoning, NO code execution. This ensures transparency and auditability of semantic decisions.

### Q: How do I handle LOW confidence blocks?

**A**: FASE 5 consolidated report lists them in "Confidence Analysis" section:
1. Review block description (is it clear enough?)
2. Refine description with more specific details
3. Re-run FASE 2-3 to regenerate YAML with better context

### Q: Can I skip phases?

**A**: No. Pipeline MUST execute all 5 phases sequentially. However, you can:
- Run individual agents standalone (e.g., re-run FASE 3 only)
- Process existing intermediate files (e.g., start from `.yaml` files at FASE 4)

---

## Support

- **Issues**: See v4 agent files for detailed instructions and constraints
- **Legacy reference**: `.github/agents/legacy/yaml-pipeline-v3.2.0-monolithic.md`
- **Strategy document**: `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md`

---

**Migration Status**: ✅ Documented  
**Last Updated**: 2025-11-21  
**Version**: 4.0.0
