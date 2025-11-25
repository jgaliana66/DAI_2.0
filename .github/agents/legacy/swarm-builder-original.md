---
description: Build a new SwarmBuilder JSON from markdown files and a template JSON, updating version numbers
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Create a new SwarmBuilder JSON file by:
1. Reading a template JSON file (source swarm)
2. Reading markdown files from the corresponding agent folder
3. Updating all `goals` fields with markdown content
4. Replacing version strings throughout the JSON
5. Generating a new JSON file with updated version

## Operating Constraints

- **NEVER modify the source JSON** (read-only)
- **Version format**: `vMAJOR-MINOR` (e.g., `v3-5`, `v4-1`)
- **Simple string replacement**: Replace old version with new version in all `id` and `name` fields
- **Preserve structure**: Keep all other JSON fields unchanged
- **Sequential matching**: Match `.md` files (01-, 02-, 03-...) with agents array order

## Input Detection

Automatically detect from user input or workspace:
- Source JSON file (template)
- Folder with numbered `.md` files
- Old version (extract from JSON filename/content)
- New version (user specifies: e.g., "v3-6", "v4-0")

If any input is missing, ask the user to provide it.

## Execution Steps

### 1. Validate Input

- Verify source JSON exists and is readable
- Verify JSON has `"agents"` array
- Verify markdown folder exists
- Extract old version from JSON (e.g., `v3-5` from `J2C-v1-Swarm-v3-5.json`)
- Confirm new version with user (e.g., "Change from v3-5 to v3-6?")

### 2. Read Markdown Files

- List all `.md` files in folder matching pattern: `{XX}-*.md`
- Sort by number prefix (01, 02, 03...)
- Verify count matches number of agents in JSON
- Read content of each markdown file

### 3. Create New JSON Structure

- Deep copy the source JSON structure
- For each agent in the `agents` array (with index i):
  - Read corresponding markdown file: `{i+1:02d}-*.md`
  - **Replace old version with new version INSIDE markdown content** (e.g., `v3-5` → `v3-6`)
  - Replace `agents[i].goals` with updated markdown content
  - Update `agents[i].id`: replace old version with new version
  - Update `agents[i].name` if it contains version string
- Update swarm-level `id`: replace old version with new version
- Update swarm-level `name`: replace old version with new version

### 4. Version Replacement Logic

**String replacement in TWO places:**

1. **Inside markdown content (goals field):**
   - Find all occurrences of old version pattern in markdown content (e.g., `v3-5`, `v3.5`, `3.5`)
   - Replace with new version pattern (e.g., `v3-6`)
   - Common patterns to replace:
     - `v3-5` → `v3-6`
     - `v3.5` → `v3.6` (if present)
     - `3.5.1` → `3.6.0` (state_version format)

2. **In JSON structure (id/name fields):**
   - Find all occurrences of old version in `id` and `name` fields
   - Replace with new version pattern

**Example transformations:**
- `J2C-v1-Swarm-v3-5` → `J2C-v1-Swarm-v3-6`
- `J2Ci-v1-Orchestrator-v3-5` → `J2Ci-v1-Orchestrator-v3-6`
- `"state_version": "3.5.1"` → `"state_version": "3.6.0"` (in markdown content)
- `updated_by="J2Ci-Migration_Motives"` → unchanged (agent names don't have versions)

### 5. Generate Output File

- Create new filename based on new version: `J2C-v1-Swarm-{new_version}.json`
- Write JSON with proper formatting (indent=2)
- Save to `swarm/json/` directory (or user-specified location)
- Confirm file was created successfully

### 6. Generate Summary

Display operation summary:
- Source JSON used (with old version)
- New JSON created (with new version)
- Number of agents processed
- Number of markdown files integrated
- List of version changes made

## Output Format

### File Name Convention

```
J2C-v1-Swarm-{new_version}.json
```

Where `{new_version}` is the new version specified by user (e.g., `v3-6`)

### JSON Structure

Preserve exact structure of source JSON, only modifying:
- `id` fields (version replacement)
- `name` fields (version replacement where applicable)
- `goals` fields (replaced with markdown content)

## Error Handling

- **Source JSON not found**: Display error with path and stop
- **Invalid JSON structure**: Display error explaining expected structure and stop
- **Missing agents array**: Display error and stop
- **Markdown folder not found**: Display error with expected path and stop
- **Mismatch in agent count**: Display warning showing counts and ask user to confirm
- **Missing markdown file**: Display error with expected filename and stop
- **Invalid version format**: Suggest correct format (`vMAJOR-MINOR`) and stop

## Example Execution

**User input:**
```
Create new swarm v3-6 from swarm/agents/J2C-v1-Swarm-v3-5
```

**Process:**
1. Detect source JSON: `swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json`
2. Detect markdown folder: `swarm/agents/J2C-v1-Swarm-v3-5/`
3. Old version: `v3-5`
4. New version: `v3-6`
5. Read 11 markdown files (01- through 11-)
6. Update all `goals` and version strings
7. Generate: `swarm/json/J2C-v1-Swarm-v3-6.json`

**Output:**
```
✓ Source JSON: swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json
✓ Old version: v3-5
✓ New version: v3-6

Processing agents:
  01-J2Ci-Orchestrator.md → Agent 1 ✓
  02-J2Ci-Migration_Motives.md → Agent 2 ✓
  03-J2Ci-Stakeholder_Map.md → Agent 3 ✓
  04-J2Ci-ASIS_Context.md → Agent 4 ✓
  05-J2Ci-Risks_Constraints.md → Agent 5 ✓
  06-J2Ci-GAP_Analysis.md → Agent 6 ✓
  07-J2Ci-Requirements_Facilitator.md → Agent 7 ✓
  08-J2Ci-Documentation_Aggregator.md → Agent 8 ✓
  09-J2Ci-Methodology_Assurance-DISABLED.md → Agent 9 ✓
  10-J2Ci-Question_Suggester.md → Agent 10 ✓
  11-J2Ci-Greeter.md → Agent 11 ✓

✓ Created: swarm/json/J2C-v1-Swarm-v3-6.json

Summary:
- Agents processed: 11
- Version changes: v3-5 → v3-6
- Goals updated from markdown: 11
- Source JSON unchanged: ✓
```

## Operating Principles

### Preserve Source Integrity
- Source JSON is NEVER modified
- All operations are read-only on source
- New JSON is a complete, independent copy

### Version Consistency
- All version strings must follow `vMAJOR-MINOR` format
- Version replacement is global across all id/name fields
- Old version completely replaced by new version

### Content Fidelity
- Markdown content copied with **version strings updated**
- Old version replaced with new version inside markdown
- Preserve all other whitespace and special characters
- Common version patterns replaced: `vX-Y`, `vX.Y`, `X.Y.Z`

### Validation First
- Always validate inputs before processing
- Verify file counts match
- Confirm version changes with user before proceeding

## Context

$ARGUMENTS
