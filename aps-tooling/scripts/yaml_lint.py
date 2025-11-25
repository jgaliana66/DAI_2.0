#!/usr/bin/env python3
"""
Linter para archivos YAML de agentes SWARM.
Valida estructura, SIDs, bloques obligatorios, atributos semánticos y deny-terms.

Uso:
    python3 yaml_lint.py <archivo.yaml>
    python3 yaml_lint.py --batch swarm/agents/*.yaml
"""

import yaml
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter

# Bloques obligatorios (por nombre o patrón en content)
REQUIRED_BLOCKS = {
    'entry_guard': {
        'patterns': [
            r'active_agent.*≠',
            r'if.*active_agent.*!=',
            r'si.*active_agent',
        ],
        'description': 'Entry Guard (verificar active_agent)'
    },
    'no_salto_automatico': {
        'patterns': [
            r'nunca.*devuelvo control',
            r'no.*salto.*automático',
            r'no-salto',
        ],
        'description': 'Política NO-SALTO-AUTOMÁTICO'
    },
    'state_json_protocol': {
        'patterns': [
            r'state_json',
            r'fusionar.*state_json',
            r'generar.*state_json',
        ],
        'description': 'Protocolo STATE_JSON'
    },
    'loop_contract': {
        'patterns': [
            r'loop.*contract',
            r'iteración.*continua',
            r'detección.*intención',
        ],
        'description': 'Loop Contract (iteración continua)'
    }
}

# Términos prohibidos (anti-patterns)
# Se detectan en content de bloques, con excepciones contextuales
DENY_TERMS = [
    r'cumpl[oí].*heur[ií]stica.*devuelv',  # "cumplo/cumplí heurística...devuelvo/devuelve"
    r'handoff.*autom[áa]tic',
    r'(?<!no\s)promoci[oó]n.*autom[áa]tic',
    r'salto.*autom[áa]tic.*heur[ií]stica',
]

# Patrones de negación que indican antipatrón descriptivo (no ERROR)
NEGATION_PATTERNS = [
    r'(?i)no\s+(hacer|hagas|hacer|realiz|ejecut)',  # "NO hacer handoff automático"
    r'(?i)nunca\s+',                                  # "NUNCA devuelvo control automático"
    r'(?i)prohibid[oa]\s+',                          # "Prohibido handoff automático"
    r'(?i)evitar\s+',                                # "Evitar salto automático"
    r'(?i)❌\s*',                                     # "❌ handoff automático"
    r'(?i)\[antipatr[oó]n\]',                       # "[ANTIPATRÓN] handoff automático"
    r'(?i)\[ejemplo\s+incorrecto\]',                # "[EJEMPLO INCORRECTO]"
    r'(?i)antes:\s*',                                # "Antes: handoff automático"
    r'(?i)mal:\s*',                                  # "Mal: devuelvo tras heurística"
]

# Block types válidos (incluyendo tipos especiales exentos de DENY_TERMS)
VALID_BLOCK_TYPES = ['BLK', 'INS', 'OUT', 'VAR', 'GOAL', 'CONST', 'REQ', 'EXAMPLE', 'ANTIPATTERN']

# Block types exentos de validación DENY_TERMS (ejemplos y antipatrones descriptivos)
DENY_TERMS_EXEMPT_TYPES = ['EXAMPLE', 'ANTIPATTERN']

# Atributos semánticos obligatorios
REQUIRED_ATTRIBUTES = ['block_type', 'accion', 'relacion', 'nivel', 'sid', 'content']

# Agentes exceptuados de bloques obligatorios (one-shot, helpers, disabled)
EXEMPT_AGENTS = [
    'J2Ci-Orchestrator',           # One-shot MVC coordinator
    'J2Ci-Documentation_Aggregator',  # One-shot consolidator
    'J2Ci-Methodology_Assurance',   # Internal validator (DISABLED)
    'J2Ci-Question_Suggester',      # Helper non-iterativo
    'J2Ci-Greeter',                 # One-shot welcome/LSRG
]


class LintError:
    def __init__(self, severity: str, block: str, code: str, message: str):
        self.severity = severity  # ERROR, WARNING, INFO
        self.block = block
        self.code = code
        self.message = message
    
    def __str__(self):
        return f"  {self.severity} [{self.code}] {self.block}: {self.message}"


