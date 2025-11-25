#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════
APS v3.5 - YAML Semantic Linter v6 (SID-Based Validation)
════════════════════════════════════════════════════════════════════════════

Validador semántico que usa SIDs para detectar problemas estructurales.

VALIDACIONES IMPLEMENTADAS:
1. ✅ SIDs duplicados
2. ✅ Contradicciones semánticas (acciones opuestas)
3. ✅ Bloques obligatorios faltantes
4. ✅ Desplazamientos (block_type vs SID type)
5. ✅ STATE_JSON inconsistente
6. ✅ Mapeos de fases ambiguos
7. ✅ DENY_TERMS por patrón de SID
8. ✅ Bloques con confianza baja

USO:
    python3 yaml_lint_v6_semantic.py archivo.yaml
    python3 yaml_lint_v6_semantic.py swarm/agents/**/*.yaml

AUTOR: APS v3.5 Validation Team
FECHA: 2025-11-19
VERSIÓN: 6.0 (SID-Based Semantic Validation)
════════════════════════════════════════════════════════════════════════════
"""

import re
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class SemanticValidator:
    """Validador semántico basado en análisis de SIDs"""
    
    def __init__(self):
        self.issues = []
    
    def validate_file(self, yaml_path: Path) -> Tuple[int, int]:
        """Valida un archivo YAML y retorna (errores, warnings)"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self._add_issue('FILE', 'error', f"Error leyendo archivo: {e}")
            return self._count_issues()
        
        # Extraer bloques
        if 'agent' in data:
            blocks = data['agent'].get('blocks', {})
        else:
            blocks = data.get('blocks', {})
        
        # Ejecutar validaciones semánticas
        self._validate_sid_uniqueness(blocks)
        self._validate_semantic_contradictions(blocks)
        self._validate_required_blocks(blocks)
        self._validate_sid_block_type_alignment(blocks)
        self._validate_state_json_consistency(blocks)
        self._validate_phase_mappings(blocks)
        self._validate_deny_terms_by_sid(blocks)
        self._validate_confidence_levels(blocks)
        
        return self._count_issues()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 1: SIDs Duplicados
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_sid_uniqueness(self, blocks: Dict):
        """Detecta SIDs duplicados en el mismo archivo"""
        sid_usage = {}
        
        for block_name, block_data in blocks.items():
            if not isinstance(block_data, dict):
                continue
                
            sid = block_data.get('sid', '')
            if sid and not sid.startswith('TEMP_'):
                if sid in sid_usage:
                    self._add_issue(
                        f"{block_name} vs {sid_usage[sid]}",
                        'error',
                        f"SID duplicado: '{sid}'"
                    )
                else:
                    sid_usage[sid] = block_name
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 2: Contradicciones Semánticas
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_semantic_contradictions(self, blocks: Dict):
        """Detecta acciones opuestas sobre la misma relación"""
        OPPOSITE_ACTIONS = {
            'mostrar': 'ocultar',
            'activar': 'desactivar',
            'permitir': 'prohibir',
            'ejecutar': 'omitir',
            'incluir': 'excluir',
            'habilitar': 'deshabilitar',
            'crear': 'eliminar'
        }
        
        sids_by_relation = defaultdict(list)
        
        for block_name, block_data in blocks.items():
            if not isinstance(block_data, dict):
                continue
                
            sid = block_data.get('sid', '')
            if sid and '.' in sid:
                parts = sid.split('.')
                if len(parts) >= 4:
                    accion = parts[1]
                    relacion = '.'.join(parts[2:-1]) if len(parts) > 4 else parts[2]
                    sids_by_relation[relacion].append({
                        'block': block_name,
                        'accion': accion,
                        'sid': sid
                    })
        
        # Buscar contradicciones
        for relacion, sid_list in sids_by_relation.items():
            acciones = [item['accion'] for item in sid_list]
            
            for accion1, accion2 in OPPOSITE_ACTIONS.items():
                if accion1 in acciones and accion2 in acciones:
                    blocks_involved = [
                        item['block'] for item in sid_list 
                        if item['accion'] in [accion1, accion2]
                    ]
                    self._add_issue(
                        f"{blocks_involved[0]} vs {blocks_involved[1]}",
                        'error',
                        f"Contradicción: '{accion1}' vs '{accion2}' sobre '{relacion}'"
                    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 3: Bloques Obligatorios Faltantes
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_required_blocks(self, blocks: Dict):
        """Detecta bloques obligatorios faltantes por patrón de SID"""
        REQUIRED_SID_PATTERNS = {
            'Entry Guard': r'^BLK\.verificar\.(control\.active_agent|entrada)\.guard$',
            'Exit Strategy': r'^(BLK|GOAL)\.(detectar|definir|ejecutar)\.(salida|exit|terminacion|output)',
            'State JSON Protocol': r'^(PROT|BLK)\.(generar|validar|ejecutar)\..*state'
        }
        
        all_sids = [
            b.get('sid', '') for b in blocks.values() 
            if isinstance(b, dict)
        ]
        
        for block_name, pattern in REQUIRED_SID_PATTERNS.items():
            found = any(re.search(pattern, sid, re.IGNORECASE) for sid in all_sids)
            
            if not found:
                self._add_issue(
                    'GLOBAL',
                    'warning',
                    f"Bloque '{block_name}' no encontrado (patrón: {pattern})"
                )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 4: Desplazamientos (block_type vs SID type)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_sid_block_type_alignment(self, blocks: Dict):
        """Verifica que el TYPE del SID coincida con block_type"""
        for block_name, block_data in blocks.items():
            if not isinstance(block_data, dict):
                continue
                
            block_type = block_data.get('block_type', '')
            sid = block_data.get('sid', '')
            
            if sid and block_type and '.' in sid:
                sid_type = sid.split('.')[0]
                
                # Validar coincidencia para tipos conocidos
                known_types = ['BLK', 'GOAL', 'CST', 'POL', 'PROT', 'OUT', 'INP']
                if block_type in known_types and sid_type != block_type:
                    self._add_issue(
                        block_name,
                        'warning',
                        f"Desplazamiento: block_type='{block_type}' pero SID='{sid_type}.*'"
                    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 5: STATE_JSON Inconsistente
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_state_json_consistency(self, blocks: Dict):
        """Detecta ejemplos de STATE_JSON con estructuras diferentes"""
        json_structures = []
        
        for block_name, block_data in blocks.items():
            if not isinstance(block_data, dict):
                continue
                
            content = block_data.get('content', '')
            
            # Buscar bloques JSON en código
            json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            
            for json_str in json_blocks:
                try:
                    parsed = json.loads(json_str)
                    structure = set(parsed.keys())
                    json_structures.append({
                        'block': block_name,
                        'keys': structure
                    })
                except:
                    pass
        
        # Comparar estructuras
        if len(json_structures) > 1:
            first_keys = json_structures[0]['keys']
            for item in json_structures[1:]:
                if item['keys'] != first_keys:
                    self._add_issue(
                        f"{json_structures[0]['block']} vs {item['block']}",
                        'warning',
                        f"STATE_JSON inconsistente: {first_keys} ≠ {item['keys']}"
                    )
                    break
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 6: Mapeos de Fases Ambiguos
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_phase_mappings(self, blocks: Dict):
        """Detecta múltiples agentes asignados a la misma fase"""
        for block_name, block_data in blocks.items():
            if not isinstance(block_data, dict):
                continue
                
            content = block_data.get('content', '')
            
            # Buscar tablas de mapeo fase→agente
            table_rows = re.findall(r'\|\s*(\w+)\s*\|\s*([\w-]+)\s*\|', content)
            
            phase_agents = defaultdict(list)
            headers = ['fase', 'phase', 'agente', 'agent', 'flag']
            
            for phase, agent in table_rows:
                if phase.lower() not in headers:
                    phase_agents[phase].append(agent)
            
            # Detectar ambigüedad
            for phase, agents in phase_agents.items():
                unique_agents = set(agents)
                if len(agents) > 1 and len(unique_agents) > 1:
                    self._add_issue(
                        block_name,
                        'warning',
                        f"Fase '{phase}' mapeada a {len(unique_agents)} agentes: {list(unique_agents)}"
                    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 7: DENY_TERMS por SID
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_deny_terms_by_sid(self, blocks: Dict):
        """Detecta antipatrones usando patrones de SID y contenido"""
        DENY_PATTERNS_SID = [
            (r'\.automatico\.handoff', 'Handoff automático sin confirmación'),
            (r'\.omitir\.validacion', 'Omitir validación'),
            (r'\.skip\.(entrada|guard)', 'Saltar Entry Guard'),
            (r'\.bypass\.', 'Bypass de validaciones')
        ]
        
        DENY_PATTERNS_TEXT = [
            (r'(?i)(avanzar|saltar|delegar).*autom[aá]ticamente', 'Salto automático sin confirmación'),
            (r'(?i)sin.*preguntar.*usuario', 'Acción sin confirmación del usuario'),
            (r'(?i)marcar.*covered.*avanzar.*fase', 'Handoff automático detectado')
        ]
        
        for block_name, block_data in blocks.items():
            if not isinstance(block_data, dict):
                continue
                
            sid = block_data.get('sid', '')
            content = block_data.get('content', '')
            
            # Validar SID
            for pattern, message in DENY_PATTERNS_SID:
                if re.search(pattern, sid, re.IGNORECASE):
                    self._add_issue(
                        block_name,
                        'error',
                        f"DENY_TERM (SID): {message}"
                    )
            
            # Validar contenido
            for pattern, message in DENY_PATTERNS_TEXT:
                if re.search(pattern, content):
                    self._add_issue(
                        block_name,
                        'error',
                        f"DENY_TERM (contenido): {message}"
                    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDACIÓN 8: Bloques con Confianza Baja
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_confidence_levels(self, blocks: Dict):
        """Alerta sobre muchos bloques con confianza baja"""
        low_confidence = []
        
        for block_name, block_data in blocks.items():
            if not isinstance(block_data, dict):
                continue
                
            confidence = block_data.get('confidence', 'MEDIUM')
            if confidence == 'LOW':
                low_confidence.append(block_name)
        
        if len(low_confidence) > 3:
            self._add_issue(
                'GLOBAL',
                'info',
                f"{len(low_confidence)} bloques LOW confidence: {', '.join(low_confidence[:3])}..."
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Utilidades
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _add_issue(self, location: str, severity: str, message: str):
        """Registra un problema detectado"""
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
    
    def save_report(self, output_path: Path, validated_files: List[Path]):
        """Guarda el reporte en formato Markdown"""
        from datetime import datetime
        
        errors = [i for i in self.issues if i['severity'] == 'error']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        infos = [i for i in self.issues if i['severity'] == 'info']
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Reporte de Validación Semántica APS v3.5\n\n")
            f.write(f"**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Archivos validados**: {len(validated_files)}\n\n")
            
            for vf in validated_files:
                f.write(f"- `{vf}`\n")
            
            f.write("\n---\n\n")
            
            # Resumen
            f.write("## 📊 Resumen Ejecutivo\n\n")
            f.write(f"- ❌ **Errores críticos**: {len(errors)}\n")
            f.write(f"- ⚠️  **Warnings**: {len(warnings)}\n")
            f.write(f"- ℹ️  **Información**: {len(infos)}\n\n")
            
            if len(errors) > 0:
                f.write("**Estado**: 🚫 VALIDACIÓN FALLIDA - Bloquea integración\n\n")
                f.write("**Próximo paso**: Corregir errores críticos en archivos `.md` fuente\n\n")
            elif len(warnings) > 0:
                f.write("**Estado**: ⚠️  VALIDACIÓN CON WARNINGS - Requiere revisión\n\n")
                f.write("**Próximo paso**: Revisar warnings antes de integrar\n\n")
            else:
                f.write("**Estado**: ✅ LISTO PARA INTEGRACIÓN\n\n")
            
            f.write("---\n\n")
            
            # Errores detallados
            if errors:
                f.write("## ❌ Errores Críticos\n\n")
                for idx, issue in enumerate(errors, 1):
                    f.write(f"### {idx}. {issue['location']}\n\n")
                    f.write(f"**Problema**: {issue['message']}\n\n")
                    
                    # Recomendaciones
                    if 'SID duplicado' in issue['message']:
                        f.write("**Acción recomendada**: Consolidar bloques duplicados o renombrar SID único\n\n")
                        f.write("**Documentación**: `APS/LINTER_RULES.md § 1.3` (Unicidad de SIDs)\n\n")
                    elif 'Contradicción' in issue['message']:
                        f.write("**Acción recomendada**: Decidir política única y eliminar instrucción contradictoria\n\n")
                        f.write("**Documentación**: `METODOLOGIA § 2` (Problema operativo - Contradicciones)\n\n")
                    elif 'DENY_TERM' in issue['message']:
                        f.write("**Acción recomendada**: Añadir validación de confirmación de usuario\n\n")
                        f.write("**Documentación**: `APS/LINTER_RULES.md § 2.1` (DENY_TERMS)\n\n")
                    
                    f.write("---\n\n")
            
            # Warnings
            if warnings:
                f.write("## ⚠️  Warnings\n\n")
                for idx, issue in enumerate(warnings, 1):
                    f.write(f"### {idx}. {issue['location']}\n\n")
                    f.write(f"**Problema**: {issue['message']}\n\n")
                    
                    if 'no encontrado' in issue['message']:
                        if 'Entry Guard' in issue['message']:
                            f.write("**Acción recomendada**: Añadir bloque de validación de entrada\n\n")
                            f.write("**Template SID**: `BLK.verificar.control.active_agent.guard`\n\n")
                        elif 'Exit Strategy' in issue['message']:
                            f.write("**Acción recomendada**: Definir condiciones de terminación\n\n")
                            f.write("**Template SID**: `BLK.detectar.salida.protocol`\n\n")
                        elif 'State JSON' in issue['message']:
                            f.write("**Acción recomendada**: Añadir protocolo STATE_JSON\n\n")
                            f.write("**Template SID**: `PROT.generar.state_json.template`\n\n")
                    elif 'inconsistente' in issue['message']:
                        f.write("**Acción recomendada**: Unificar estructura de STATE_JSON\n\n")
                        f.write("**Documentación**: `APS § 11` (Protocolo STATE_JSON)\n\n")
                    elif 'mapeada a' in issue['message']:
                        f.write("**Acción recomendada**: Asignar cada fase a un solo agente\n\n")
                    
                    f.write("---\n\n")
            
            # Info
            if infos:
                f.write("## ℹ️  Información\n\n")
                for issue in infos:
                    f.write(f"- {issue['message']}\n")
                    if 'LOW confidence' in issue['message']:
                        f.write("  - **Acción**: Revisar bloques y enriquecer con vocabulario APS\n")
                        f.write("  - **Ver**: `aps-tooling/schemas/sid_vocabulary_v1.yaml`\n")
                f.write("\n")
            
            f.write("---\n\n")
            f.write("*Generado por yaml_lint_v6_semantic.py*\n")
    
    def print_report(self):
        """Imprime reporte detallado de validación"""
        errors = [i for i in self.issues if i['severity'] == 'error']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        infos = [i for i in self.issues if i['severity'] == 'info']
        
        print("\n" + "="*80)
        print("📋 REPORTE DE VALIDACIÓN SEMÁNTICA APS v3.5")
        print("="*80)
        
        if errors:
            print(f"\n❌ ERRORES CRÍTICOS: {len(errors)}")
            print("-" * 80)
            
            for idx, issue in enumerate(errors, 1):
                print(f"\n{idx}. 📍 Ubicación: {issue['location']}")
                print(f"   ❌ Problema: {issue['message']}")
                
                # Añadir recomendación según tipo de error
                if 'SID duplicado' in issue['message']:
                    print(f"   💡 Acción: Consolidar bloques duplicados o renombrar SID único")
                    print(f"   📖 Documentación: APS/LINTER_RULES.md § 1.3 (Unicidad de SIDs)")
                    
                elif 'Contradicción' in issue['message']:
                    print(f"   💡 Acción: Decidir política única y eliminar instrucción contradictoria")
                    print(f"   📖 Ver: METODOLOGIA § 2 (Problema operativo - Contradicciones)")
                    
                elif 'DENY_TERM' in issue['message']:
                    print(f"   💡 Acción: Añadir validación de confirmación de usuario antes de ejecutar")
                    print(f"   📖 Regla: APS/LINTER_RULES.md § 2.1 (DENY_TERMS)")
        
        if warnings:
            print(f"\n\n⚠️  WARNINGS: {len(warnings)}")
            print("-" * 80)
            
            for idx, issue in enumerate(warnings, 1):
                print(f"\n{idx}. 📍 Ubicación: {issue['location']}")
                print(f"   ⚠️  Problema: {issue['message']}")
                
                # Añadir recomendación según tipo de warning
                if 'no encontrado' in issue['message']:
                    if 'Entry Guard' in issue['message']:
                        print(f"   💡 Acción: Añadir bloque de validación de entrada")
                        print(f"   📝 Template: BLK.verificar.control.active_agent.guard")
                    elif 'Exit Strategy' in issue['message']:
                        print(f"   💡 Acción: Definir condiciones de terminación del agente")
                        print(f"   📝 Template: BLK.detectar.salida.protocol")
                    elif 'State JSON' in issue['message']:
                        print(f"   💡 Acción: Añadir protocolo STATE_JSON para handoff")
                        print(f"   📝 Template: PROT.generar.state_json.template")
                        
                elif 'Desplazamiento' in issue['message']:
                    print(f"   💡 Acción: Mover contenido a sección correcta o ajustar block_type")
                    
                elif 'inconsistente' in issue['message']:
                    print(f"   💡 Acción: Unificar estructura de STATE_JSON en todo el agente")
                    print(f"   📖 Ver: APS § 11 (Protocolo STATE_JSON)")
                    
                elif 'mapeada a' in issue['message']:
                    print(f"   💡 Acción: Asignar cada fase a un solo agente responsable")
        
        if infos:
            print(f"\n\nℹ️  INFORMACIÓN: {len(infos)}")
            print("-" * 80)
            
            for issue in infos:
                print(f"\n   ℹ️  {issue['message']}")
                if 'LOW confidence' in issue['message']:
                    print(f"   💡 Acción: Revisar bloques marcados y enriquecer con vocabulario APS")
                    print(f"   📖 Ver: aps-tooling/schemas/sid_vocabulary_v1.yaml")
        
        if not errors and not warnings and not infos:
            print("\n✅ VALIDACIÓN EXITOSA: Sin problemas detectados")
            print("\nEl agente cumple con todos los requisitos semánticos de APS v3.5")
        
        # Resumen ejecutivo
        print("\n" + "="*80)
        print("📊 RESUMEN EJECUTIVO")
        print("="*80)
        print(f"   ❌ Errores críticos:  {len(errors)}")
        print(f"   ⚠️  Warnings:          {len(warnings)}")
        print(f"   ℹ️  Información:       {len(infos)}")
        
        if len(errors) > 0:
            print(f"\n   🚫 Estado: VALIDACIÓN FALLIDA - Bloquea integración")
            print(f"   📝 Próximo paso: Corregir errores críticos en archivo .md fuente")
        elif len(warnings) > 0:
            print(f"\n   ⚠️  Estado: VALIDACIÓN CON WARNINGS - Requiere revisión")
            print(f"   📝 Próximo paso: Revisar warnings antes de integrar")
        else:
            print(f"\n   ✅ Estado: LISTO PARA INTEGRACIÓN")
        
        print("="*80 + "\n")
        
        return len(errors)


def main():
    parser = argparse.ArgumentParser(
        description='APS v3.5 - YAML Semantic Linter v6 (SID-Based)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 yaml_lint_v6_semantic.py agent.yaml
  python3 yaml_lint_v6_semantic.py swarm/agents/**/*.yaml
  python3 yaml_lint_v6_semantic.py agent.yaml --output report.md
        """
    )
    
    parser.add_argument(
        'yaml_files', 
        nargs='+', 
        type=Path, 
        help='Archivos YAML a validar'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Guardar reporte en archivo (opcional)'
    )
    
    args = parser.parse_args()
    
    print("🔍 APS v3.5 - Validador Semántico (basado en SIDs)")
    print("="*80 + "\n")
    
    validator = SemanticValidator()
    total_errors = 0
    total_warnings = 0
    
    for yaml_file in args.yaml_files:
        if not yaml_file.exists():
            print(f"❌ Archivo no encontrado: {yaml_file}")
            continue
            
        print(f"📄 Validando: {yaml_file.name}")
        print("-" * 80)
        
        errors, warnings = validator.validate_file(yaml_file)
        total_errors += errors
        total_warnings += warnings
    
    # Reporte en terminal
    exit_code = validator.print_report()
    
    # Guardar reporte en archivo si se especificó
    if args.output:
        validator.save_report(args.output, args.yaml_files)
        print(f"\n💾 Reporte guardado en: {args.output}")
    else:
        # Auto-guardar en swarm/reports/validation/
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Determinar nombre del swarm
        if len(args.yaml_files) > 0:
            swarm_name = args.yaml_files[0].parent.name
        else:
            swarm_name = "unknown"
        
        report_dir = Path('swarm/reports/validation')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"{swarm_name}_validation_{timestamp}.md"
        validator.save_report(report_file, args.yaml_files)
        print(f"\n💾 Reporte auto-guardado en: {report_file}")
    
    # Exit code
    sys.exit(exit_code if exit_code < 3 else 2)


if __name__ == "__main__":
    main()
