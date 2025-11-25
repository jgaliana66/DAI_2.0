#!/usr/bin/env python3
"""
APS v3.5 YAML Linter v3 - Con validación semántica
Detecta defectos estructurales Y semánticos en agentes SWARM
"""

import yaml
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Patrones sospechosos que indican defectos semánticos
SUSPICIOUS_PATTERNS = {
    'entry_guard': {
        'always_active': [
            r'SIEMPRE\s+activarse',
            r'sin\s+importar\s+active_agent',
            r'activarse\s+también.*CONTRADICCIÓN',
            r'activarse\s+siempre',
        ],
        'missing_logic': [
            r'\(No\s+hay\s+Entry\s+Guard',
            r'\(ausente\)',
            r'Entry\s+Guard\s+ausente',
            r'Sin\s+Entry\s+Guard',
        ],
        'required_keywords': [
            r'active_agent',
            r'control\.',
        ]
    },
    'exit_strategy': {
        'no_return_control': [
            r'NO\s+cambia\s+active_agent',
            r'NO\s+devuelve.*control',
            r'Orchestrator\s+queda\s+esperando',
            r'no\s+devolver\s+control',
        ],
        'contradictory': [
            r'CONTRADICCIÓN',
            r'contradictoria',
            r'¿Cuál\s+prevalece',
            r'¿Cuál\s+usar',
        ],
        'missing': [
            r'\(No\s+hay.*salida',
            r'Exit\s+Strategy\s+ausente',
            r'\(ausente\)',
        ],
        'required_keywords': [
            r'control\.active_agent',
            r'devolver.*control',
            r'Orchestrator',
            r'handoff',
        ]
    },
    'loop_contract': {
        'infinite_loop': [
            r'while\s+True',
            r'while\s+not.*:\s*$',  # while sin break visible
            r'nunca\s+termina',
            r'sin.*salida',
            r'sin.*escape',
        ],
        'no_exit_condition': [
            r'Loop\s+sin\s+condición\s+de\s+salida',
            r'sin\s+detección\s+de\s+intención',
            r'sin\s+menú\s+de\s+opciones',
        ],
        'missing': [
            r'Loop\s+Contract\s+ausente',
            r'\(Falta\s+definición',
        ],
        'required_keywords': [
            r'confirmar|continuar|listo',
            r'añadir\s+más',
            r'sugerencias',
        ]
    },
    'state_json': {
        'forbidden_fields': [
            r'"motivaciones"',
            r'"stakeholders"',
            r'"asis"',
            r'"riesgos"',
            r'"gaps"',
            r'"requisitos"',
            r'custom_field',
        ],
        'inconsistent_structure': [
            r'Estructura\s+inconsistente',
            r'dos\s+ejemplos\s+diferentes',
        ],
        'missing_required': [
            r'Falta\s+meta\.',
            r'sin\s+meta\s+completo',
        ]
    },
    'mvc_violations': {
        'input_modifies_covered': [
            r'covered\.\w+\s*=\s*True',
            r'STATE_JSON\.covered\.',
            r'Marcar\s+covered\.',
        ],
        'input_changes_phase': [
            r'ada\.phase\s*=',
            r'Cambiar\s+ada\.phase',
        ],
        'input_activates_agents': [
            r'control\.active_agent\s*=\s*["\'][^O]',  # No Orchestrator
            r'Activar\s+siguiente\s+agente',
            r'activa\s+otros\s+agentes',
        ]
    },
    'heuristics': {
        'contradictory': [
            r'≥\s*(\d+).*≥\s*(\d+)',  # Dos números diferentes
            r'Al\s+menos\s+(\d+).*≥\s*(\d+)',
        ]
    }
}

# ============================================================================
# FUNCIONES DE VALIDACIÓN SEMÁNTICA
# ============================================================================

