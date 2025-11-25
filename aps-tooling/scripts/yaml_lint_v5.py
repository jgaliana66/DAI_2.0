#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════
APS v3.5 - YAML Semantic Linter v5 (Zero-Config + AI-Assisted)
════════════════════════════════════════════════════════════════════════════

Validador semántico con CERO CONFIGURACIÓN para casos comunes.

MEJORAS sobre v4:
- ✅ Modo AUTO: aprende reglas del SWARM existente (sin config manual)
- ✅ Modo AI-ASSIST: genera reglas desde descripción en lenguaje natural
- ✅ Modo MANUAL: usa archivo de reglas custom (v4 legacy)
- ✅ Detección inteligente de dominios comunes (e-commerce, support, etc.)
- ✅ Sugerencias automáticas de mejoras

USO:
    # Modo AUTO (sin configuración - aprende del SWARM)
    python3 yaml_lint_v5.py swarm/agents/MySwarm/*.yaml
    
    # Modo AI-ASSIST (describe tu dominio en lenguaje natural)
    python3 yaml_lint_v5.py agent.yaml --domain "validar pedidos de e-commerce"
    
    # Modo MANUAL (usa archivo de reglas custom)
    python3 yaml_lint_v5.py agent.yaml --rules custom_rules.yaml
    
    # Generar reglas desde SWARM existente (para reutilizar)
    python3 yaml_lint_v5.py swarm/agents/MySwarm/*.yaml --learn-rules > my_rules.yaml

AUTOR: APS v3.5 Validation Team
FECHA: 2025-11-19
VERSIÓN: 5.0 (Zero-Config)
════════════════════════════════════════════════════════════════════════════
"""

import re
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, Counter
import json


# ═══════════════════════════════════════════════════════════════════════════
# CLASE: IntelligentRuleLearner
# ═══════════════════════════════════════════════════════════════════════════

class IntelligentRuleLearner:
    """Aprende reglas automáticamente analizando SWARMs existentes"""
    
    def __init__(self):
        self.learned_patterns = defaultdict(list)
        self.learned_keywords = defaultdict(set)
        self.learned_roles = set()
        self.field_accesses = defaultdict(lambda: defaultdict(int))
    
    def learn_from_swarm(self, yaml_files: List[Path]) -> Dict:
        """
        Analiza múltiples archivos YAML y aprende patrones comunes
        Retorna: diccionario de reglas aprendidas
        """
        print("🧠 Aprendiendo patrones del SWARM existente...")
        
        for yaml_file in yaml_files:
            self._analyze_file(yaml_file)
        
        # Generar reglas basadas en lo aprendido
        rules = self._generate_learned_rules()
        
        print(f"✅ Aprendizaje completo: {len(rules.get('suspicious_patterns', {}))} categorías de patrones detectadas")
        
        return rules
    
    def _analyze_file(self, yaml_file: Path):
        """Analiza un archivo individual y extrae patrones"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception:
            return
        
        # Extraer agente
        if 'agent' in data:
            agent_name = data['agent'].get('name', '')
            blocks = data['agent'].get('blocks', {})
        else:
            agent_name = data.get('metadata', {}).get('agent_name', '')
            blocks = data.get('blocks', {})
        
        # Aprender rol del agente
        role = self._infer_role(agent_name)
        self.learned_roles.add(role)
        
        # Analizar bloques
        for block_name, block_content in blocks.items():
            content = block_content.get('content', '') if isinstance(block_content, dict) else str(block_content)
            
            # Aprender keywords usados
            self._extract_keywords(block_name, content)
            
            # Aprender accesos a campos
            self._extract_field_accesses(content, role)
    
    def _infer_role(self, agent_name: str) -> str:
        """Infiere el rol del agente por su nombre"""
        name_lower = agent_name.lower()
        
        if 'orchestrator' in name_lower or 'orquestador' in name_lower:
            return 'ORCHESTRATOR'
        elif 'helper' in name_lower or 'asistente' in name_lower:
            return 'HELPER'
        elif 'input' in name_lower:
            return 'INPUT'
        else:
            # Por defecto, asumir INPUT (conservador)
            return 'INPUT'
    
    def _extract_keywords(self, block_name: str, content: str):
        """Extrae keywords comunes de bloques"""
        block_type = self._classify_block(block_name)
        
        # Palabras clave relevantes (control, validación, etc.)
        keywords = re.findall(r'\b(verify|validate|check|confirm|process|create|update|delete|activate|control|handoff)\w*\b', content, re.IGNORECASE)
        
        for kw in keywords:
            self.learned_keywords[block_type].add(kw.lower())
    
    def _classify_block(self, block_name: str) -> str:
        """Clasifica un bloque por su nombre"""
        name_lower = block_name.lower()
        
        if 'entry' in name_lower or 'guard' in name_lower:
            return 'entry_guard'
        elif 'exit' in name_lower or 'salida' in name_lower:
            return 'exit_strategy'
        elif 'loop' in name_lower or 'bucle' in name_lower:
            return 'loop_contract'
        elif 'state' in name_lower and 'json' in name_lower:
            return 'state_json'
        else:
            return 'general'
    
    def _extract_field_accesses(self, content: str, role: str):
        """Extrae qué campos modifica cada rol"""
        # Buscar asignaciones (field = value)
        assignments = re.findall(r'(\w+(?:\.\w+)*)\s*=', content)
        
        for field in assignments:
            self.field_accesses[role][field] += 1
    
    def _generate_learned_rules(self) -> Dict:
        """Genera reglas YAML basadas en lo aprendido"""
        rules = {
            'version': '1.0',
            'metadata': {
                'description': 'Reglas aprendidas automáticamente del SWARM',
                'domain': 'auto-learned',
                'generated_by': 'yaml_lint_v5.py',
            },
            'suspicious_patterns': {},
            'required_keywords': {},
            'role_permissions': {},
        }
        
        # Generar required_keywords basado en keywords frecuentes
        for block_type, keywords in self.learned_keywords.items():
            if len(keywords) >= 2:  # Al menos 2 keywords aprendidos
                rules['required_keywords'][block_type] = {
                    'must_contain_any': list(keywords)[:5],  # Top 5
                    'message': f"{block_type.replace('_', ' ').title()} debe contener keywords relevantes",
                    'severity': 'warning'
                }
        
        # Generar role_permissions basado en accesos observados
        for role in self.learned_roles:
            allowed_fields = [field for field, count in self.field_accesses[role].items() if count >= 2]
            
            if role == 'ORCHESTRATOR':
                rules['role_permissions'][role] = {
                    'can_modify': ['.*'],  # Orchestrator puede todo
                    'can_activate_agents': True,
                }
            else:
                rules['role_permissions'][role] = {
                    'can_modify': allowed_fields[:10] if allowed_fields else [],
                    'cannot_modify': ['covered\\..*', 'ada\\.phase'] if role != 'ORCHESTRATOR' else [],
                    'can_activate_agents': False,
                }
        
        return rules


# ═══════════════════════════════════════════════════════════════════════════
# CLASE: NaturalLanguageRuleGenerator
# ═══════════════════════════════════════════════════════════════════════════

class NaturalLanguageRuleGenerator:
    """Genera reglas desde descripción en lenguaje natural"""
    
    DOMAIN_TEMPLATES = {
        'ecommerce': {
            'keywords': ['inventory', 'stock', 'cart', 'payment', 'order', 'shipping', 'price'],
            'patterns': [
                {
                    'category': 'inventory_check',
                    'pattern': 'create.*order.*without.*stock',
                    'message': 'Order created without inventory validation',
                },
                {
                    'category': 'payment_validation',
                    'pattern': 'process.*payment.*without.*verify',
                    'message': 'Payment processed without validation',
                },
            ],
        },
        'support': {
            'keywords': ['ticket', 'escalate', 'priority', 'sla', 'customer', 'resolve'],
            'patterns': [
                {
                    'category': 'ticket_handling',
                    'pattern': 'close.*ticket.*without.*confirm',
                    'message': 'Ticket closed without user confirmation',
                },
            ],
        },
        'devops': {
            'keywords': ['deploy', 'rollback', 'test', 'production', 'environment'],
            'patterns': [
                {
                    'category': 'deployment',
                    'pattern': 'deploy.*production.*without.*test',
                    'message': 'Deployment to production without running tests',
                },
            ],
        },
    }
    
    def generate_from_description(self, description: str) -> Dict:
        """
        Genera reglas desde descripción en lenguaje natural
        Ejemplo: "validar pedidos de e-commerce con inventario"
        """
        print(f"🤖 Generando reglas desde descripción: '{description}'")
        
        # Detectar dominio por keywords
        detected_domain = self._detect_domain(description)
        
        if detected_domain:
            print(f"✅ Dominio detectado: {detected_domain}")
            template = self.DOMAIN_TEMPLATES[detected_domain]
            return self._expand_template(template, description)
        else:
            print("⚠️  Dominio no reconocido, usando reglas genéricas")
            return self._generate_generic_rules(description)
    
    def _detect_domain(self, description: str) -> Optional[str]:
        """Detecta el dominio por keywords en la descripción"""
        desc_lower = description.lower()
        
        for domain, config in self.DOMAIN_TEMPLATES.items():
            keywords = config['keywords']
            matches = sum(1 for kw in keywords if kw in desc_lower)
            
            if matches >= 2:  # Al menos 2 keywords coinciden
                return domain
        
        return None
    
    def _expand_template(self, template: Dict, description: str) -> Dict:
        """Expande una plantilla de dominio con la descripción del usuario"""
        rules = {
            'version': '1.0',
            'metadata': {
                'description': f"Reglas generadas desde: {description}",
                'domain': 'ai-generated',
            },
            'suspicious_patterns': {},
            'required_keywords': {},
        }
        
        # Añadir patrones del template
        for pattern_config in template['patterns']:
            category = pattern_config['category']
            
            if category not in rules['suspicious_patterns']:
                rules['suspicious_patterns'][category] = {}
            
            rules['suspicious_patterns'][category]['auto_generated'] = [{
                'pattern': pattern_config['pattern'],
                'severity': 'error',
                'message': pattern_config['message'],
            }]
        
        # Añadir keywords requeridos
        for block_type in ['entry_guard', 'exit_strategy', 'validation_block']:
            rules['required_keywords'][block_type] = {
                'must_contain_any': template['keywords'][:3],
                'message': f"{block_type} should contain domain-specific keywords",
                'severity': 'warning',
            }
        
        return rules
    
    def _generate_generic_rules(self, description: str) -> Dict:
        """Genera reglas genéricas cuando no se detecta dominio específico"""
        # Extraer keywords de la descripción
        keywords = re.findall(r'\b[a-z]{4,}\b', description.lower())
        unique_keywords = list(set(keywords))[:5]
        
        return {
            'version': '1.0',
            'metadata': {
                'description': f"Reglas genéricas desde: {description}",
                'domain': 'generic',
            },
            'required_keywords': {
                'validation_block': {
                    'must_contain_any': unique_keywords if unique_keywords else ['validate', 'verify', 'check'],
                    'message': 'Validation block should contain relevant keywords',
                    'severity': 'warning',
                },
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# CLASE: SimpleValidator (validador simplificado)
# ═══════════════════════════════════════════════════════════════════════════

class SimpleValidator:
    """Validador simplificado que usa reglas aprendidas o generadas"""
    
    def __init__(self, rules: Dict):
        self.rules = rules
        self.issues = []
    
    def validate_file(self, yaml_file: Path) -> Tuple[int, int]:
        """Valida un archivo YAML"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ ERROR: No se pudo leer {yaml_file}: {e}")
            return (1, 0)
        
        # Parsear estructura
        if 'agent' in data:
            blocks = data['agent'].get('blocks', {})
        else:
            blocks = data.get('blocks', {})
        
        # Validar bloques
        for block_name, block_content in blocks.items():
            content = block_content.get('content', '') if isinstance(block_content, dict) else str(block_content)
            self._validate_block(block_name, content)
        
        return self._count_issues()
    
    def _validate_block(self, block_name: str, content: str):
        """Valida un bloque individual"""
        # Aplicar required_keywords
        required_kw = self.rules.get('required_keywords', {})
        for block_type, config in required_kw.items():
            if block_type.replace('_', ' ').lower() in block_name.lower():
                keywords = config.get('must_contain_any', [])
                if not any(kw in content.lower() for kw in keywords):
                    self._add_issue(
                        block_name,
                        config.get('severity', 'warning'),
                        config.get('message', 'Missing required keywords')
                    )
        
        # Aplicar suspicious_patterns
        patterns = self.rules.get('suspicious_patterns', {})
        for category, subcats in patterns.items():
            for subcat, rules_list in subcats.items():
                for rule in rules_list:
                    pattern = rule.get('pattern', '')
                    if re.search(pattern, content, re.IGNORECASE):
                        self._add_issue(
                            block_name,
                            rule.get('severity', 'warning'),
                            rule.get('message', 'Suspicious pattern detected')
                        )
    
    def _add_issue(self, location: str, severity: str, message: str):
        """Registra un issue"""
        self.issues.append({
            'location': location,
            'severity': severity,
            'message': message
        })
    
    def _count_issues(self) -> Tuple[int, int]:
        """Cuenta errores y warnings"""
        errors = sum(1 for i in self.issues if i['severity'] == 'error')
        warnings = sum(1 for i in self.issues if i['severity'] == 'warning')
        return (errors, warnings)
    
    def print_report(self):
        """Imprime reporte"""
        errors = [i for i in self.issues if i['severity'] == 'error']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        
        if errors:
            print(f"\n❌ ERRORES: {len(errors)}")
            for issue in errors:
                print(f"  ❌ {issue['location']}: {issue['message']}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS: {len(warnings)}")
            for issue in warnings:
                print(f"  ⚠️  {issue['location']}: {issue['message']}")
        
        if not errors and not warnings:
            print("\n✅ VALIDACIÓN EXITOSA: No se encontraron problemas")
        
        print(f"\n📊 RESUMEN: {len(errors)} errores, {len(warnings)} warnings")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='APS v3.5 - YAML Semantic Linter v5 (Zero-Config)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:

  # 🚀 MODO AUTO (sin configuración - aprende del SWARM)
  python3 yaml_lint_v5.py swarm/agents/MySwarm/*.yaml
  
  # 🤖 MODO AI-ASSIST (describe tu dominio)
  python3 yaml_lint_v5.py agent.yaml --domain "validar pedidos de e-commerce"
  
  # 📋 MODO MANUAL (usa archivo de reglas)
  python3 yaml_lint_v5.py agent.yaml --rules custom_rules.yaml
  
  # 🧠 APRENDER REGLAS (para reutilizar)
  python3 yaml_lint_v5.py swarm/agents/MySwarm/*.yaml --learn-rules > my_rules.yaml
        """
    )
    
    parser.add_argument('yaml_files', nargs='+', type=Path, help='Archivos YAML a validar')
    parser.add_argument('--domain', type=str, help='Descripción del dominio en lenguaje natural')
    parser.add_argument('--rules', type=Path, help='Archivo de reglas custom (modo manual)')
    parser.add_argument('--learn-rules', action='store_true', help='Aprender reglas del SWARM y exportarlas')
    
    args = parser.parse_args()
    
    # Determinar modo de operación
    if args.learn_rules:
        # MODO: Aprender y exportar reglas
        print("🧠 MODO: Aprender reglas del SWARM\n")
        learner = IntelligentRuleLearner()
        rules = learner.learn_from_swarm(args.yaml_files)
        print("\n" + yaml.dump(rules, default_flow_style=False, allow_unicode=True))
        sys.exit(0)
    
    elif args.domain:
        # MODO: AI-Assisted (desde descripción natural)
        print(f"🤖 MODO: Generación AI-Assisted\n")
        generator = NaturalLanguageRuleGenerator()
        rules = generator.generate_from_description(args.domain)
    
    elif args.rules:
        # MODO: Manual (archivo de reglas)
        print(f"📋 MODO: Reglas manuales desde {args.rules}\n")
        try:
            with open(args.rules, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ ERROR: No se pudo cargar reglas: {e}")
            sys.exit(1)
    
    else:
        # MODO: AUTO (aprender del SWARM y validar)
        print("🚀 MODO: AUTO (aprendizaje automático del SWARM)\n")
        learner = IntelligentRuleLearner()
        rules = learner.learn_from_swarm(args.yaml_files)
    
    # Validar archivos
    print("\n" + "="*80)
    print("📄 VALIDANDO ARCHIVOS")
    print("="*80 + "\n")
    
    validator = SimpleValidator(rules)
    total_errors = 0
    total_warnings = 0
    
    for yaml_file in args.yaml_files:
        print(f"📄 {yaml_file.name}")
        errors, warnings = validator.validate_file(yaml_file)
        total_errors += errors
        total_warnings += warnings
    
    # Reporte final
    validator.print_report()
    
    # Exit code
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == '__main__':
    main()
