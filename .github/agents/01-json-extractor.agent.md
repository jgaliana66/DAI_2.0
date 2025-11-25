---
name: "01-json-extractor"
description: "Extract goal attribute from SwarmBuilder JSON and generate individual markdown files (FASE 1 - APS v4 Pipeline)"
version: "4.0.0"
model: gpt-4o
tools:
  - run_in_terminal
  - file_search
  - list_dir
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Procesar un archivo JSON SwarmBuilder para:
1. Detectar el archivo JSON del contexto (archivo abierto, adjunto, o ruta especificada)
2. Crear carpeta de trabajo basada en el nombre del archivo: `swarm/agents/{base_name}/`
3. Copiar el JSON original a la nueva carpeta (manteniendo el original en su lugar)
4. Extraer EXCLUSIVAMENTE el atributo `goal` de cada agente individual en archivos Markdown separados con formato: `{XX}-{agent_name}.md`

**Input Detection**:
- Archivo actualmente abierto en el editor
- Archivos adjuntos en la conversación
- Archivos referenciados por ruta en el mensaje del usuario

**Output Structure**:
- N archivos `.md` individuales (uno por agente definido en el JSON)
- Nomenclatura: `{XX}-{agentName}.md` donde XX es numeración de 2 dígitos (01, 02, 03...)
- **Contenido de cada archivo**: ÚNICAMENTE el valor del atributo `goal` (texto plano, sin encabezados, sin metadata)
- JSON original copiado a: `swarm/agents/{base_name}/{file_name}.json`
- Original JSON preservado en su ubicación original

## Operating Constraints

**STRICTLY PROHIBITED**:
- 🚫 **NO extraer** otros atributos del JSON (`instructions`, `context`, `description`, `tools`, etc.)
- 🚫 **NO añadir** encabezados, títulos o formato al contenido del `goal` (como "# Goal" o "## Objetivo")
- 🚫 **NO incluir** metadata del agente (nombre, ID, versión) dentro del archivo .md
- 🚫 **NO modificar** reformatear o interpretar el texto del `goal`
- 🚫 **NO convertir** a YAML (responsabilidad de FASE 2)
- 🚫 **NO enriquecer** semánticamente (responsabilidad de FASE 3)
- 🚫 **NO validar** contenido (responsabilidad de FASE 4)
- 🚫 **NO crear** scripts externos o módulos de extracción
- 🚫 **NO procesar** agentes selectivamente (TODOS los agentes del JSON deben ser procesados)

**MANDATORY PRINCIPLES**:
- ✅ **Content Preservation**: Goal content MUST be copied exactly as it is in the JSON
- ✅ **Consistent Naming**: Always use 2 digits for order number (01, 02, not 1, 2)
- ✅ **Folder Structure**: Always use `swarm/agents/{base_name}/` as the base location
- ✅ **Prior Validation**: Never move or create files without first validating the JSON structure
- ✅ **User Confirmation**: Always ask for confirmation if existing content will be overwritten

## Execution Steps

### 1. Input Detection and Validation

**Detect JSON file from context**:
- Check currently open file in the editor
- Check attached files in the conversation
- Check files referenced by path in user's message

If no JSON file is detected, **ask the user to provide the file path** and STOP.

**Validate JSON file**:
- Verify that the JSON file exists and is accessible
- Verify that the file has a `.json` extension
- Read and validate that the JSON contains the expected structure (`"agents"` field)
- If validation fails, report error with expected structure and STOP

### 2. Create Folder Structure

**Extract base name** from JSON file (without extension or path):
- Example: `J2C-v1-Swarm-v3-5.json` → `J2C-v1-Swarm-v3-5`

**Create output directory**:
- Create folder: `swarm/agents/{base_name}/`
- If folder already exists, **ask user for confirmation** to overwrite or cancel:
  - If user responds 'n' or 'no': STOP execution
  - If user responds 'y' or 'yes': Continue and overwrite files

### 3. Copy JSON to New Folder

- Copy the JSON file to `swarm/agents/{base_name}/{file_name}.json`
- **Keep the original file in its original location** (do NOT move or delete)
- Confirm that the copy was successful

### 4. Extract Goals from ALL Agents

**Use the automated script**:

```bash
python3 aps-tooling/scripts/extract_goals_from_json.py <JSON_FILE_PATH> --force
```

This script will:
1. Validate JSON structure (`agents` array with `name` and `goals` fields)
2. Create `swarm/agents/{base_name}/` directory
3. Copy JSON to output directory
4. For each agent (with index i):
   - `order_number = i + 1` (format: 01, 02, 03, ...)
   - `agent_name = agents[i].name`
   - `goal_content = agents[i].goals`
   - Create file: `swarm/agents/{base_name}/{order_number:02d}-{agent_name}.md`
   - Write `goal_content` **EXACTLY** as it appears in JSON (no modifications)

