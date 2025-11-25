# YAML Pipeline APS v4 - Specialized Sequential Agents

**Architecture**: 5 specialized agents + orchestrator prompt  
**Version**: 4.0.0  
**Date**: 2025-11-21  
**Specification**: `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md`

---

## 🎯 Architecture Overview

This pipeline replaces the monolithic `yaml-pipeline.md` agent with 5 specialized
agents that execute sequentially in strict batch-by-phase order.

### Agents

| Phase | Agent | Responsibility | Dependencies |
|-------|-------|----------------|--------------|
| FASE 1 | `01-json-extractor.md` | Extract `goal` from JSON → `.md` files | - |
| FASE 2 | `02-md2yaml-converter.md` | Convert `.md` → `.yaml` (mechanical) | `md2yaml.py` |
| FASE 3 | `03-semantic-enricher.md` | Enrich YAML with SIDs (LLM-only) | `sid_vocabulary_v1.yaml` |
| FASE 4 | `04-yaml-validator.md` | Validate enriched YAML | `yaml_lint_v6_semantic.py` |
| FASE 5 | `05-report-generator.md` | Consolidate validation reports | - |

### Orchestrator

**Location**: `.github/prompts/yaml-pipeline-v4/ORCHESTRATOR.md` (alias `@yaml-pipeline`)

**NOT an agent file** - it's a prompt/alias that loads each agent sequentially.

---

## 📦 Batch Processing Principle

**CRITICAL**: Pipeline MUST process entire batch per phase, NOT file-by-file.

```
FASE 1 → ALL files extracted
   ↓
FASE 2 → ALL files converted
   ↓
FASE 3 → ALL files enriched
   ↓
FASE 4 → ALL files validated
   ↓
FASE 5 → Consolidated report
```

---

## 🚀 Usage

```bash
# Via Copilot alias (recommended)
@yaml-pipeline swarm/json/MySwarm.json

# Manual invocation (load orchestrator instructions)
# See: .github/prompts/yaml-pipeline-v4/ORCHESTRATOR.md
```

**Expected flow** (see `ORCHESTRATOR.md` for details):
1. Loads `01-json-extractor.md` → extracts ALL goals to `.md` files
2. Loads `02-md2yaml-converter.md` → converts ALL `.md` → `.yaml` with placeholders
3. Loads `03-semantic-enricher.md` → enriches ALL `.yaml` with SIDs (100% LLM)
4. Loads `04-yaml-validator.md` → validates ALL `.yaml`, generates individual reports
5. Loads `05-report-generator.md` → consolidates reports into master report

**Output**:
- Markdown goals: `swarm/agents/{batch}/*.md`
- Enriched YAMLs: `swarm/agents/{batch}/*.yaml`
- Individual reports: `swarm/reports/validation/*_validation_*.md`
- Master report: `swarm/reports/validation/{batch}_CONSOLIDADO_FINAL_{timestamp}.md`

---

## 📚 References

- **Strategy Document**: `APS/ESTRATEGIA_AGENTES_ESPECIALIZADOS_SECUENCIALES.md`
- **Methodology**: `APS/METODOLOGIA_SWARM_FLEXIBLE_v3.5_FUSIONADA.md`
- **Validation Rules**: `APS/LINTER_RULES.md`
- **Legacy Monolithic Agent**: `.github/agents/legacy/yaml-pipeline-v3.2.0-monolithic.md`

---

## ⚠️ Key Constraints

### FASE 3 (Semantic Enricher)
- ❌ **NO code execution** (Python, JS, etc.)
- ❌ **NO pseudocode interpretation**
- ❌ **NO programmatic algorithms**
- ✅ **100% linguistic LLM reasoning**

### Orchestrator
- ❌ **NO subagents** or delegation
- ❌ **NO context switching magic**
- ✅ **Sequential loading** of agent instructions
- ✅ **Direct tool execution**

---

**Version**: 4.0.0  
**Last Updated**: 2025-11-21  
**Status**: Initial Implementation
