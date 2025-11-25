#!/usr/bin/env python3
"""
md2aps.py - Extrae estructuras semánticas de prompt.md a agent.apS.yaml
"""

import argparse
import os
import sys
import yaml
import re

def parse_markdown_agent(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    sections = {'role': '', 'goals': '', 'constraints': '', 'tools': ''}
    # Flexible extraction: look for keywords and headers
    lines = content.splitlines()
    buf = ''
    current = None
    keywords = {
        'role': ['rol', 'role', 'objetivo', 'propósito'],
        'goals': ['objetivo', 'goals', 'meta', 'finalidad'],
        'constraints': ['restricciones', 'constraints', 'limitaciones', 'política'],
        'tools': ['herramientas', 'tools', 'variables disponibles']
    }
    for i, line in enumerate(lines):
        header = re.match(r'^(#+)\s*(.*)', line)
        if header:
            htxt = header.group(2).strip().lower()
            for k, kwlist in keywords.items():
                if any(kw in htxt for kw in kwlist):
                    if current and buf:
                        sections[current] += buf.strip() + '\n'
                    current = k
                    buf = ''
                    break
        elif current:
            buf += line + '\n'
    if current and buf:
        sections[current] += buf.strip() + '\n'
    # Fallback: if no headers, try to extract by searching for keywords in text
    if not any(sections.values()):
        text = content.lower()
        for k, kwlist in keywords.items():
            for kw in kwlist:
                idx = text.find(kw)
                if idx != -1:
                    # Take 10 lines after keyword
                    start = max(0, text[:idx].count('\n'))
                    chunk = '\n'.join(lines[start:start+10])
                    sections[k] = chunk
                    break
    # Clean up
    for k in sections:
        sections[k] = sections[k].strip()
    return sections

def agent_to_yaml(sections, agent_name):
    return {
        'name': agent_name,
        'role': sections.get('role', ''),
        'goals': sections.get('goals', ''),
        'constraints': sections.get('constraints', ''),
        'tools': sections.get('tools', '')
    }

def main():
    parser = argparse.ArgumentParser(description='Extract APS YAML from agent Markdown.')
    parser.add_argument('input', help='Path to agent markdown file or directory')
    parser.add_argument('--outdir', help='Output directory for YAML files', default=None)
    parser.add_argument('--strict', action='store_true', help='Fail on missing sections')
    args = parser.parse_args()


    if os.path.isdir(args.input):
        files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.endswith('.md') and os.path.isfile(os.path.join(args.input, f))]
    else:
        files = [args.input]

    for md_path in files:
        agent_name = os.path.splitext(os.path.basename(md_path))[0]
        try:
            sections = parse_markdown_agent(md_path)
            if args.strict and any(not sections.get(k) for k in ['role','goals','constraints']):
                print(f"ERROR: Missing required section in {md_path}", file=sys.stderr)
                continue
            agent_yaml = agent_to_yaml(sections, agent_name)
            yaml_str = yaml.dump(agent_yaml, sort_keys=False, allow_unicode=True)
            if args.outdir:
                os.makedirs(args.outdir, exist_ok=True)
                out_path = os.path.join(args.outdir, f'{agent_name}.aps.yaml')
                with open(out_path, 'w', encoding='utf-8') as out:
                    out.write(yaml_str)
                print(f"Generated {out_path}")
            else:
                print(f"# {agent_name}.aps.yaml\n{yaml_str}")
        except Exception as e:
            print(f"ERROR processing {md_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