def check_suspicious_patterns(content: str, pattern_category: str, block_name: str) -> List[Dict[str, str]]:
    """Busca patrones sospechosos en el contenido de un bloque"""
    issues = []
    
    if pattern_category not in SUSPICIOUS_PATTERNS:
        return issues
    
    patterns = SUSPICIOUS_PATTERNS[pattern_category]
    
    for issue_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                issues.append({
                    'type': 'SEMANTIC_WARNING',
                    'category': pattern_category,
                    'issue': issue_type,
                    'block': block_name,
                    'pattern': pattern,
                    'message': f"Patrón sospechoso '{issue_type}' detectado"
                })
    
    return issues

def validate_entry_guard_logic(block_name: str, content: str) -> List[Dict[str, str]]:
    """Valida lógica del Entry Guard"""
    issues = []
    
    # Buscar patrones sospechosos
    issues.extend(check_suspicious_patterns(content, 'entry_guard', block_name))
    
    # Verificar keywords requeridos
    has_active_agent = bool(re.search(r'active_agent', content, re.IGNORECASE))
    has_control = bool(re.search(r'control\.', content, re.IGNORECASE))
    
    if not (has_active_agent or has_control):
        issues.append({
            'type': 'SEMANTIC_ERROR',
            'category': 'entry_guard',
            'issue': 'missing_keywords',
            'block': block_name,
            'message': "Entry Guard no menciona 'active_agent' ni 'control'"
        })
    
    return issues

def validate_exit_strategy_logic(block_name: str, content: str) -> List[Dict[str, str]]:
    """Valida que Exit Strategy devuelve control correctamente"""
    issues = []
    
    # Buscar patrones sospechosos
    issues.extend(check_suspicious_patterns(content, 'exit_strategy', block_name))
    
    # Verificar keywords de devolución de control
    has_return_control = bool(re.search(
        r'control\.active_agent.*Orchestrator|devolver.*control|handoff',
        content,
        re.IGNORECASE
    ))
    
    if not has_return_control:
        issues.append({
            'type': 'SEMANTIC_WARNING',
            'category': 'exit_strategy',
            'issue': 'no_explicit_return',
            'block': block_name,
            'message': "Exit Strategy no menciona explícitamente devolución de control a Orchestrator"
        })
    
    return issues

def validate_loop_contract_logic(block_name: str, content: str) -> List[Dict[str, str]]:
    """Valida Loop Contract tiene condiciones de salida"""
    issues = []
    
    # Buscar patrones sospechosos
    issues.extend(check_suspicious_patterns(content, 'loop_contract', block_name))
    
    # Verificar menciones de confirmación/continuar
    has_exit_keywords = bool(re.search(
        r'confirmar|continuar|listo|añadir\s+más|sugerencias',
        content,
        re.IGNORECASE
    ))
    
    if not has_exit_keywords:
        issues.append({
            'type': 'SEMANTIC_WARNING',
            'category': 'loop_contract',
            'issue': 'no_exit_mechanism',
            'block': block_name,
            'message': "Loop Contract no describe mecanismo de salida (confirmar/continuar/listo)"
        })
    
    return issues

