#!/usr/bin/env python3
"""
YAML Pipeline CLI - Modo Batch para CI/CD

Ejecuta el pipeline completo (md2yaml + enrich + lint) en modo batch.
Compatible con CI/CD: salida JSON, exit codes claros, sin emojis.

Uso:
    # Modo CI (JSON, sin colores)
    python3 yaml_pipeline_cli.py --batch "swarm/agents/**/*.md" --ci-mode
    
    # Modo interactivo (colores, emojis)
    python3 yaml_pipeline_cli.py --batch "swarm/agents/**/*.md"
    
Exit Codes:
    0 = Success (sin errores ni warnings)
    1 = Warnings (ej: LOW confidence SIDs)
    2 = Errors (ej: DENY_TERMS, duplicados)
    3 = Validation failed
    4 = Security error
    5 = Internal error
"""

import argparse
import json
import sys
import glob
import subprocess
import shlex
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Exit codes
EXIT_CODE_SUCCESS = 0
EXIT_CODE_WARNINGS = 1
EXIT_CODE_ERRORS = 2
EXIT_CODE_VALIDATION_FAILED = 3
EXIT_CODE_SECURITY_ERROR = 4
EXIT_CODE_INTERNAL_ERROR = 5

# Security: Allowed scripts and paths
ALLOWED_SCRIPTS = [
    'code/md2yaml.py',
    'code/enrich_yaml_with_llm.py',
    'code/yaml_lint.py'
]

ALLOWED_PREFIXES = [
    'swarm/agents/',
    'code/'
]


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


