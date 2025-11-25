import re
import yaml
from pathlib import Path

# Diccionario parametrizable de abreviaturas de tipo de bloque
BLOCK_TYPE_MAP = {
    'Motivaciones': 'GOAL',
    'Stakeholders': 'STK',
    'AS-IS': 'ASIS',
    'Riesgos': 'CST',
    'Restricciones': 'CST',
    'GAP': 'GAP',
    'Requisitos': 'REQ',
    'OUTPUT': 'OUT',
    'Meta': 'META',
    'Instrucciones': 'INS',
    'Variables': 'VAR',
}

# Mapeos para inferir acción, relación y nivel
ACCION_KEYWORDS = {
    'verificar': ['guard', 'validar', 'comprobar', 'verificar', 'entry guard'],
    'instruir': ['instrucciones', 'protocolo', 'reglas', 'guía', 'procedimiento'],
    'detectar': ['detectar', 'identificar', 'reconocer', 'paso'],
    'generar': ['output', 'salida', 'generar', 'producir'],
    'capturar': ['capturar', 'recopilar', 'obtener', 'preguntar'],
    'coordinar': ['coordinar', 'activar', 'delegar', 'flujo'],
    'resumir': ['resumen', 'resumir', 'consolidar'],
}

RELACION_KEYWORDS = {
    'control.active_agent': ['control', 'active_agent', 'guard', 'entry'],
    'usuario.respuesta': ['usuario', 'respuesta', 'primera', 'output'],
    'agente': ['agente', 'agent', 'swarm', 'orquestador'],
    'fase': ['fase', 'phase', 'motivaciones', 'stakeholders', 'asis', 'riesgos', 'gap', 'requisitos'],
    'estado': ['estado', 'state', 'json', 'session'],
}

NIVEL_KEYWORDS = {
    'guard': ['guard', 'entry', 'validación'],
    'tactical': ['táctica', 'tactical', 'operación'],
    'strategic': ['estratégico', 'strategic', 'objetivo'],
    'general': ['general', 'protocolo', 'instrucción'],
}

