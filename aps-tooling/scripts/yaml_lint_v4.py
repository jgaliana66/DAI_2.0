#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════
APS v3.5 - YAML Semantic Linter v4 (Generic Rule-Based)
════════════════════════════════════════════════════════════════════════════

Validador semántico configurable mediante archivos de reglas YAML.

MEJORAS sobre v3:
- ✅ Reglas externalizadas en validation_rules_v1.yaml
- ✅ Soporte multi-dominio (generic, j2c, custom)
- ✅ Patrones configurables sin recompilar
- ✅ Fácil extensión para nuevos SWARMs
- ✅ Reportes customizables

USO:
    # Usar reglas por defecto (swarm/rules/validation_rules_v1.yaml)
    python3 yaml_lint_v4.py agent.yaml
    
    # Especificar archivo de reglas custom
    python3 yaml_lint_v4.py agent.yaml --rules custom_rules.yaml
    
    # Output formato JSON
    python3 yaml_lint_v4.py agent.yaml --format json

AUTOR: APS v3.5 Validation Team
FECHA: 2025-11-19
VERSIÓN: 4.0
════════════════════════════════════════════════════════════════════════════
"""

import re
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════════════════
# CLASE: ValidationRule
# ═══════════════════════════════════════════════════════════════════════════

class ValidationRule:
    """Representa una regla de validación cargada desde YAML"""
    
    def __init__(self, rule_id: str, config: Dict[str, Any]):
        self.rule_id = rule_id
        self.pattern = config.get('pattern', '')
        self.severity = config.get('severity', 'warning')
        self.message = config.get('message', 'Validation issue detected')
        self.compiled_pattern = re.compile(self.pattern, re.IGNORECASE) if self.pattern else None
    
    def matches(self, text: str) -> bool:
        """Retorna True si el patrón coincide con el texto"""
        if not self.compiled_pattern:
            return False
        return bool(self.compiled_pattern.search(text))
    
    def __repr__(self):
        return f"ValidationRule(id={self.rule_id}, severity={self.severity})"


# ═══════════════════════════════════════════════════════════════════════════
# CLASE: RuleEngine
# ═══════════════════════════════════════════════════════════════════════════

class RuleEngine:
    """Motor de reglas que carga y aplica validaciones desde archivo YAML"""
    
    def __init__(self, rules_file: Path):
        self.rules_file = rules_file
        self.config = self._load_rules()
        self.rules_by_category = self._parse_rules()
        self.role_permissions = self.config.get('role_permissions', {})
        self.required_keywords = self.config.get('required_keywords', {})
        self.structural_requirements = self.config.get('structural_requirements', {})
        self.semantic_validators = self.config.get('semantic_validators', {})
    
    def _load_rules(self) -> Dict:
        """Carga el archivo de reglas YAML"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ ERROR: Archivo de reglas no encontrado: {self.rules_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ ERROR: Formato YAML inválido en reglas: {e}")
            sys.exit(1)
    
    def _parse_rules(self) -> Dict[str, List[ValidationRule]]:
        """Convierte configuración YAML en objetos ValidationRule"""
        rules = defaultdict(list)
        
        suspicious = self.config.get('suspicious_patterns', {})
        for category, subcategories in suspicious.items():
            for subcat_name, rule_list in subcategories.items():
                for rule_config in rule_list:
                    rule_id = f"{category}.{subcat_name}"
                    rules[category].append(ValidationRule(rule_id, rule_config))
        
        return dict(rules)
    
    def get_rules_for_category(self, category: str) -> List[ValidationRule]:
        """Retorna reglas para una categoría específica"""
        return self.rules_by_category.get(category, [])
    
    def get_required_keywords(self, block_type: str) -> Dict:
        """Retorna keywords requeridos para un tipo de bloque"""
        return self.required_keywords.get(block_type, {})
    
    def get_role_permissions(self, role: str) -> Dict:
        """Retorna permisos para un rol específico"""
        return self.role_permissions.get(role, {})
    
    def get_duplicate_threshold(self) -> float:
        """Retorna threshold de similitud para duplicados"""
        dup_config = self.semantic_validators.get('duplicate_detection', {})
        return dup_config.get('similarity_threshold', 0.70)
    
    def get_forbidden_state_keys(self) -> List[str]:
        """Retorna claves prohibidas en STATE_JSON"""
        state_config = self.semantic_validators.get('state_json_schema', {})
        return state_config.get('forbidden_keys', [])


