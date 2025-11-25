#!/usr/bin/env python3
"""
Linter para archivos YAML de agentes SWARM (APS v3.5+).
Valida estructura, SIDs, bloques obligatorios y deny-terms.

⚠️ IMPORTANTE: Este linter lee las reglas desde swarm/schemas/aps_v3.5_rules.yaml
   NO codifica reglas hardcoded. Si actualizas APS, actualiza el schema.

Uso:
    python3 yaml_lint.py <archivo.yaml>
    python3 yaml_lint.py --batch swarm/agents/*.yaml
"""

import yaml
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter

# ============================================================================
# CARGA DE REGLAS DESDE SCHEMA CANÓNICO
# ============================================================================

def load_aps_rules(schema_path: str = "swarm/schemas/aps_v3.5_rules.yaml") -> Dict:
    """
    Carga reglas APS desde el schema canónico.
    
    Returns:
        Dict con todas las reglas: required_blocks, antipatterns, vocabulary, etc.
    
    Raises:
        FileNotFoundError: Si el schema no existe
        yaml.YAMLError: Si el schema está malformado
    """
    path = Path(schema_path)
    if not path.exists():
        print(f"⚠️ WARNING: Schema APS no encontrado en {schema_path}")
        print(f"   Usando reglas por defecto (legacy)")
        return get_legacy_rules()
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
            print(f"✅ Reglas APS v{rules.get('version', 'unknown')} cargadas desde {schema_path}")
            return rules
    except yaml.YAMLError as e:
        print(f"❌ ERROR: Schema APS malformado: {e}")
        print(f"   Usando reglas por defecto (legacy)")
        return get_legacy_rules()


def get_legacy_rules() -> Dict:
    """
    Reglas legacy (hardcoded) para backward compatibility.
    DEPRECATED: Migrar a aps_v3.5_rules.yaml
    """
    return {
        'version': '3.5-legacy',
        'required_blocks': [
            {
                'name': 'Entry Guard',
                'patterns': [r'active_agent.*≠', r'if.*active_agent.*!='],
                'required_in': ['all']
            },
            {
                'name': 'State JSON',
                'patterns': [r'state_json', r'fusionar.*state_json'],
                'required_in': ['all']
            }
        ],
        'antipatterns': {
            'NO_AUTO_HANDOFF': {
                'patterns': [r'handoff.*autom[áa]tic'],
                'severity': 'ERROR'
            }
        },
        'negation_patterns': {
            'patterns': [r'NO\s+', r'NUNCA\s+', r'❌']
        }
    }


# ============================================================================
# VALIDACIÓN DE ESTRUCTURA
# ============================================================================

def validate_structure(yaml_content: Dict, rules: Dict) -> List[str]:
    """
    Valida estructura básica del YAML.
    """
    errors = []
    
    # 1. Verificar estructura APS v3.5: agent.blocks
    if 'agent' not in yaml_content:
        errors.append("❌ ERROR: Falta clave 'agent' en YAML (estructura APS v3.5)")
        return errors
    
    agent = yaml_content['agent']
    if 'blocks' not in agent:
        errors.append("❌ ERROR: Falta clave 'agent.blocks' en YAML")
        return errors
    
    blocks = agent['blocks']
    if not isinstance(blocks, dict):
        errors.append("❌ ERROR: 'agent.blocks' debe ser un diccionario")
        return errors
    
    if len(blocks) == 0:
        errors.append("⚠️ WARNING: YAML sin bloques")
    
    return errors


def validate_sids(blocks: Dict[str, Dict], rules: Dict) -> List[str]:
    """
    Valida que todos los bloques tengan SID válido.
    """
    errors = []
    sid_pattern = re.compile(r'^(BLK|INS|OUT|VAR|GOAL|CONST|REQ)\.[a-z0-9_\.]+$')
    
    # Obtener patrón del schema si existe
    if 'structural_validations' in rules:
        custom_pattern = rules['structural_validations'].get('invalid_sid_format', {}).get('pattern')
        if custom_pattern:
            sid_pattern = re.compile(custom_pattern)
    
    for block_name, block in blocks.items():
        # 1. Verificar que exista 'sid'
        if 'sid' not in block:
            errors.append(f"❌ ERROR: Bloque '{block_name}' sin SID")
            continue
        
        sid = block['sid']
        
        # 2. Verificar formato
        if not sid_pattern.match(sid):
            errors.append(f"❌ ERROR: SID inválido en '{block_name}': {sid}")
    
    return errors


