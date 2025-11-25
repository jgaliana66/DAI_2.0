---
name: "json-extractor"
description: "FASE 1: Extract goal fields from SwarmBuilder JSON → individual .md files (standalone invocation)"
agent: "01-json-extractor"
argument-hint: "Ruta al archivo JSON SwarmBuilder"
---

Process the SwarmBuilder JSON file (open, attached, or specified by path) and extract the `goal` attribute from each agent into individual `.md` files.

**Batch mode**: Process ALL agents in a single operation.

**Output**: `swarm/agents/{base_name}/XX-AgentName.md` files containing only goal text.