def extract_blocks_from_md(md_path):
    """
    Extrae bloques explícitos de un archivo Markdown usando encabezados.
    Devuelve un diccionario con el nombre del bloque, su tipo y su contenido.
    Auto-numera bloques duplicados para que el linter los detecte posteriormente.
    Genera placeholders para accion, relacion, nivel y SIDs temporales.
    """
    blocks = {}
    block_counts = {}  # Contador de apariciones de cada nombre de bloque
    temp_sid_counter = 1  # Contador para SIDs temporales
    current_block = None
    current_content = []
    header_pattern = re.compile(r'^(#{1,6})\s*(.+)$')

    def get_block_type(block_name):
        """
        Infiere el tipo de bloque basado en el nombre.
        Detecta marcadores especiales como [EXAMPLE] o [ANTIPATRÓN].
        """
        name_upper = block_name.upper()
        
        # Detectar marcadores especiales (exentos de DENY_TERMS)
        if '[EXAMPLE]' in name_upper or '[EJEMPLO]' in name_upper:
            return 'EXAMPLE'
        if '[ANTIPATRÓN]' in name_upper or '[ANTIPATRON]' in name_upper:
            return 'ANTIPATTERN'
        
        # Mapeo estándar
        for key in BLOCK_TYPE_MAP:
            if key.lower() in block_name.lower():
                return BLOCK_TYPE_MAP[key]
        return 'BLK'

    with open(md_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = header_pattern.match(line)
            if match:
                if current_block:
                    content = '\n'.join(current_content).strip()
                    block_type = get_block_type(current_block)
                    
                    blocks[current_block] = {
                        'block_type': block_type,
                        'accion': '<<PENDING_AI>>',
                        'relacion': '<<PENDING_AI>>',
                        'nivel': '<<PENDING_AI>>',
                        'sid': f'TEMP_{block_type}_{temp_sid_counter:03d}',
                        'content': content
                    }
                    temp_sid_counter += 1
                
                # Detectar duplicados y auto-numerar
                raw_block_name = match.group(2).strip()
                if raw_block_name in block_counts:
                    block_counts[raw_block_name] += 1
                    current_block = f"{raw_block_name} ({block_counts[raw_block_name]})"
                else:
                    block_counts[raw_block_name] = 1
                    current_block = raw_block_name
                
                current_content = []
            else:
                if current_block:
                    current_content.append(line.rstrip())
        if current_block:
            content = '\n'.join(current_content).strip()
            block_type = get_block_type(current_block)
            
            blocks[current_block] = {
                'block_type': block_type,
                'accion': '<<PENDING_AI>>',
                'relacion': '<<PENDING_AI>>',
                'nivel': '<<PENDING_AI>>',
                'sid': f'TEMP_{block_type}_{temp_sid_counter:03d}',
                'content': content
            }
    return blocks

def generate_yaml_for_agent(md_path, yaml_path):
    blocks = extract_blocks_from_md(md_path)
    agent_struct = {
        'agent': {
            'name': Path(md_path).stem,
            'source_md': str(md_path),
            'blocks': blocks
        }
    }
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(agent_struct, f, allow_unicode=True, sort_keys=False)

def process_file(md_file):
    """
    Procesa un único archivo .md y genera su correspondiente .yaml.
    Retorna True si tuvo éxito, False en caso contrario.
    """
    yaml_file = str(Path(md_file).with_suffix('.yaml'))
    try:
        generate_yaml_for_agent(md_file, yaml_file)
        return True
    except Exception as e:
        print(f"❌ Error procesando {Path(md_file).name}: {e}")
        return False

def collect_files(args):
    """
    Recolecta todos los archivos .md a procesar desde los argumentos.
    Soporta:
    - Archivos individuales: archivo.md
    - Directorios: carpeta/ → carpeta/*.md
    - Patrones glob: ruta/*.md
    - Múltiples argumentos: file1.md file2.md file3.md
    
    Retorna lista de rutas absolutas a archivos .md válidos.
    """
    import glob
    
    files_to_process = []
    
    for arg in args:
        arg_path = Path(arg)
        
        # Caso 1: Es un directorio → buscar todos los .md dentro
        if arg_path.is_dir():
            md_files = list(arg_path.glob('*.md'))
            if md_files:
                files_to_process.extend([str(f) for f in md_files])
            else:
                print(f"⚠️  Warning: No se encontraron archivos .md en {arg}")
        
        # Caso 2: Es un archivo .md existente
        elif arg_path.is_file() and arg_path.suffix == '.md':
            files_to_process.append(str(arg_path))
        
        # Caso 3: Puede ser un patrón glob
        elif '*' in arg or '?' in arg:
            matches = glob.glob(arg, recursive=True)
            md_matches = [f for f in matches if f.endswith('.md')]
            if md_matches:
                files_to_process.extend(md_matches)
            else:
                print(f"⚠️  Warning: El patrón '{arg}' no coincide con ningún archivo .md")
        
        # Caso 4: No es válido
        else:
            if arg_path.exists() and not arg_path.suffix == '.md':
                print(f"⚠️  Warning: '{arg}' no es un archivo .md (ignorado)")
            else:
                print(f"⚠️  Warning: '{arg}' no existe o no es válido (ignorado)")
    
    # Eliminar duplicados y ordenar
    files_to_process = sorted(set(files_to_process))
    
    return files_to_process

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python md2yaml.py <archivo.md> [salida.yaml]")
        print("  o: python md2yaml.py <directorio/>")
        print("  o: python md2yaml.py <patrón.md>")
        print("  o: python md2yaml.py archivo1.md archivo2.md ...")
        exit(1)
    
    # Caso especial: modo simple con archivo de salida explícito
    # python md2yaml.py archivo.md salida.yaml
    if len(sys.argv) == 3 and not sys.argv[2].endswith('.md') and Path(sys.argv[1]).is_file():
        md_path = sys.argv[1]
        yaml_path = sys.argv[2]
        generate_yaml_for_agent(md_path, yaml_path)
        print(f"✅ YAML generado en {yaml_path}")
        exit(0)
    
    # Modo batch: recolectar archivos de todos los argumentos
    files_to_process = collect_files(sys.argv[1:])
    
    if not files_to_process:
        print("❌ No se encontraron archivos .md para procesar")
        exit(1)
    
    # Procesar archivos
    if len(files_to_process) == 1:
        # Modo simple: un solo archivo
        md_file = files_to_process[0]
        yaml_file = str(Path(md_file).with_suffix('.yaml'))
        success = process_file(md_file)
        if success:
            print(f"✅ YAML generado: {yaml_file}")
            exit(0)
        else:
            exit(1)
    else:
        # Modo batch: múltiples archivos
        print(f"🔄 Procesando {len(files_to_process)} archivos Markdown...")
        success_count = 0
        
        for i, md_file in enumerate(files_to_process, 1):
            yaml_file = str(Path(md_file).with_suffix('.yaml'))
            if process_file(md_file):
                print(f"✅ [{i}/{len(files_to_process)}] {Path(md_file).name} → {Path(yaml_file).name}")
                success_count += 1
        
        print(f"\n✅ Completado: {success_count}/{len(files_to_process)} archivos convertidos")
        exit(0 if success_count == len(files_to_process) else 1)