def detect_duplicate_blocks(blocks: Dict[str, Dict], rules: Dict) -> List[str]:
    """
    Detecta bloques duplicados y bloques auto-numerados.
    """
    warnings = []
    block_names = list(blocks.keys())
    
    # Contar duplicados (no debería haber en dict, pero check por si acaso)
    duplicates = [name for name, count in Counter(block_names).items() if count > 1]
    
    for dup in duplicates:
        warnings.append(f"⚠️ WARNING: Bloque duplicado: '{dup}'")
    
    # Detectar auto-numerados (ej: "Bloque (2)")
    auto_numbered = re.compile(r'^(.+)\s+\((\d+)\)$')
    for name in block_names:
        if auto_numbered.match(name):
            warnings.append(f"⚠️ WARNING: Bloque auto-numerado: '{name}' (detectado por md2yaml)")
    
    return warnings


def validate_required_blocks(blocks: Dict[str, Dict], rules: Dict) -> List[str]:
    """
    Valida que existan bloques obligatorios según APS.
    """
    errors = []
    
    required_blocks = rules.get('required_blocks', [])
    
    # Detectar si es agente greeter
    agent_name = ''
    for name, block in blocks.items():
        if 'greeter' in name.lower():
            agent_name = 'greeter'
            break
    
    for req_block in required_blocks:
        block_name = req_block['name']
        patterns = req_block['patterns']
        required_in = req_block.get('required_in', ['all'])
        
        # Si es 'all', siempre es obligatorio
        if 'all' not in required_in:
            # Si es greeter y el bloque requiere 'agents_except_greeter', skip
            if agent_name == 'greeter' and 'agents_except_greeter' in required_in:
                continue
            continue  # TODO: detectar otros tipos de agente
        
        # Buscar match en nombre o contenido del bloque
        found = False
        for name, block in blocks.items():
            # Buscar en nombre del bloque Y en contenido
            search_text = name + ' ' + str(block.get('content', ''))
            for pattern in patterns:
                if re.search(pattern, search_text, re.IGNORECASE):
                    found = True
                    break
            if found:
                break
        
        if not found:
            errors.append(f"❌ ERROR: Bloque obligatorio faltante: {block_name}")
            errors.append(f"   Debe incluir alguno de estos patterns: {patterns}")
    
    return errors


def validate_deny_terms(blocks: Dict[str, Dict], rules: Dict) -> List[str]:
    """
    Valida términos prohibidos (antipatrones) con detección contextual.
    """
    errors = []
    warnings = []
    
    antipatterns = rules.get('antipatterns', {})
    negation_patterns_config = rules.get('negation_patterns', {})
    negation_patterns = negation_patterns_config.get('patterns', [])
    exempt_types = rules.get('exempt_block_types', [])
    
    # Compilar patrones de negación
    negation_regexes = [re.compile(p, re.IGNORECASE) for p in negation_patterns]
    
    for block_name, block in blocks.items():
        block_type = block.get('block_type', '').upper()
        content = str(block.get('content', ''))
        
        # Verificar cada antipatrón
        for antipattern_name, config in antipatterns.items():
            patterns = config.get('patterns', [])
            severity = config.get('severity', 'ERROR')
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Detectar contexto
                    
                    # 1. ¿Está en bloque exento?
                    if block_type in exempt_types:
                        errors.append(f"ℹ️ INFO: Antipatrón '{antipattern_name}' detectado en bloque exento '{block_name}'")
                        continue
                    
                    # 2. ¿Hay negación en el contexto?
                    has_negation = any(neg_re.search(content) for neg_re in negation_regexes)
                    
                    if has_negation:
                        warnings.append(f"⚠️ WARNING: Posible antipatrón '{antipattern_name}' en contexto de negación: '{block_name}'")
                        warnings.append(f"   Revisar si describe un antipatrón (OK) o lo prescribe (ERROR)")
                    else:
                        # Uso prescriptivo → ERROR
                        errors.append(f"❌ ERROR: Antipatrón '{antipattern_name}' detectado en '{block_name}'")
                        errors.append(f"   Pattern: {pattern}")
                        rationale = config.get('rationale', '')
                        if rationale:
                            errors.append(f"   Razón: {rationale}")
    
    return errors + warnings


