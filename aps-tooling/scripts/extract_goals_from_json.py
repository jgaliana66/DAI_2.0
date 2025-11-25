#!/usr/bin/env python3
"""
FASE 1 - JSON Goal Extractor
Extrae el campo 'goals' de cada agente en un JSON SwarmBuilder
y crea archivos .md individuales.

Parte del pipeline APS v4.0
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def validate_json_structure(json_data: dict) -> Tuple[bool, str]:
    """
    Valida que el JSON tenga la estructura esperada de SwarmBuilder.
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if not isinstance(json_data, dict):
        return False, "JSON root debe ser un objeto/diccionario"
    
    if 'agents' not in json_data:
        return False, "JSON no contiene campo 'agents'"
    
    if not isinstance(json_data['agents'], list):
        return False, "Campo 'agents' debe ser un array"
    
    if len(json_data['agents']) == 0:
        return False, "Campo 'agents' está vacío"
    
    # Validar que cada agente tenga 'name' y 'goals'
    for idx, agent in enumerate(json_data['agents']):
        if 'name' not in agent:
            return False, f"Agente en índice {idx} no tiene campo 'name'"
        
        if 'goals' not in agent:
            return False, f"Agente '{agent.get('name', f'Agent{idx}')}' no tiene campo 'goals'"
    
    return True, ""


def extract_goals(json_path: str, output_dir: str = None, force: bool = False) -> Dict[str, any]:
    """
    Extrae goals de un JSON SwarmBuilder y crea archivos .md.
    
    Args:
        json_path: Ruta al archivo JSON
        output_dir: Directorio de salida (opcional, por defecto swarm/agents/{base_name})
        force: Si True, sobrescribe archivos existentes sin preguntar
        
    Returns:
        Dict con información del proceso:
        {
            'success': bool,
            'files_created': List[str],
            'json_copy': str,
            'total_agents': int,
            'errors': List[str]
        }
    """
    result = {
        'success': False,
        'files_created': [],
        'json_copy': None,
        'total_agents': 0,
        'errors': []
    }
    
    # Validar que el archivo existe
    json_file = Path(json_path)
    if not json_file.exists():
        result['errors'].append(f"Archivo no encontrado: {json_path}")
        return result
    
    if not json_file.suffix == '.json':
        result['errors'].append(f"El archivo debe tener extensión .json: {json_path}")
        return result
    
    # Leer y parsear JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        result['errors'].append(f"Error parseando JSON: {e}")
        return result
    except Exception as e:
        result['errors'].append(f"Error leyendo archivo: {e}")
        return result
    
    # Validar estructura
    is_valid, error_msg = validate_json_structure(json_data)
    if not is_valid:
        result['errors'].append(f"Estructura JSON inválida: {error_msg}")
        return result
    
    # Determinar directorio de salida
    base_name = json_file.stem  # Nombre sin extensión
    if output_dir is None:
        output_dir = f"swarm/agents/{base_name}"
    
    output_path = Path(output_dir)
    
    # Crear directorio (preguntar si existe y no force)
    if output_path.exists() and not force:
        print(f"⚠️  El directorio {output_path} ya existe.")
        response = input("¿Desea sobrescribir los archivos? (s/n): ").strip().lower()
        if response not in ['s', 'si', 'sí', 'y', 'yes']:
            result['errors'].append("Operación cancelada por el usuario")
            return result
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Copiar JSON al directorio de salida
    json_copy_path = output_path / json_file.name
    try:
        import shutil
        shutil.copy2(json_file, json_copy_path)
        result['json_copy'] = str(json_copy_path)
    except Exception as e:
        result['errors'].append(f"Error copiando JSON: {e}")
        # No es crítico, continuamos
    
    # Procesar cada agente
    agents = json_data['agents']
    result['total_agents'] = len(agents)
    
    for idx, agent in enumerate(agents, start=1):
        agent_name = agent.get('name', f'Agent{idx}')
        goals_content = agent.get('goals', '')
        
        # Nombre del archivo: XX-AgentName.md
        filename = f"{idx:02d}-{agent_name}.md"
        filepath = output_path / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(goals_content)
            result['files_created'].append(str(filepath))
        except Exception as e:
            result['errors'].append(f"Error escribiendo {filename}: {e}")
    
    # Marcar como exitoso si se crearon archivos
    result['success'] = len(result['files_created']) > 0
    
    return result


def main():
    """Función principal para uso desde línea de comandos"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extrae el campo "goals" de cada agente en un JSON SwarmBuilder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s swarm/json/J2C-v1-Swarm-v3-5.json
  %(prog)s swarm/json/J2C-v1-Swarm-v3-5.json --output custom/path
  %(prog)s swarm/json/J2C-v1-Swarm-v3-5.json --force
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Ruta al archivo JSON SwarmBuilder'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Directorio de salida (default: swarm/agents/{base_name})',
        default=None
    )
    
    parser.add_argument(
        '-f', '--force',
        help='Sobrescribir archivos existentes sin preguntar',
        action='store_true'
    )
    
    parser.add_argument(
        '--json',
        help='Salida en formato JSON',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Ejecutar extracción
    result = extract_goals(args.json_file, args.output, args.force)
    
    # Mostrar resultados
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result['success']:
            print(f"\n✅ Extracción completada exitosamente")
            print(f"\n📊 Resumen:")
            print(f"   - Total agentes: {result['total_agents']}")
            print(f"   - Archivos creados: {len(result['files_created'])}")
            if result['json_copy']:
                print(f"   - JSON copiado a: {result['json_copy']}")
            
            print(f"\n📁 Archivos generados:")
            for filepath in result['files_created']:
                print(f"   ✓ {filepath}")
            
            if result['errors']:
                print(f"\n⚠️  Advertencias:")
                for error in result['errors']:
                    print(f"   - {error}")
        else:
            print(f"\n❌ Error en la extracción")
            print(f"\n🔴 Errores:")
            for error in result['errors']:
                print(f"   - {error}")
            sys.exit(1)
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
