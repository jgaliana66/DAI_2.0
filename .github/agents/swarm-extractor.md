---
description: Extract and organize agents from SwarmBuilder JSON files into structured folder with individual markdown files
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Process a SwarmBuilder JSON file to:
1. Detect the JSON file from context (open file, attached file, or specified path)
2. Create a working folder based on the file name: `swarm/agents/{base_name}/`
3. Copy the original JSON to the new folder (keeping the original in place)
4. Extract each individual agent's goal into separate Markdown files with format: `{XX}-{agent_name}.md`

## Operating Constraints

- **Always validate** the JSON file exists and has the expected `"agents"` structure
- **Use 2-digit numbering** for order (01, 02, 03...)
- **Preserve goal content** exactly as it appears in the JSON
- **Ask for confirmation** if the target folder already exists
- **Provide a summary** of all files created after completion

## Input Detection

Automatically detect the JSON file from:
- Currently open file in the editor
- Attached files in the conversation  
- Files referenced by path in user's message

If no JSON file is detected, ask the user to provide the file path.

## Execution Steps

### 1. Validate Input

- Verify that the JSON file exists and is accessible
- Verify that the file has a `.json` extension
- Read and validate that the JSON contains the expected structure (`"agents"` field)
- If validation fails, report error and stop

### 2. Create Folder Structure

- Extract base name from file (without extension or path)
- Create folder: `swarm/agents/{base_name}/`
- If folder already exists, ask user if they want to overwrite or cancel

### 3. Copy JSON to New Folder

- Copy the JSON file to `swarm/agents/{base_name}/{file_name}.json`
- Keep the original file in its original location
- Confirm that the copy was successful

### 4. Extract Individual Goals

For each agent in the agents array (with index i):

- `order_number = i + 1` (format: 01, 02, 03, ...)
- `agent_name = agents[i].name`
- `goal_content = agents[i].goal`
- Create file: `swarm/agents/{base_name}/{order_number:02d}-{agent_name}.md`
- Write `goal_content` to the file exactly as it appears

### 5. Generate Summary

Display operation summary with:
- Folder created path
- JSON copied to location
- Original JSON location preserved
- Total agents extracted (count)
- List of all `.md` files created

## Output Format

### File Name Convention

```
{XX}-{agent_name}.md
```

Where:
- `XX`: Order number with 2 digits (01, 02, 03, ...)
- `agent_name`: Agent name as it appears in the JSON

### File Content

The exact content of the agent's `"goal"` field in the JSON, without modifications or additional formatting.

## Error Handling

- **JSON file not found**: Display error message and stop execution
- **Invalid JSON or missing "agents" field**: Display error message explaining expected structure and stop
- **Folder already exists**: Ask user for confirmation to overwrite (y/n)
  - If 'n': Stop execution
  - If 'y': Continue and overwrite files
- **Agent without name or goal**: Display warning and skip, continue with next agent

## Example Output

```
✓ Created folder: swarm/agents/J2C-v1-Swarm-v3-5/
✓ JSON copied to: swarm/agents/J2C-v1-Swarm-v3-5/J2C-v1-Swarm-v3-5.json
✓ Original preserved: swarm/json/J2C-v1-Swarm-v3-5.json

Extracted agents:
01-J2Ci-Orchestrator.md
02-J2Ci-Migration_Motives.md
03-J2Ci-Stakeholder_Map.md
04-J2Ci-ASIS_Context.md
05-J2Ci-Risks_Constraints.md
06-J2Ci-GAP_Analysis.md
07-J2Ci-Requirements_Facilitator.md
08-J2Ci-Documentation_Aggregator.md
09-J2Ci-Methodology_Assurance.md
10-J2Ci-Question_Suggester.md
11-J2Ci-Greeter.md

Total: 11 agents processed successfully
```

## Operating Principles

### Content Preservation
- Goal content MUST be copied exactly as it is in the JSON
- No modifications, formatting, or additions

### Consistent Naming
- Always use 2 digits for order number (01, 02, not 1, 2)
- Preserve agent names exactly as they appear in JSON

### Folder Structure
- Always use `swarm/agents/{base_name}/` as the base location
- Never create files outside this structure

### Prior Validation
- Never move or create files without first validating the JSON structure
- Stop immediately on any validation error

### User Confirmation
- Always ask for confirmation if existing content will be overwritten
- Never silently overwrite without user consent

## Context

$ARGUMENTS