# ============================================================================
# ORQUESTACIÓN PRINCIPAL
# ============================================================================

def lint_yaml_file(yaml_path: str, rules: Dict) -> Tuple[int, int]:
    """
    Valida un archivo YAML contra las reglas APS.
    
    Returns:
        (error_count, warning_count)
    """
    path = Path(yaml_path)
    
    if not path.exists():
        print(f"❌ ERROR: Archivo no encontrado: {yaml_path}")
        return (1, 0)
    
    print(f"\n{'='*70}")
    print(f"🔍 Validando: {yaml_path}")
    print(f"{'='*70}")
    
    # Cargar YAML
    try:
        with open(path, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ ERROR: YAML malformado: {e}")
        return (1, 0)
    
    all_errors = []
    all_warnings = []
    
    # 1. Validar estructura
    all_errors.extend(validate_structure(yaml_content, rules))
    
    if 'agent' not in yaml_content or 'blocks' not in yaml_content['agent']:
        # Si no hay bloques, no podemos continuar
        print(f"\n❌ TOTAL ERRORES: {len(all_errors)}")
        return (len(all_errors), 0)
    
    blocks = yaml_content['agent']['blocks']
    
    # 2. Validar SIDs
    all_errors.extend(validate_sids(blocks, rules))
    
    # 3. Detectar duplicados
    all_warnings.extend(detect_duplicate_blocks(blocks, rules))
    
    # 4. Validar bloques obligatorios
    all_errors.extend(validate_required_blocks(blocks, rules))
    
    # 5. Validar deny-terms
    deny_results = validate_deny_terms(blocks, rules)
    for msg in deny_results:
        if msg.startswith('❌'):
            all_errors.append(msg)
        elif msg.startswith('⚠️'):
            all_warnings.append(msg)
        else:
            all_warnings.append(msg)  # INFO también como warning
    
    # Imprimir resultados
    print()
    if all_errors:
        print("❌ ERRORES:")
        for error in all_errors:
            print(f"  {error}")
    
    if all_warnings:
        print("\n⚠️ WARNINGS:")
        for warning in all_warnings:
            print(f"  {warning}")
    
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN: {len(all_errors)} errores, {len(all_warnings)} warnings")
    print(f"{'='*70}\n")
    
    return (len(all_errors), len(all_warnings))


def main():
    """Entry point."""
    if len(sys.argv) < 2:
        print("Uso: python3 yaml_lint.py <archivo.yaml>")
        print("     python3 yaml_lint.py --batch swarm/agents/*.yaml")
        sys.exit(1)
    
    # Cargar reglas APS
    rules = load_aps_rules()
    
    # Procesar archivos
    if sys.argv[1] == '--batch':
        files = sys.argv[2:]
        total_errors = 0
        total_warnings = 0
        
        for yaml_file in files:
            errors, warnings = lint_yaml_file(yaml_file, rules)
            total_errors += errors
            total_warnings += warnings
        
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN BATCH: {total_errors} errores, {total_warnings} warnings en {len(files)} archivos")
        print(f"{'='*70}\n")
        
        sys.exit(1 if total_errors > 0 else 0)
    else:
        yaml_file = sys.argv[1]
        errors, warnings = lint_yaml_file(yaml_file, rules)
        sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
