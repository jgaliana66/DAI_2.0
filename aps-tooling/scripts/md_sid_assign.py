#!/usr/bin/env python3
"""
Asigna SIDs determinísticos a ítems en Markdown de agentes SWARM.
Idempotente: mismo texto → mismo SID.

Formato SID: <PREFIJO>_<SLUG>_<HASH4>
Ejemplo: G_CAPTURAR_MOTIVACIONES_7B3F

Uso:
    python3 md_sid_assign.py <archivo.md>
    python3 md_sid_assign.py --batch swarm/agents/*.md
"""

import re
import hashlib
import unicodedata
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Prefijos por sección
SECTION_PREFIXES = {
    'GOALS': 'G',
    'GOAL': 'G',
    'CONSTRAINTS': 'C',
    'CONSTRAINT': 'C',
    'PROTOCOLS': 'P',
    'PROTOCOL': 'P',
    'KEYWORDS': 'K',
    'HEURISTICS': 'H',
    'HEURISTIC': 'H',
    'POLICIES': 'POL',
    'POLICY': 'POL',
    'INSTRUCTIONS': 'I',
    'VARIABLES': 'V',
    'OUTPUT': 'OUT',
    'BLOCKS': 'BLK',
    'LOOPS': 'L',
    'LOOP': 'L',
}

# Regex para detectar secciones
SECTION_REGEX = re.compile(r'^##\s+([A-Z][A-Z\s]+)\s*$', re.MULTILINE)

# Regex para detectar ítems (viñetas)
ITEM_REGEX = re.compile(r'^(\s*)- (.+)$', re.MULTILINE)

# Regex para detectar SID existente
SID_MARKER_REGEX = re.compile(
    r'<!--sid:([A-Z0-9_]+)(?:\s+sha1=([0-9a-f]{8}))?-->\s*\n(.+?)\n\s*<!--/sid-->',
    re.DOTALL
)


def slugify(text: str, max_words: int = 5) -> str:
    """
    Convierte texto a SLUG normalizado.
    - Quita tildes
    - Solo a-z0-9
    - Mayúsculas
    - Max 5-7 palabras
    """
    # Normalizar unicode (quitar tildes)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Quitar puntuación, colapsar espacios
    text = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Tomar primeras N palabras
    words = text.split()[:max_words]
    slug = '_'.join(words).upper()
    
    return slug if slug else 'UNNAMED'


def compute_hash(text: str, length: int = 4) -> str:
    """
    Calcula hash SHA1 del texto y retorna primeros N caracteres hex.
    """
    sha1 = hashlib.sha1(text.strip().encode('utf-8')).hexdigest()
    return sha1[:length * 2]  # 4 bytes = 8 caracteres hex


def generate_sid(prefix: str, text: str) -> Tuple[str, str]:
    """
    Genera SID determinístico: <prefix>_<slug>_<hash>
    Retorna (sid, sha1_hash)
    """
    slug = slugify(text, max_words=5)
    hash8 = compute_hash(text, length=4)
    hash4 = hash8[:4].upper()  # Primeros 4 caracteres hex
    
    sid = f"{prefix}_{slug}_{hash4}"
    return sid, hash8


def extract_sections(content: str) -> Dict[str, List[Tuple[int, str, str]]]:
    """
    Extrae secciones y sus ítems del Markdown.
    Retorna: {section_name: [(line_num, indent, item_text), ...]}
    """
    sections = {}
    current_section = None
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Detectar sección
        section_match = SECTION_REGEX.match(line)
        if section_match:
            section_name = section_match.group(1).strip().upper()
            # Normalizar nombre de sección
            for key in SECTION_PREFIXES:
                if key in section_name:
                    current_section = key
                    break
            if current_section not in sections:
                sections[current_section] = []
            continue
        
        # Detectar ítem (viñeta)
        if current_section:
            item_match = ITEM_REGEX.match(line)
            if item_match:
                indent = item_match.group(1)
                item_text = item_match.group(2).strip()
                sections[current_section].append((i, indent, item_text))
    
    return sections


def assign_sids(md_path: Path, dry_run: bool = False) -> bool:
    """
    Procesa un archivo Markdown, asigna SIDs faltantes y actualiza sha1.
    Retorna True si hubo cambios.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    lines = content.split('\n')
    
    # Extraer SIDs existentes para detectar colisiones
    existing_sids = {}
    for match in SID_MARKER_REGEX.finditer(content):
        sid = match.group(1)
        existing_sids[sid] = match.group(3).strip()
    
    # Extraer secciones e ítems
    sections = extract_sections(content)
    
    changes = []
    new_sids = {}
    
    for section_name, items in sections.items():
        if section_name not in SECTION_PREFIXES:
            continue
        
        prefix = SECTION_PREFIXES[section_name]
        
        for line_num, indent, item_text in items:
            # Verificar si ya tiene SID
            line_content = lines[line_num]
            
            # Buscar si las líneas anteriores tienen <!--sid:...-->
            has_sid = False
            if line_num > 0 and '<!--sid:' in lines[line_num - 1]:
                has_sid = True
            
            if not has_sid:
                # Generar nuevo SID
                sid, sha1 = generate_sid(prefix, item_text)
                
                # Verificar colisiones
                collision_count = 0
                original_sid = sid
                while sid in existing_sids or sid in new_sids:
                    collision_count += 1
                    sid = f"{original_sid}_{chr(64 + collision_count)}"  # _A, _B, _C...
                
                new_sids[sid] = item_text
                
                # Insertar marcador
                marker_start = f"{indent}<!--sid:{sid} sha1={sha1}-->"
                marker_end = f"{indent}<!--/sid-->"
                
                # Reemplazar línea
                lines[line_num] = f"{marker_start}\n{indent}- {item_text}\n{marker_end}"
                
                changes.append(f"  + {sid}: {item_text[:50]}...")
    
    if not changes:
        print(f"✅ {md_path.name}: sin cambios (todos los ítems ya tienen SID)")
        return False
    
    # Generar contenido actualizado
    new_content = '\n'.join(lines)
    
    if dry_run:
        print(f"🔍 {md_path.name}: {len(changes)} SIDs a generar (dry-run)")
        for change in changes[:5]:  # Mostrar solo primeros 5
            print(change)
        return True
    
    # Guardar
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {md_path.name}: {len(changes)} SIDs asignados")
    for change in changes[:3]:  # Mostrar solo primeros 3
        print(change)
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Asigna SIDs determinísticos a agentes SWARM')
    parser.add_argument('files', nargs='+', help='Archivos .md a procesar')
    parser.add_argument('--batch', action='store_true', help='Procesar múltiples archivos')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin escribir cambios')
    
    args = parser.parse_args()
    
    if args.batch:
        import glob
        pattern = args.files[0] if args.files else 'swarm/agents/*.md'
        files = glob.glob(pattern)
        files = [Path(f) for f in files if f.endswith('.md')]
    else:
        files = [Path(f) for f in args.files]
    
    print(f"🔄 Procesando {len(files)} archivos Markdown...")
    
    changed = 0
    for f in files:
        if not f.exists():
            print(f"⚠️  {f}: no existe")
            continue
        
        if assign_sids(f, dry_run=args.dry_run):
            changed += 1
    
    print(f"\n✅ Completado: {changed}/{len(files)} archivos modificados")


if __name__ == '__main__':
    main()