def validate_file_path(file_path: str) -> Path:
    """
    Valida que el path sea seguro.
    
    Raises:
        SecurityError: Si el path es inseguro
    """
    path = Path(file_path).resolve()
    
    # 1. Verificar que existe
    if not path.exists():
        raise SecurityError(f"Path no existe: {file_path}")
    
    # 2. Verificar prefijos permitidos
    relative = str(path.relative_to(Path.cwd()))
    if not any(relative.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        raise SecurityError(f"Path fuera de scope permitido: {relative}")
    
    # 3. Verificar extensión
    if path.suffix not in ['.md', '.yaml', '.py']:
        raise SecurityError(f"Extensión no permitida: {path.suffix}")
    
    return path


def execute_safe_command(script: str, *args) -> Tuple[int, str, str]:
    """
    Ejecuta comando con validación de seguridad.
    
    Returns:
        (exit_code, stdout, stderr)
    
    Raises:
        SecurityError: Si el script no está en allowlist
    """
    if script not in ALLOWED_SCRIPTS:
        raise SecurityError(f"Script no permitido: {script}")
    
    # Construir comando - NO usar shlex.quote() aquí porque subprocess.run ya maneja esto
    cmd = ['python3', script] + [str(arg) for arg in args]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos max
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        raise SecurityError(f"Timeout ejecutando {script}")


def parse_lint_output(stdout: str, stderr: str) -> Dict:
    """
    Parsea salida de yaml_lint.py.
    
    Returns:
        {
            "errors": [...],
            "warnings": [...],
            "duplicates": [...],
            "auto_numbered": [...]
        }
    """
    errors = []
    warnings = []
    duplicates = []
    auto_numbered = []
    
    # Parsear stderr (donde yaml_lint.py escribe los errores)
    for line in stderr.split('\n'):
        if '❌' in line or 'ERROR' in line:
            errors.append({
                "severity": "ERROR",
                "message": line.strip()
            })
        elif '⚠️' in line or 'WARNING' in line:
            warnings.append({
                "severity": "WARNING",
                "message": line.strip()
            })
        elif 'DUPLICADO' in line.upper():
            duplicates.append(line.strip())
        elif 'AUTO-NUMERADO' in line.upper():
            auto_numbered.append(line.strip())
    
    return {
        "errors": errors,
        "warnings": warnings,
        "duplicates": duplicates,
        "auto_numbered": auto_numbered
    }


def process_single_file(md_file: str, ci_mode: bool) -> Dict:
    """
    Procesa un archivo .md individual.
    
    Returns:
        {
            "source": "archivo.md",
            "output": "archivo.yaml",
            "status": "success|error",
            "blocks": 22,
            "errors": [...],
            "warnings": [...]
        }
    """
    try:
        # Validar path
        md_path = validate_file_path(md_file)
        yaml_path = md_path.with_suffix('.yaml')
        
        if not ci_mode:
            print(f"🔄 Procesando: {md_file}")
        
        # FASE 1: Conversión MD → YAML
        exit_code, stdout, stderr = execute_safe_command(
            'code/md2yaml.py',
            str(md_path)
        )
        
        if exit_code != 0:
            return {
                "source": str(md_path),
                "output": str(yaml_path),
                "status": "error",
                "blocks": 0,
                "errors": [{
                    "code": "MD2YAML_FAILED",
                    "message": f"md2yaml.py failed: {stderr}"
                }],
                "warnings": []
            }
        
        # FASE 2: Enriquecimiento (actualmente manual con @sid-generator)
        # En CI mode, asumimos que los SIDs ya existen o se saltean
        if not ci_mode:
            print(f"  ⏩ Saltando enriquecimiento (requiere @sid-generator manual)")
        
        # FASE 3: Validación
        exit_code, stdout, stderr = execute_safe_command(
            'code/yaml_lint.py',
            str(yaml_path)
        )
        
        lint_result = parse_lint_output(stdout, stderr)
        
        # Contar bloques (leer YAML)
        blocks = count_blocks_in_yaml(yaml_path)
        
        status = "success"
        if lint_result["errors"]:
            status = "error"
        elif lint_result["warnings"]:
            status = "warning"
        
        return {
            "source": str(md_path),
            "output": str(yaml_path),
            "status": status,
            "blocks": blocks,
            "errors": lint_result["errors"],
            "warnings": lint_result["warnings"],
            "duplicates": lint_result["duplicates"],
            "auto_numbered": lint_result["auto_numbered"]
        }
        
    except SecurityError as e:
        return {
            "source": md_file,
            "status": "security_error",
            "errors": [{
                "code": "SECURITY_ERROR",
                "message": str(e)
            }],
            "warnings": []
        }
    except Exception as e:
        return {
            "source": md_file,
            "status": "internal_error",
            "errors": [{
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }],
            "warnings": []
        }


def count_blocks_in_yaml(yaml_path: Path) -> int:
    """Cuenta bloques en YAML (simple conteo de líneas 'sid:')."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content.count('sid:')
    except:
        return 0


def run_batch(pattern: str, ci_mode: bool = False) -> int:
    """
    Ejecuta pipeline en modo batch.
    
    Args:
        pattern: Glob pattern (ej: "swarm/agents/**/*.md")
        ci_mode: Si True, salida JSON sin emojis
    
    Returns:
        Exit code (0=success, 1=warnings, 2=errors)
    """
    files = glob.glob(pattern, recursive=True)
    files = [f for f in files if f.endswith('.md')]
    
    if not files:
        if ci_mode:
            print(json.dumps({
                "status": "error",
                "exit_code": EXIT_CODE_ERRORS,
                "message": f"No files found: {pattern}"
            }))
        else:
            print(f"❌ No se encontraron archivos con patrón: {pattern}")
        return EXIT_CODE_ERRORS
    
    results = {
        "status": "success",
        "exit_code": 0,
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "pattern": pattern,
        "summary": {
            "files_processed": len(files),
            "files_success": 0,
            "files_warnings": 0,
            "files_errors": 0,
            "total_blocks": 0
        },
        "files": []
    }
    
    max_exit_code = EXIT_CODE_SUCCESS
    
    for md_file in files:
        file_result = process_single_file(md_file, ci_mode)
        results["files"].append(file_result)
        
        # Actualizar contadores
        if file_result["status"] == "success":
            results["summary"]["files_success"] += 1
        elif file_result["status"] == "warning":
            results["summary"]["files_warnings"] += 1
            max_exit_code = max(max_exit_code, EXIT_CODE_WARNINGS)
        elif file_result["status"] == "error":
            results["summary"]["files_errors"] += 1
            max_exit_code = max(max_exit_code, EXIT_CODE_ERRORS)
        elif file_result["status"] == "security_error":
            results["summary"]["files_errors"] += 1
            max_exit_code = EXIT_CODE_SECURITY_ERROR
        elif file_result["status"] == "internal_error":
            results["summary"]["files_errors"] += 1
            max_exit_code = EXIT_CODE_INTERNAL_ERROR
        
        results["summary"]["total_blocks"] += file_result.get("blocks", 0)
    
    results["exit_code"] = max_exit_code
    results["status"] = get_status_from_exit_code(max_exit_code)
    
    if ci_mode:
        print(json.dumps(results, indent=2))
    else:
        print_human_summary(results)
    
    return max_exit_code


def get_status_from_exit_code(code: int) -> str:
    """Convierte exit code a status string."""
    if code == EXIT_CODE_SUCCESS:
        return "success"
    elif code == EXIT_CODE_WARNINGS:
        return "warnings"
    elif code == EXIT_CODE_ERRORS:
        return "errors"
    elif code == EXIT_CODE_VALIDATION_FAILED:
        return "validation_failed"
    elif code == EXIT_CODE_SECURITY_ERROR:
        return "security_error"
    else:
        return "internal_error"


def print_human_summary(results: Dict):
    """Imprime resumen human-friendly (modo interactivo)."""
    print("\n" + "="*70)
    print(f"📊 RESUMEN BATCH")
    print("="*70)
    print(f"Patrón: {results['pattern']}")
    print(f"Archivos procesados: {results['summary']['files_processed']}")
    print(f"Estado: {results['status'].upper()}")
    print(f"Exit code: {results['exit_code']}")
    
    summary = results['summary']
    print(f"\n✅ Success: {summary['files_success']}")
    print(f"⚠️  Warnings: {summary['files_warnings']}")
    print(f"❌ Errors: {summary['files_errors']}")
    print(f"📦 Total bloques: {summary['total_blocks']}")
    
    # Mostrar archivos con errores
    error_files = [f for f in results['files'] if f['status'] in ['error', 'security_error', 'internal_error']]
    if error_files:
        print(f"\n❌ Archivos con errores:")
        for file_result in error_files:
            print(f"  - {file_result['source']}")
            for error in file_result.get('errors', []):
                print(f"      [{error.get('code', 'ERROR')}] {error['message']}")
    
    # Mostrar archivos con warnings
    warning_files = [f for f in results['files'] if f['status'] == 'warning']
    if warning_files:
        print(f"\n⚠️  Archivos con warnings:")
        for file_result in warning_files:
            print(f"  - {file_result['source']}")
            for warning in file_result.get('warnings', []):
                print(f"      {warning['message']}")
    
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description='YAML Pipeline Batch Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
    # Modo CI (JSON, sin colores)
    python3 yaml_pipeline_cli.py --batch "swarm/agents/**/*.md" --ci-mode
    
    # Modo interactivo (colores, emojis)
    python3 yaml_pipeline_cli.py --batch "swarm/agents/**/*.md"
    
Exit Codes:
    0 = Success (sin errores ni warnings)
    1 = Warnings
    2 = Errors
    3 = Validation failed
    4 = Security error
    5 = Internal error
        """
    )
    
    parser.add_argument(
        '--batch',
        required=True,
        help='Glob pattern (ej: swarm/agents/**/*.md)'
    )
    
    parser.add_argument(
        '--ci-mode',
        action='store_true',
        help='Modo CI (JSON output, no emojis)'
    )
    
    parser.add_argument(
        '--output-json',
        action='store_true',
        help='Alias para --ci-mode'
    )
    
    args = parser.parse_args()
    ci_mode = args.ci_mode or args.output_json
    
    try:
        exit_code = run_batch(args.batch, ci_mode)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        if ci_mode:
            print(json.dumps({"status": "interrupted", "exit_code": 130}))
        else:
            print("\n⚠️  Proceso interrumpido por usuario")
        sys.exit(130)
    except Exception as e:
        if ci_mode:
            print(json.dumps({
                "status": "internal_error",
                "exit_code": EXIT_CODE_INTERNAL_ERROR,
                "message": str(e)
            }))
        else:
            print(f"\n❌ Error interno: {e}")
        sys.exit(EXIT_CODE_INTERNAL_ERROR)


if __name__ == "__main__":
    main()
