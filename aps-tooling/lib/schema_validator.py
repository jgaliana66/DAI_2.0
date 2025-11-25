"""
Schema Validator - APS Tooling
===============================

Validador de schemas YAML contra aps_agent_schema_v1.yaml y otros schemas.
"""

import yaml
import jsonschema
from pathlib import Path
from typing import Dict, List, Optional, Union


class SchemaValidator:
    """
    Validador de archivos YAML contra schemas JSON Schema.
    
    Ejemplo:
        >>> validator = SchemaValidator()
        >>> errors = validator.validate_file('agent.yaml')
        >>> if errors:
        ...     print("❌ Errores:", errors)
    """
    
    def __init__(self, schema_path: Optional[Union[str, Path]] = None):
        """
        Inicializa el validador.
        
        Args:
            schema_path: Ruta al schema YAML. Si es None, usa aps_agent_schema_v1.yaml
        """
        if schema_path is None:
            # Ruta por defecto al schema de agentes
            self.schema_path = Path(__file__).parent.parent / 'schemas' / 'aps_agent_schema_v1.yaml'
        else:
            self.schema_path = Path(schema_path)
        
        self.schema: Optional[Dict] = None
    
    def load_schema(self) -> Dict:
        """
        Carga el schema desde el archivo.
        
        Returns:
            Diccionario con el schema
        
        Raises:
            FileNotFoundError: Si el schema no existe
            yaml.YAMLError: Si el schema es inválido
        """
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema no encontrado: {self.schema_path}")
        
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = yaml.safe_load(f)
        
        return self.schema
    
    def validate_data(self, data: Dict) -> List[Dict]:
        """
        Valida un diccionario contra el schema.
        
        Args:
            data: Datos a validar
        
        Returns:
            Lista de errores encontrados. Cada error es un diccionario con:
            - 'path': Ruta JSON al campo con error
            - 'message': Mensaje de error
            - 'validator': Tipo de validación que falló
        """
        if self.schema is None:
            self.load_schema()
        
        errors = []
        validator = jsonschema.Draft7Validator(self.schema)
        
        for error in validator.iter_errors(data):
            errors.append({
                'path': list(error.path),
                'message': error.message,
                'validator': error.validator,
                'schema_path': list(error.schema_path)
            })
        
        return errors
    
    def validate_file(self, filepath: Union[str, Path]) -> List[Dict]:
        """
        Valida un archivo YAML contra el schema.
        
        Args:
            filepath: Ruta al archivo YAML
        
        Returns:
            Lista de errores encontrados
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            yaml.YAMLError: Si el YAML es inválido
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self.validate_data(data)
    
    def format_error_message(self, error: Dict, include_path: bool = True) -> str:
        """
        Formatea un error para mostrar al usuario.
        
        Args:
            error: Diccionario de error de validate_data()
            include_path: Si True, incluye la ruta JSON
        
        Returns:
            Mensaje formateado
        """
        path_str = '.'.join(str(p) for p in error['path']) if error['path'] else 'root'
        
        if include_path:
            return f"[{path_str}] {error['message']}"
        else:
            return error['message']
    
    def validate_with_report(self, filepath: Union[str, Path]) -> Dict:
        """
        Valida un archivo y genera un reporte completo.
        
        Args:
            filepath: Ruta al archivo YAML
        
        Returns:
            {
                'valid': bool,
                'filepath': str,
                'error_count': int,
                'errors': List[Dict],
                'formatted_errors': List[str]
            }
        """
        filepath = Path(filepath)
        errors = self.validate_file(filepath)
        
        return {
            'valid': len(errors) == 0,
            'filepath': str(filepath),
            'error_count': len(errors),
            'errors': errors,
            'formatted_errors': [self.format_error_message(e) for e in errors]
        }
    
    def validate_batch(
        self,
        filepaths: List[Union[str, Path]],
        stop_on_error: bool = False
    ) -> List[Dict]:
        """
        Valida múltiples archivos.
        
        Args:
            filepaths: Lista de rutas a archivos YAML
            stop_on_error: Si True, detiene al primer error
        
        Returns:
            Lista de reportes (uno por archivo)
        """
        reports = []
        
        for filepath in filepaths:
            try:
                report = self.validate_with_report(filepath)
                reports.append(report)
                
                if stop_on_error and not report['valid']:
                    break
                    
            except Exception as e:
                reports.append({
                    'valid': False,
                    'filepath': str(filepath),
                    'error_count': 1,
                    'errors': [{'message': str(e)}],
                    'formatted_errors': [f"Error al procesar: {str(e)}"]
                })
                
                if stop_on_error:
                    break
        
        return reports
    
    def print_validation_report(self, report: Dict) -> None:
        """
        Imprime un reporte de validación de forma legible.
        
        Args:
            report: Reporte de validate_with_report()
        """
        filepath = report['filepath']
        
        if report['valid']:
            print(f"✅ {filepath}: VÁLIDO")
        else:
            print(f"❌ {filepath}: {report['error_count']} error(es)")
            for error_msg in report['formatted_errors']:
                print(f"   - {error_msg}")


class APSValidator(SchemaValidator):
    """
    Validador especializado para agentes APS v3.5.
    
    Además de validar contra el schema, verifica:
    - SIDs únicos globalmente
    - Componentes de SID en vocabulario
    - Referencias cruzadas entre bloques
    """
    
    def __init__(self):
        """Inicializa validador APS con schema de agentes."""
        super().__init__()
    
    def validate_sids_unique(self, data: Dict) -> List[str]:
        """
        Verifica que todos los SIDs sean únicos en el archivo.
        
        Args:
            data: Datos del YAML cargado
        
        Returns:
            Lista de SIDs duplicados
        """
        blocks = data.get('blocks', {})
        sids = []
        duplicates = []
        
        for block_id, block_data in blocks.items():
            sid = block_data.get('sid')
            if sid:
                if sid in sids:
                    duplicates.append(sid)
                else:
                    sids.append(sid)
        
        return duplicates
    
    def validate_sid_components(self, data: Dict) -> List[Dict]:
        """
        Verifica que los componentes de los SIDs estén en el vocabulario.
        
        Returns:
            Lista de errores (componentes no válidos)
        """
        from .vocabulary_loader import VocabularyLoader
        
        vocab = VocabularyLoader()
        errors = []
        blocks = data.get('blocks', {})
        
        for block_id, block_data in blocks.items():
            sid = block_data.get('sid')
            if not sid:
                continue
            
            parts = sid.split('.')
            if len(parts) != 3:
                errors.append({
                    'block_id': block_id,
                    'sid': sid,
                    'error': f'SID debe tener formato accion.relacion.nivel (tiene {len(parts)} partes)'
                })
                continue
            
            accion, relacion, nivel = parts
            
            # Validar con vocabulario
            result = vocab.validate_sid_components(accion, relacion, nivel)
            
            if result['errors']:
                errors.append({
                    'block_id': block_id,
                    'sid': sid,
                    'error': '; '.join(result['errors'])
                })
        
        return errors
    
    def validate_full(self, filepath: Union[str, Path]) -> Dict:
        """
        Validación completa APS: schema + SIDs + vocabulario.
        
        Returns:
            {
                'valid': bool,
                'filepath': str,
                'schema_errors': List[Dict],
                'duplicate_sids': List[str],
                'vocabulary_errors': List[Dict]
            }
        """
        filepath = Path(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        schema_errors = self.validate_data(data)
        duplicate_sids = self.validate_sids_unique(data)
        vocabulary_errors = self.validate_sid_components(data)
        
        return {
            'valid': len(schema_errors) == 0 and len(duplicate_sids) == 0 and len(vocabulary_errors) == 0,
            'filepath': str(filepath),
            'schema_errors': schema_errors,
            'duplicate_sids': duplicate_sids,
            'vocabulary_errors': vocabulary_errors
        }


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    print("🔍 Ejemplo de uso - SchemaValidator\n")
    
    # Ejemplo 1: Validación básica
    validator = SchemaValidator()
    
    # Crear archivo de ejemplo con error
    example_file = Path('example_invalid.yaml')
    with open(example_file, 'w') as f:
        f.write("""
# Archivo sin agent_name (error)
version: "3.5"
blocks:
  BLK-001:
    sid: verificar.control.guard
    content: Contenido
""")
    
    try:
        report = validator.validate_with_report(example_file)
        validator.print_validation_report(report)
    finally:
        example_file.unlink()
    
    print("\n" + "="*60 + "\n")
    
    # Ejemplo 2: Validación APS completa
    print("🔍 Validación APS completa\n")
    
    aps_validator = APSValidator()
    
    example_aps = Path('example_aps.yaml')
    with open(example_aps, 'w') as f:
        f.write("""
agent_name: "Test Agent"
version: "3.5"
blocks:
  BLK-001:
    sid: verificar.control.guard
    content: Verificar algo
  BLK-002:
    sid: capturar.input.task
    content: Capturar datos
""")
    
    try:
        aps_report = aps_validator.validate_full(example_aps)
        print(f"✅ Válido: {aps_report['valid']}")
        print(f"   Schema errors: {len(aps_report['schema_errors'])}")
        print(f"   SIDs duplicados: {len(aps_report['duplicate_sids'])}")
        print(f"   Errores vocabulario: {len(aps_report['vocabulary_errors'])}")
    finally:
        example_aps.unlink()