# ═══════════════════════════════════════════════════════════════════════════
# CLASE: SemanticValidator
# ═══════════════════════════════════════════════════════════════════════════

class SemanticValidator:
    """Validador semántico que usa RuleEngine para aplicar reglas"""
    
    def __init__(self, rule_engine: RuleEngine):
        self.rules = rule_engine
        self.issues = []
    
    def validate_file(self, yaml_file: Path) -> Tuple[int, int]:
        """
        Valida un archivo YAML de agente
        Retorna: (num_errors, num_warnings)
        """
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ ERROR: No se pudo leer {yaml_file}: {e}")
            return (1, 0)
        
        # Soportar estructura antigua (top-level metadata/blocks) y nueva (agent.name/blocks)
        if 'agent' in data:
            agent_name = data['agent'].get('name', yaml_file.stem)
            blocks = data['agent'].get('blocks', {})
        else:
            agent_name = data.get('metadata', {}).get('agent_name', yaml_file.stem)
            blocks = data.get('blocks', {})
        
        agent_role = self._determine_role(agent_name)
        
        # Validar cada bloque
        for block_name, block_content in blocks.items():
            # Soportar ambas estructuras: dict con 'content' o string directo
            if isinstance(block_content, dict):
                content = block_content.get('content', '')
            else:
                content = str(block_content)
            
            # 1. Validar Entry Guards
            if self._is_entry_guard(block_name):
                self._validate_entry_guard(block_name, content)
            
            # 2. Validar Exit Strategies
            if self._is_exit_strategy(block_name):
                self._validate_exit_strategy(block_name, content)
            
            # 3. Validar Loop Contracts
            if self._is_loop_contract(block_name):
                self._validate_loop_contract(block_name, content)
            
            # 4. Validar STATE_JSON
            if self._is_state_json(block_name):
                self._validate_state_json(block_name, content)
            
            # 5. Validar permisos MVC
            self._validate_mvc_permissions(block_name, content, agent_role)
        
        # 6. Validar duplicados semánticos
        self._validate_duplicate_blocks(blocks)
        
        return self._count_issues()
    
    def _determine_role(self, agent_name: str) -> str:
        """Determina el rol del agente basado en su nombre"""
        name_lower = agent_name.lower()
        
        if 'orchestrator' in name_lower or 'orquestador' in name_lower:
            return 'ORCHESTRATOR'
        elif 'helper' in name_lower or 'ayudante' in name_lower or 'asistente' in name_lower:
            return 'HELPER'
        else:
            return 'INPUT'
    
    def _is_entry_guard(self, block_name: str) -> bool:
        """Detecta si un bloque es Entry Guard"""
        name_lower = block_name.lower()
        return 'entry' in name_lower or 'guard' in name_lower or 'entrada' in name_lower
    
    def _is_exit_strategy(self, block_name: str) -> bool:
        """Detecta si un bloque es Exit Strategy"""
        name_lower = block_name.lower()
        return 'exit' in name_lower or 'salida' in name_lower or 'estrategia' in name_lower
    
    def _is_loop_contract(self, block_name: str) -> bool:
        """Detecta si un bloque es Loop Contract"""
        name_lower = block_name.lower()
        return 'loop' in name_lower or 'bucle' in name_lower or 'iteración' in name_lower
    
    def _is_state_json(self, block_name: str) -> bool:
        """Detecta si un bloque es STATE_JSON"""
        name_lower = block_name.lower()
        return ('state' in name_lower and 'json' in name_lower) or 'estado' in name_lower
    
    def _validate_entry_guard(self, block_name: str, content: str):
        """Valida lógica de Entry Guard usando reglas configuradas"""
        # Aplicar reglas de patrones sospechosos
        for rule in self.rules.get_rules_for_category('entry_guard'):
            if rule.matches(content):
                self._add_issue(block_name, rule.severity, rule.message)
        
        # Verificar keywords requeridos
        kw_config = self.rules.get_required_keywords('entry_guard')
        if kw_config:
            must_contain = kw_config.get('must_contain_any', [])
            if not any(re.search(kw, content, re.IGNORECASE) for kw in must_contain):
                self._add_issue(
                    block_name,
                    kw_config.get('severity', 'error'),
                    kw_config.get('message', 'Entry Guard missing required keywords')
                )
    
    def _validate_exit_strategy(self, block_name: str, content: str):
        """Valida lógica de Exit Strategy usando reglas configuradas"""
        # Aplicar reglas de patrones sospechosos
        for rule in self.rules.get_rules_for_category('exit_strategy'):
            if rule.matches(content):
                self._add_issue(block_name, rule.severity, rule.message)
        
        # Verificar keywords requeridos
        kw_config = self.rules.get_required_keywords('exit_strategy')
        if kw_config:
            must_contain = kw_config.get('must_contain_any', [])
            if not any(re.search(kw, content, re.IGNORECASE) for kw in must_contain):
                self._add_issue(
                    block_name,
                    kw_config.get('severity', 'error'),
                    kw_config.get('message', 'Exit Strategy missing required keywords')
                )
    
    def _validate_loop_contract(self, block_name: str, content: str):
        """Valida lógica de Loop Contract usando reglas configuradas"""
        # Aplicar reglas de patrones sospechosos
        for rule in self.rules.get_rules_for_category('loop_contract'):
            if rule.matches(content):
                self._add_issue(block_name, rule.severity, rule.message)
        
        # Verificar keywords requeridos
        kw_config = self.rules.get_required_keywords('loop_contract')
        if kw_config:
            must_contain = kw_config.get('must_contain_any', [])
            if not any(re.search(kw, content, re.IGNORECASE) for kw in must_contain):
                self._add_issue(
                    block_name,
                    kw_config.get('severity', 'warning'),
                    kw_config.get('message', 'Loop Contract missing exit mechanism')
                )
    
    def _validate_state_json(self, block_name: str, content: str):
        """Valida contenido de STATE_JSON usando reglas configuradas"""
        # Aplicar reglas de patrones sospechosos
        for rule in self.rules.get_rules_for_category('state_json'):
            if rule.matches(content):
                self._add_issue(block_name, rule.severity, rule.message)
        
        # Verificar claves prohibidas
        forbidden = self.rules.get_forbidden_state_keys()
        for key in forbidden:
            if re.search(rf'["\']?{key}["\']?\s*:', content, re.IGNORECASE):
                self._add_issue(
                    block_name,
                    'error',
                    f"STATE_JSON incluye campo prohibido '{key}' (solo debe contener control, no datos de proyecto)"
                )
    
    def _validate_mvc_permissions(self, block_name: str, content: str, agent_role: str):
        """Valida que el agente respeta permisos MVC según su rol"""
        permissions = self.rules.get_role_permissions(agent_role)
        if not permissions:
            return
        
        # Verificar modificaciones prohibidas
        cannot_modify = permissions.get('cannot_modify', [])
        for forbidden_pattern in cannot_modify:
            # Buscar asignaciones a campos prohibidos
            pattern = rf'{forbidden_pattern}\s*='
            if re.search(pattern, content):
                self._add_issue(
                    block_name,
                    'error',
                    f"Agente {agent_role} no puede modificar '{forbidden_pattern}' (violación MVC)"
                )
        
        # Verificar activación directa de agentes (solo Orchestrator)
        if not permissions.get('can_activate_agents', False):
            for rule in self.rules.get_rules_for_category('mvc_violations'):
                if 'direct_activation' in rule.rule_id and rule.matches(content):
                    self._add_issue(block_name, rule.severity, rule.message)
    
    def _validate_duplicate_blocks(self, blocks: Dict):
        """Detecta bloques con contenido muy similar (duplicados semánticos)"""
        if not self.rules.semantic_validators.get('duplicate_detection', {}).get('enabled', True):
            return
        
        threshold = self.rules.get_duplicate_threshold()
        block_items = list(blocks.items())
        
        for i, (name1, content1) in enumerate(block_items):
            text1 = content1.get('content', '')
            words1 = set(re.findall(r'\w+', text1.lower()))
            
            if len(words1) == 0:
                continue
            
            for name2, content2 in block_items[i+1:]:
                text2 = content2.get('content', '')
                words2 = set(re.findall(r'\w+', text2.lower()))
                
                if len(words2) == 0:
                    continue
                
                # Calcular similitud
                common = words1 & words2
                total = words1 | words2
                similarity = len(common) / len(total) if total else 0
                
                if similarity >= threshold:
                    self._add_issue(
                        f"{name1} vs {name2}",
                        'warning',
                        f"Bloques semánticamente duplicados ({similarity*100:.0f}% similitud)"
                    )
    
    def _add_issue(self, location: str, severity: str, message: str):
        """Registra un issue de validación"""
        self.issues.append({
            'location': location,
            'severity': severity,
            'message': message
        })
    
    def _count_issues(self) -> Tuple[int, int]:
        """Cuenta errores y warnings"""
        errors = sum(1 for issue in self.issues if issue['severity'] == 'error')
        warnings = sum(1 for issue in self.issues if issue['severity'] == 'warning')
        return (errors, warnings)
    
    def print_report(self):
        """Imprime reporte de validación"""
        errors = [i for i in self.issues if i['severity'] == 'error']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        
        if errors:
            print(f"\n❌ ERRORES: {len(errors)}")
            for issue in errors:
                print(f"  ❌ ERROR en '{issue['location']}': {issue['message']}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS: {len(warnings)}")
            for issue in warnings:
                print(f"  ⚠️  WARNING en '{issue['location']}': {issue['message']}")
        
        if not errors and not warnings:
            print("\n✅ VALIDACIÓN EXITOSA: No se encontraron problemas semánticos")
        
        print(f"\n📊 RESUMEN: {len(errors)} errores, {len(warnings)} warnings")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='APS v3.5 - YAML Semantic Linter v4 (Rule-Based)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Validar con reglas por defecto
  python3 yaml_lint_v4.py agent.yaml
  
  # Usar archivo de reglas custom
  python3 yaml_lint_v4.py agent.yaml --rules my_rules.yaml
  
  # Output JSON
  python3 yaml_lint_v4.py agent.yaml --format json
        """
    )
    
    parser.add_argument('yaml_file', type=Path, help='Archivo YAML del agente a validar')
    parser.add_argument(
        '--rules',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'swarm' / 'rules' / 'validation_rules_v1.yaml',
        help='Archivo de reglas de validación (default: swarm/rules/validation_rules_v1.yaml)'
    )
    parser.add_argument(
        '--format',
        choices=['detailed', 'summary', 'json'],
        default='detailed',
        help='Formato de salida del reporte'
    )
    
    args = parser.parse_args()
    
    # Validar archivo de entrada
    if not args.yaml_file.exists():
        print(f"❌ ERROR: Archivo no encontrado: {args.yaml_file}")
        sys.exit(1)
    
    # Cargar reglas
    rule_engine = RuleEngine(args.rules)
    print(f"📋 Reglas cargadas desde: {args.rules}")
    print(f"📄 Validando: {args.yaml_file}\n")
    
    # Validar
    validator = SemanticValidator(rule_engine)
    errors, warnings = validator.validate_file(args.yaml_file)
    
    # Reportar
    if args.format == 'json':
        import json
        print(json.dumps({
            'file': str(args.yaml_file),
            'errors': errors,
            'warnings': warnings,
            'issues': validator.issues
        }, indent=2))
    else:
        validator.print_report()
    
    # Exit code
    sys.exit(1 if errors > 0 else 0)


if __name__ == '__main__':
    main()