def lint_yaml_file(yaml_path: Path) -> Tuple[List[LintError], Dict]:
    """
    Valida un archivo YAML de agente.
    Retorna (errores, stats)
    """
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [LintError('ERROR', 'FILE', 'YAML_INVALID', f"YAML inválido: {e}")], {}
    except Exception as e:
        return [LintError('ERROR', 'FILE', 'READ_ERROR', f"Error leyendo archivo: {e}")], {}
    
    errors = []
    
    # 1. Validar estructura básica
    if 'agent' not in data:
        errors.append(LintError('ERROR', 'ROOT', 'MISSING_AGENT', "Falta clave 'agent' en raíz"))
        return errors, {}
    
    agent = data['agent']
    
    if 'name' not in agent:
        errors.append(LintError('ERROR', 'agent', 'MISSING_NAME', "Falta 'agent.name'"))
    
    if 'blocks' not in agent:
        errors.append(LintError('ERROR', 'agent', 'MISSING_BLOCKS', "Falta 'agent.blocks'"))
        return errors, {}
    
    blocks = agent['blocks']
    
    if not isinstance(blocks, dict):
        errors.append(LintError('ERROR', 'blocks', 'INVALID_TYPE', "'blocks' debe ser un diccionario"))
        return errors, {}
    
    # 2. Validar bloques individuales
    sids_found = []
    block_types_count = Counter()
    required_blocks_found = {key: False for key in REQUIRED_BLOCKS.keys()}
    
    for block_name, block_data in blocks.items():
        if not isinstance(block_data, dict):
            errors.append(LintError('WARNING', block_name, 'BLOCK_INVALID', "Bloque no es un diccionario"))
            continue
        
        # 2.1 Validar atributos obligatorios
        missing_attrs = []
        for attr in REQUIRED_ATTRIBUTES:
            if attr not in block_data:
                missing_attrs.append(attr)
        
        if missing_attrs:
            errors.append(LintError(
                'ERROR', block_name, 'MISSING_ATTRS',
                f"Faltan atributos: {', '.join(missing_attrs)}"
            ))
        
        # 2.2 Validar block_type
        block_type = block_data.get('block_type', '')
        if block_type not in VALID_BLOCK_TYPES:
            errors.append(LintError(
                'WARNING', block_name, 'INVALID_BLOCK_TYPE',
                f"block_type '{block_type}' no está en tipos válidos: {VALID_BLOCK_TYPES}"
            ))
        
        block_types_count[block_type] += 1
        
        # 2.3 Validar SID
        sid = block_data.get('sid', '')
        if sid:
            sids_found.append(sid)
            
            # Validar formato SID: <block_type>.<accion>.<relacion>.<nivel>
            # Acepta tanto 4 partes como 5+ partes (para relaciones compuestas)
            sid_parts = sid.split('.')
            if len(sid_parts) < 4:
                errors.append(LintError(
                    'WARNING', block_name, 'SID_FORMAT',
                    f"SID mal formado: '{sid}' (esperado al menos 4 partes: <type>.<accion>.<relacion>.<nivel>)"
                ))
            elif sid_parts[0] != block_type:
                errors.append(LintError(
                    'WARNING', block_name, 'SID_MISMATCH',
                    f"SID '{sid}' no coincide con block_type '{block_type}'"
                ))
        else:
            errors.append(LintError('ERROR', block_name, 'MISSING_SID', "Falta atributo 'sid'"))
        
        # 2.4 Validar content (deny-terms con contexto)
        content = str(block_data.get('content', ''))
        content_lower = content.lower()
        
        # Eximir bloques EXAMPLE y ANTIPATTERN de validación DENY_TERMS
        if block_type not in DENY_TERMS_EXEMPT_TYPES:
            for deny_pattern in DENY_TERMS:
                if re.search(deny_pattern, content_lower, re.IGNORECASE):
                    # Verificar si está en contexto de negación/antipatrón
                    is_negation_context = False
                    for negation_pattern in NEGATION_PATTERNS:
                        if re.search(negation_pattern, content, re.IGNORECASE | re.MULTILINE):
                            is_negation_context = True
                            break
                    
                    if is_negation_context:
                        # Contexto de antipatrón descriptivo → WARNING en lugar de ERROR
                        errors.append(LintError(
                            'WARNING', block_name, 'DENY_TERM_CONTEXT',
                            f"Término prohibido en contexto de negación/antipatrón: '{deny_pattern[:30]}...' "
                            f"(Verificar que es descriptivo y no prescriptivo)"
                        ))
                    else:
                        # Uso directo del antipatrón → ERROR
                        errors.append(LintError(
                            'ERROR', block_name, 'DENY_TERM',
                            f"Término prohibido detectado: patrón '{deny_pattern[:30]}...'"
                        ))
        else:
            # Bloque EXAMPLE/ANTIPATTERN → solo INFO
            errors.append(LintError(
                'INFO', block_name, 'EXEMPT_DENY_TERMS',
                f"Bloque tipo '{block_type}' exento de validación DENY_TERMS (ejemplo/antipatrón descriptivo)"
            ))
        
        # 2.5 Detectar bloques obligatorios
        for req_key, req_config in REQUIRED_BLOCKS.items():
            for pattern in req_config['patterns']:
                if re.search(pattern, content, re.IGNORECASE):
                    required_blocks_found[req_key] = True
                    break
    
    # 3. Validar unicidad de SIDs
    sid_counts = Counter(sids_found)
    for sid, count in sid_counts.items():
        if count > 1:
            errors.append(LintError(
                'ERROR', 'GLOBAL', 'SID_DUPLICATE',
                f"SID duplicado '{sid}' aparece {count} veces"
            ))
    
    # 3.5 Detectar bloques auto-numerados (duplicados en .md fuente)
    for block_name in blocks.keys():
        if re.search(r' \(\d+\)$', block_name):
            original_name = re.sub(r' \(\d+\)$', '', block_name)
            errors.append(LintError(
                'ERROR', block_name, 'AUTO_NUMBERED_BLOCK',
                f"Bloque duplicado en .md fuente: '{original_name}' → eliminar duplicados en archivo .md"
            ))
    
    # 5. Estadísticas
    stats = {
        'total_blocks': len(blocks),
        'sids_count': len(sids_found),
        'unique_sids': len(set(sids_found)),
        'block_types': dict(block_types_count),
        'required_blocks': sum(required_blocks_found.values()),
        'errors': len([e for e in errors if e.severity == 'ERROR']),
        'warnings': len([e for e in errors if e.severity == 'WARNING']),
        'info': len([e for e in errors if e.severity == 'INFO']),
    }
    
    return errors, stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Linter para YAMLs de agentes SWARM')
    parser.add_argument('files', nargs='+', help='Archivos .yaml a validar')
    parser.add_argument('--batch', action='store_true', help='Procesar múltiples archivos')
    parser.add_argument('--strict', action='store_true', help='Tratar warnings como errores')
    
    args = parser.parse_args()
    
    if args.batch:
        import glob
        pattern = args.files[0] if args.files else 'swarm/agents/*.yaml'
        files = glob.glob(pattern)
        files = [Path(f) for f in files if f.endswith('.yaml')]
    else:
        files = [Path(f) for f in args.files]
    
    print(f"🔍 Validando {len(files)} archivos YAML...\n")
    
    total_errors = 0
    total_warnings = 0
    failed_files = []
    
    for f in files:
        if not f.exists():
            print(f"⚠️  {f}: no existe")
            continue
        
        errors, stats = lint_yaml_file(f)
        
        if errors:
            print(f"{'❌' if stats.get('errors', 0) > 0 else '⚠️'} {f.name}:")
            for error in errors:
                print(error)
            print(f"   Stats: {stats['total_blocks']} bloques, {stats['sids_count']} SIDs, "
                  f"{stats['required_blocks']}/4 bloques obligatorios")
            print(f"   Errores: {stats['errors']}, Warnings: {stats['warnings']}\n")
            
            total_errors += stats['errors']
            total_warnings += stats['warnings']
            
            if stats['errors'] > 0 or (args.strict and stats['warnings'] > 0):
                failed_files.append(f.name)
        else:
            print(f"✅ {f.name}: OK ({stats['total_blocks']} bloques, {stats['sids_count']} SIDs)")
    
    print(f"\n{'='*60}")
    print(f"Total: {total_errors} errores, {total_warnings} warnings")
    
    if failed_files:
        print(f"❌ FAIL: {len(failed_files)} archivos con problemas:")
        for fname in failed_files:
            print(f"   - {fname}")
        sys.exit(1)
    else:
        print(f"✅ PASS: Todos los archivos válidos")
        sys.exit(0)


if __name__ == '__main__':
    main()
