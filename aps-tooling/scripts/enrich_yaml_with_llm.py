#!/usr/bin/env python3
"""
Genera YAMLs de agentes SWARM con placeholders semánticos.
Añade: accion=<<PENDING_AI>>, relacion=<<PENDING_AI>>, nivel=<<PENDING_AI>>, sid=TEMP_XXX_NNN

El agente Copilot @sid-generator reemplazará los placeholders con SIDs semánticos reales.
"""

import yaml
import sys
import json
from pathlib import Path

# Prompt para el LLM (puedes usar con OpenAI API, Anthropic, etc.)
ENRICHMENT_PROMPT = """
Analiza este bloque de un agente SWARM y extrae los atributos semánticos:

**Bloque:**
Nombre: {block_name}
Tipo: {block_type}
Contenido: {content}

**Tu tarea:**
1. Identifica la `accion` principal (verbo: verificar, capturar, generar, detectar, etc.)
2. Identifica la `relacion` (con qué interactúa: usuario, control, estado, output, etc.)
3. Identifica el `nivel` (guard, protocol, workflow, template, meta, etc.)
4. Genera el `sid` en formato: {block_type}.accion.relacion.nivel

**Responde SOLO con JSON válido:**
{{
  "accion": "...",
  "relacion": "...",
  "nivel": "...",
  "sid": "..."
}}
"""

PENDING_AI = '<<PENDING_AI>>'

def analyze_block_semantic(block_type, block_index):
    """
    Genera placeholders temporales para SIDs.
    El agente Copilot (@sid-generator) los reemplazará con SIDs semánticos reales.
    
    Formato temporal: TEMP_<TYPE>_NNN
    Formato final (generado por IA): <TYPE>.<accion>.<relacion>.<nivel>
    """
    # Generar SID temporal numerado (placeholder para Copilot)
    temp_sid = f"TEMP_{block_type}_{block_index:03d}"
    
    return {
        'accion': PENDING_AI,
        'relacion': PENDING_AI,
        'nivel': PENDING_AI,
        'sid': temp_sid
    }


def enrich_yaml_file(input_path, output_path=None):
    """
    Lee un YAML de agente, enriquece bloques con atributos semánticos,
    y guarda el resultado.
    """
    if output_path is None:
        output_path = input_path
    
    # Leer YAML preservando orden
    with open(input_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'agent' not in data or 'blocks' not in data['agent']:
        print(f"⚠️  {input_path}: no tiene estructura agent.blocks esperada")
        return False
    
    blocks = data['agent']['blocks']
    enriched_count = 0
    block_index = 0
    
    for block_name, block_data in blocks.items():
        if not isinstance(block_data, dict):
            continue
        
        block_type = block_data.get('block_type', 'BLK')
        content = block_data.get('content', '')
        
        # Si ya tiene SID real (no temporal), saltar
        if 'sid' in block_data and not block_data['sid'].startswith('TEMP_'):
            continue
        
        # Analizar y generar placeholder temporal
        block_index += 1
        semantic = analyze_block_semantic(block_type, block_index)
        
        # Insertar atributos (mantener orden: block_type, accion, relacion, nivel, sid, content)
        ordered_block = {
            'block_type': block_type,
            'accion': semantic['accion'],
            'relacion': semantic['relacion'],
            'nivel': semantic['nivel'],
            'sid': semantic['sid'],
            'content': content
        }
        
        blocks[block_name] = ordered_block
        enriched_count += 1
    
    # Guardar YAML enriquecido
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ {input_path.name}: {enriched_count} bloques con placeholders generados")
    print("   → Siguiente paso: @sid-generator para SIDs semánticos")
    return True


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 enrich_yaml_with_llm.py <archivo.yaml> [output.yaml]")
        print("  o: python3 enrich_yaml_with_llm.py --batch swarm/agents/*.yaml")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        # Modo batch: procesar múltiples archivos
        import glob
        pattern = sys.argv[2] if len(sys.argv) > 2 else 'swarm/agents/*.yaml'
        files = glob.glob(pattern)
        
        print(f"🔄 Enriqueciendo {len(files)} archivos YAML...")
        success = 0
        for f in files:
            if enrich_yaml_file(Path(f)):
                success += 1
        
        print(f"\n✅ Completado: {success}/{len(files)} archivos enriquecidos")
    else:
        # Modo simple: un archivo
        input_file = Path(sys.argv[1])
        output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file
        enrich_yaml_file(input_file, output_file)


if __name__ == '__main__':
    main()