def validate_state_json_content(block_name: str, content: str) -> List[Dict[str, str]]:
    """Valida que STATE_JSON no incluye datos de proyecto"""
    issues = []
    
    # Buscar campos prohibidos
    issues.extend(check_suspicious_patterns(content, 'state_json', block_name))
    
    # Buscar estructura JSON dentro del contenido
    json_blocks = re.findall(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    
    for json_block in json_blocks:
        # Verificar campos prohibidos
        forbidden = ['motivaciones', 'stakeholders', 'asis', 'riesgos', 'gaps', 'requisitos']
        for field in forbidden:
            if f'"{field}"' in json_block:
                issues.append({
                    'type': 'SEMANTIC_ERROR',
                    'category': 'state_json',
                    'issue': 'forbidden_field',
                    'block': block_name,
                    'message': f"STATE_JSON incluye campo prohibido '{field}' (solo control, no datos)"
                })
    
    return issues

def detect_mvc_violations(block_name: str, content: str, agent_role: str) -> List[Dict[str, str]]:
    """Detecta violaciones del patrón MVC Controller"""
    issues = []
    
    if agent_role == 'ORCHESTRATOR':
        return issues  # Orchestrator puede hacer todo
    
    # INPUT agents y HELPERS no pueden modificar covered.*
    if re.search(r'covered\.\w+\s*=\s*True', content, re.IGNORECASE):
        issues.append({
            'type': 'SEMANTIC_ERROR',
            'category': 'mvc_violation',
            'issue': 'input_modifies_covered',
            'block': block_name,
            'message': f"Agente {agent_role} modifica 'covered.*' (solo Orchestrator puede)"
        })
    
    # INPUT agents no pueden cambiar ada.phase
    if agent_role in ['INPUT', 'HELPER'] and re.search(r'ada\.phase\s*=', content):
        issues.append({
            'type': 'SEMANTIC_ERROR',
            'category': 'mvc_violation',
            'issue': 'changes_phase',
            'block': block_name,
            'message': f"Agente {agent_role} cambia 'ada.phase' (solo Orchestrator puede)"
        })
    
    return issues

def check_duplicate_sections(blocks: Dict[str, Any]) -> List[Dict[str, str]]:
    """Detecta secciones duplicadas semánticamente (no solo por nombre)"""
    issues = []
    
    # Buscar bloques con contenido muy similar
    block_list = list(blocks.items())
    
    for i, (name1, block1) in enumerate(block_list):
        content1 = block1.get('content', '').lower()[:200]
        
        for name2, block2 in block_list[i+1:]:
            content2 = block2.get('content', '').lower()[:200]
            
            # Similitud básica (podría mejorarse con difflib)
            if content1 and content2 and len(content1) > 50:
                common_words = set(content1.split()) & set(content2.split())
                similarity = len(common_words) / max(len(set(content1.split())), len(set(content2.split())))
                
                if similarity > 0.7:  # 70% de palabras comunes
                    issues.append({
                        'type': 'SEMANTIC_WARNING',
                        'category': 'duplicate',
                        'issue': 'semantic_duplicate',
                        'block': f"{name1} / {name2}",
                        'message': f"Bloques semánticamente duplicados ({similarity*100:.0f}% similares)"
                    })
    
    return issues

# ============================================================================
# LÓGICA PRINCIPAL (heredada de yaml_lint_v2.py)
# ============================================================================

def load_rules(rules_path: Path) -> Dict:
    """Carga reglas de validación desde YAML"""
    with open(rules_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate_structure(data: Dict, rules: Dict) -> List[Dict[str, str]]:
    """Valida estructura básica del YAML"""
    errors = []
    
    if 'agent' not in data:
        errors.append({'type': 'ERROR', 'message': "Falta clave raíz 'agent'"})
        return errors
    
    agent = data['agent']
    
    if 'blocks' not in agent:
        errors.append({'type': 'ERROR', 'message': "Falta 'agent.blocks'"})
        return errors
    
    if not isinstance(agent['blocks'], dict):
        errors.append({'type': 'ERROR', 'message': "'agent.blocks' debe ser Dict, no List"})
    
    return errors

def validate_required_blocks(blocks: Dict[str, Any], rules: Dict, agent_name: str) -> List[Dict[str, str]]:
    """Valida presencia de bloques obligatorios"""
    errors = []
    
    # Detectar si es Greeter (exento de Entry Guard)
    is_greeter = 'greeter' in agent_name.lower()
    
    for req_block in rules.get('required_blocks', []):
        block_name = req_block['name']
        patterns = req_block['patterns']
        required_in = req_block.get('required_in', ['all'])
        
        # Excepción para Greeter
        if block_name == 'Entry Guard' and is_greeter and 'agents_except_greeter' in required_in:
            continue
        
        # Buscar bloque por nombre o contenido
        found = False
        for name, block in blocks.items():
            content = block.get('content', '')
            
            # Buscar en nombre del bloque
            if any(re.search(p, name, re.IGNORECASE) for p in patterns):
                found = True
                break
            
            # Buscar en contenido
            if any(re.search(p, content, re.IGNORECASE) for p in patterns):
                found = True
                break
        
        if not found:
            errors.append({
                'type': 'ERROR',
                'category': 'missing_block',
                'message': f"Bloque obligatorio ausente: '{block_name}'"
            })
    
    return errors

def validate_agent_semantic(agent_name: str, blocks: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validación semántica completa de un agente"""
    issues = []
    
    # Determinar rol del agente
    agent_role = 'ORCHESTRATOR' if 'orchestrator' in agent_name.lower() else 'INPUT'
    if 'helper' in agent_name.lower() or 'aggregator' in agent_name.lower():
        agent_role = 'HELPER'
    
    for block_name, block in blocks.items():
        content = block.get('content', '')
        block_type = block.get('block_type', 'BLK')
        
        # Validar Entry Guard
        if 'entry' in block_name.lower() or 'guard' in block_name.lower():
            issues.extend(validate_entry_guard_logic(block_name, content))
        
        # Validar Exit Strategy
        if 'exit' in block_name.lower() or 'salida' in block_name.lower():
            issues.extend(validate_exit_strategy_logic(block_name, content))
        
        # Validar Loop Contract
        if 'loop' in block_name.lower() or 'contract' in block_name.lower():
            issues.extend(validate_loop_contract_logic(block_name, content))
        
        # Validar State JSON
        if 'state' in block_name.lower() and 'json' in block_name.lower():
            issues.extend(validate_state_json_content(block_name, content))
        
        # Validar violaciones MVC
        issues.extend(detect_mvc_violations(block_name, content, agent_role))
    
    # Buscar duplicados semánticos
    issues.extend(check_duplicate_sections(blocks))
    
    return issues

def main():
    if len(sys.argv) < 2:
        print("Uso: python yaml_lint_v3.py <archivo.yaml>")
        sys.exit(1)
    
    yaml_path = Path(sys.argv[1])
    rules_path = Path(__file__).parent.parent / 'schemas' / 'aps_v3.5_rules.yaml'
    
    if not yaml_path.exists():
        print(f"❌ ERROR: Archivo no encontrado: {yaml_path}")
        sys.exit(1)
    
    if not rules_path.exists():
        print(f"⚠️  WARNING: Reglas no encontradas: {rules_path}")
        rules = {}
    else:
        rules = load_rules(rules_path)
    
    # Cargar YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print(f"\n🔍 Validando: {yaml_path.name}")
    print("=" * 80)
    
    # Validación estructural
    structural_errors = validate_structure(data, rules)
    
    if structural_errors:
        print("\n❌ ERRORES ESTRUCTURALES:")
        for error in structural_errors:
            print(f"  ❌ {error['message']}")
        sys.exit(1)
    
    # Validación de bloques requeridos
    agent = data['agent']
    blocks = agent['blocks']
    agent_name = agent.get('name', yaml_path.stem)
    
    required_errors = validate_required_blocks(blocks, rules, agent_name)
    
    # Validación semántica (NUEVO)
    semantic_issues = validate_agent_semantic(agent_name, blocks)
    
    # Clasificar issues
    errors = [i for i in semantic_issues if i['type'] == 'SEMANTIC_ERROR'] + required_errors
    warnings = [i for i in semantic_issues if i['type'] == 'SEMANTIC_WARNING']
    
    # Mostrar resultados
    if errors:
        print("\n❌ ERRORES:")
        for error in errors:
            msg = error.get('message', 'Error desconocido')
            block = error.get('block', '')
            if block:
                print(f"  ❌ ERROR en '{block}': {msg}")
            else:
                print(f"  ❌ ERROR: {msg}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            msg = warning.get('message', 'Warning desconocido')
            block = warning.get('block', '')
            print(f"  ⚠️  WARNING en '{block}': {msg}")
    
    print("\n" + "=" * 80)
    print(f"📊 RESUMEN: {len(errors)} errores, {len(warnings)} warnings")
    print("=" * 80)
    
    if errors:
        sys.exit(1)
    elif warnings:
        sys.exit(0)  # Warnings no fallan el build
    else:
        print("✅ Validación exitosa")
        sys.exit(0)

if __name__ == '__main__':
    main()