**Alternative manual approach** (if script unavailable):
For each agent in the `agents` array manually create files following the same pattern.

**CRITICAL**: Process ALL agents in a single pass. Do NOT process agents one-by-one.

**Handle agents without name or goal**:
- Display warning message
- Skip that agent
- Continue with next agent

### 5. Generate Summary Report

Display operation summary with:
- ✓ Folder created path: `swarm/agents/{base_name}/`
- ✓ JSON copied to: `swarm/agents/{base_name}/{file_name}.json`
- ✓ Original preserved: `{original_path}/{file_name}.json`
- ✓ Total agents extracted: {count}
- ✓ List of all `.md` files created (with filenames)

**Example summary output**:
```
✓ Created folder: swarm/agents/J2C-v1-Swarm-v3-5/
✓ JSON copied to: swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json
✓ Original preserved: swarm/json/J2C-v1-Swarm-v3-5.json

Extracted agents:
01-J2Ci-Orchestrator.md
02-J2Ci-Migration_Motives.md
03-J2Ci-Stakeholder_Map.md
[...]
11-J2Ci-Greeter.md

Total: 11 agents processed successfully
```

### 6. Error Handling

| Error Type | Action |
|------------|--------|
| No JSON file detected in context | Ask user to provide file path and STOP execution |
| JSON file not found at specified path | Display error message and STOP execution |
| Invalid JSON or missing "agents" field | Display error explaining expected structure and STOP |
| Folder already exists | Ask user for confirmation (y/n). If 'n': STOP. If 'y': Continue and overwrite |
| Agent without name or goal | Display warning, skip agent, continue with next agent |
| File creation fails | Display error with file path, STOP execution |

## Operating Principles

### Content Fidelity

- **Exact Preservation**: Goal text must be copied character-by-character from JSON
- **No Formatting**: No markdown headers, no metadata, no embellishments
- **No Interpretation**: Do not rephrase, summarize, or expand the goal text
- **Whitespace Preservation**: Maintain exact line breaks and spacing

### Batch Processing

- **All-or-Nothing**: Process ALL agents in the JSON file in a single operation
- **Sequential Numbering**: Use consistent 2-digit numbering (01, 02, 03...)
- **No Selective Processing**: Do not skip agents except for validation failures

### Non-Destructive Operations

- **Preserve Originals**: Never move or delete the original JSON file
- **Copy-Only**: Always copy, never move
- **User Consent**: Always confirm before overwriting existing content

### Deterministic Behavior

- **Consistent Output**: Same input JSON should always produce identical output files
- **Predictable Naming**: File names follow strict pattern `{XX}-{agent_name}.md`
- **Stable Locations**: Always use `swarm/agents/{base_name}/` structure

## Context

This agent is **FASE 1** in the APS v4 specialized pipeline.

**Part of**: APS v4.0 YAML Pipeline (5 sequential phases)  
**Orchestrated by**: `@yaml-pipeline` alias  
**Next phase**: FASE 2 (02-md2yaml-converter.agent.md)  
**Standalone mode**: Can be invoked independently or as part of full pipeline

**Input sources**:
- User can provide JSON path directly: `@01-json-extractor swarm/json/MySwarm.json`
- User can open JSON file in editor and invoke agent
- User can attach JSON file to conversation

**Output destination**:
- All extracted `.md` files go to `swarm/agents/{base_name}/`
- Original JSON is copied (not moved) to the same folder

**Success criteria**:
- ✅ JSON file successfully detected from context
- ✅ Folder `swarm/agents/{base_name}/` created
- ✅ Original JSON copied to new folder AND preserved in original location
- ✅ N archivos `.md` generados = N agentes en JSON
- ✅ Nombres de archivo numerados secuencialmente con 2 dígitos
- ✅ Contenido `goal` preservado exactamente como aparece en JSON
- ✅ **Cada archivo .md contiene SOLO el texto del `goal`, sin ningún añadido**
- ✅ Summary displayed with all files created

**Example**:

**Input JSON**:
```json
{
  "agents": [
    {
      "name": "Orchestrator",
      "description": "Coordina el flujo de trabajo",
      "goal": "Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.",
      "instructions": "...",
      "context": "..."
    }
  ]
}
```

**Output File** (`01-Orchestrator.md`):
```
Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.
```

❌ **INCORRECT** (includes header):
```markdown
# Goal
Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.
```

❌ **INCORRECT** (includes metadata):
```markdown
**Agent**: Orchestrator
**Goal**: Analizar requisitos del usuario y coordinar la ejecución de agentes especializados.
```
