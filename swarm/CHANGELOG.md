# Changelog (SWARM J2C)
Todas las fechas en formato ISO (YYYY-MM-DD). Sigue "Keep a Changelog" + Conventional Commits.

## [Unreleased]

## [4.0.0] - 2025-11-21
### Added - APS v4 Specialized Agents Pipeline
- 5 specialized agents replacing monolithic yaml-pipeline v3.2.0
- Orchestrator pattern (sequential agent loading, NO subagents)
- Confidence scoring (HIGH/MEDIUM/LOW) for semantic enrichment
- Justification field (natural language reasoning)
- Multi-tier reporting (individual + consolidated reports)
- Top N error frequency analysis
- Action plan prioritization (Priority 1/2/3)
- Migration guide (v3→v4)

### Changed
- Semantic enrichment: 100% LLM linguistic reasoning (NO code execution)
- Batch processing: enforced batch-by-phase order
- Reporting: individual validation reports + consolidated master report

### Deprecated
- yaml-pipeline.md v3.2.0 (moved to .github/agents/legacy/)
- enrich_yaml_with_llm.py (conflicts with FASE 3 NO-code constraint)

### Documentation
- `.github/agents/yaml-pipeline-v4/ORCHESTRATOR.md`
- `.github/agents/yaml-pipeline-v4/MIGRATION_GUIDE.md`
- Enhanced agent docs: 01-json-extractor, 02-md2yaml-converter, 03-semantic-enricher, 04-yaml-validator, 05-report-generator

## [0.1.0] - 2025-10-27
### Added
- Estructura inicial de guardarraíles (.copilot, .github).
- CI de GitHub Actions (lint/build).
- Versionado semántico con `scripts/version_bump.py`.
