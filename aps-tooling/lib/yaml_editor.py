"""
YAML Editor - APS Tooling
==========================

Editor YAML basado en AST para manipulación semántica segura.
Reemplaza el método DEPRECATED string-replace.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


class YAMLBlockEditor:
    """
    Editor de bloques YAML usando Abstract Syntax Tree (AST).
    
    ⚠️ REEMPLAZO OFICIAL DE: replace_string_in_file (DEPRECATED)
    
    Ventajas del método AST:
    - Preserva estructura YAML
    - Evita corrupciones por indentación
    - Manipulación semántica segura
    - Validación automática
    
    Ejemplo:
        >>> editor = YAMLBlockEditor('agent.yaml')
        >>> editor.load()
        >>> editor.set_field('blocks.BLK-001.sid', 'verificar.control.guard')
        >>> editor.save()
    """
    
    def __init__(self, filepath: Union[str, Path]):
        """
        Inicializa el editor para un archivo YAML.
        
        Args:
            filepath: Ruta al archivo YAML
        """
        self.filepath = Path(filepath)
        self.data: Optional[Dict] = None
        self.original_data: Optional[Dict] = None
    
    def load(self) -> Dict:
        """
        Carga el archivo YAML en memoria.
        
        Returns:
            Diccionario con el contenido YAML
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            yaml.YAMLError: Si el YAML es inválido
        """
        if not self.filepath.exists():
            raise FileNotFoundError(f"No existe: {self.filepath}")
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
            self.original_data = yaml.safe_load(open(self.filepath, 'r'))
        
        return self.data
    
    def save(self, backup: bool = True) -> None:
        """
        Guarda los cambios en el archivo YAML.
        
        Args:
            backup: Si True, crea un backup .bak antes de guardar
        """
        if self.data is None:
            raise RuntimeError("No hay datos cargados. Llama a load() primero.")
        
        # Crear backup si se solicita
        if backup and self.filepath.exists():
            backup_path = self.filepath.with_suffix(self.filepath.suffix + '.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.original_data, f, allow_unicode=True, sort_keys=False)
        
        # Guardar archivo
        with open(self.filepath, 'w', encoding='utf-8') as f:
            yaml.dump(self.data, f, allow_unicode=True, sort_keys=False, indent=2)
    
    def get_field(self, path: str) -> Any:
        """
        Obtiene un campo usando notación de punto.
        
        Args:
            path: Ruta al campo (ej: 'blocks.BLK-001.sid')
        
        Returns:
            Valor del campo, o None si no existe
        
        Ejemplo:
            >>> editor.get_field('blocks.BLK-001.sid')
            'verificar.control.guard'
        """
        if self.data is None:
            raise RuntimeError("No hay datos cargados. Llama a load() primero.")
        
        parts = path.split('.')
        current = self.data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def set_field(self, path: str, value: Any) -> None:
        """
        Establece un campo usando notación de punto.
        
        Args:
            path: Ruta al campo (ej: 'blocks.BLK-001.sid')
            value: Nuevo valor
        
        Ejemplo:
            >>> editor.set_field('blocks.BLK-001.sid', 'verificar.control.guard')
        """
        if self.data is None:
            raise RuntimeError("No hay datos cargados. Llama a load() primero.")
        
        parts = path.split('.')
        current = self.data
        
        # Navegar hasta el penúltimo elemento
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Establecer valor
        current[parts[-1]] = value
    
    def delete_field(self, path: str) -> bool:
        """
        Elimina un campo usando notación de punto.
        
        Args:
            path: Ruta al campo
        
        Returns:
            True si se eliminó, False si no existía
        """
        if self.data is None:
            raise RuntimeError("No hay datos cargados. Llama a load() primero.")
        
        parts = path.split('.')
        current = self.data
        
        # Navegar hasta el penúltimo elemento
        for part in parts[:-1]:
            if part not in current:
                return False
            current = current[part]
        
        # Eliminar si existe
        if parts[-1] in current:
            del current[parts[-1]]
            return True
        
        return False
    
    def add_block(self, block_id: str, block_data: Dict) -> None:
        """
        Añade un nuevo bloque a la sección 'blocks'.
        
        Args:
            block_id: ID del bloque (ej: 'BLK-001')
            block_data: Datos del bloque
        """
        if 'blocks' not in self.data:
            self.data['blocks'] = {}
        
        self.data['blocks'][block_id] = block_data
    
    def get_all_blocks(self) -> Dict[str, Dict]:
        """
        Obtiene todos los bloques.
        
        Returns:
            Diccionario con todos los bloques
        """
        return self.get_field('blocks') or {}
    
    def update_block_sid(self, block_id: str, new_sid: str) -> bool:
        """
        Actualiza el SID de un bloque específico.
        
        Args:
            block_id: ID del bloque
            new_sid: Nuevo SID
        
        Returns:
            True si se actualizó, False si el bloque no existe
        """
        path = f'blocks.{block_id}.sid'
        if self.get_field(f'blocks.{block_id}') is None:
            return False
        
        self.set_field(path, new_sid)
        return True
    
    def get_blocks_by_sid_pattern(self, pattern: str) -> List[str]:
        """
        Busca bloques que contengan un patrón en su SID.
        
        Args:
            pattern: Patrón a buscar (ej: 'verificar')
        
        Returns:
            Lista de IDs de bloques que coinciden
        """
        blocks = self.get_all_blocks()
        matching = []
        
        for block_id, block_data in blocks.items():
            sid = block_data.get('sid', '')
            if pattern in sid:
                matching.append(block_id)
        
        return matching
    
    def validate_structure(self) -> List[str]:
        """
        Valida la estructura básica del YAML.
        
        Returns:
            Lista de errores encontrados (vacía si es válido)
        """
        errors = []
        
        if not isinstance(self.data, dict):
            errors.append("El documento debe ser un objeto YAML")
            return errors
        
        # Validar campos requeridos para agentes
        if 'agent_name' not in self.data:
            errors.append("Falta campo requerido: 'agent_name'")
        
        if 'blocks' in self.data and not isinstance(self.data['blocks'], dict):
            errors.append("El campo 'blocks' debe ser un diccionario")
        
        return errors


class YAMLBatchEditor:
    """
    Editor por lotes para múltiples archivos YAML.
    
    Ejemplo:
        >>> batch = YAMLBatchEditor(['agent1.yaml', 'agent2.yaml'])
        >>> batch.apply_to_all(lambda editor: editor.set_field('version', '3.5'))
        >>> batch.save_all()
    """
    
    def __init__(self, filepaths: List[Union[str, Path]]):
        """
        Inicializa el editor por lotes.
        
        Args:
            filepaths: Lista de rutas a archivos YAML
        """
        self.editors = [YAMLBlockEditor(fp) for fp in filepaths]
        self.loaded = False
    
    def load_all(self) -> None:
        """Carga todos los archivos."""
        for editor in self.editors:
            editor.load()
        self.loaded = True
    
    def save_all(self, backup: bool = True) -> None:
        """Guarda todos los archivos."""
        for editor in self.editors:
            editor.save(backup=backup)
    
    def apply_to_all(self, func) -> None:
        """
        Aplica una función a todos los editores.
        
        Args:
            func: Función que recibe un YAMLBlockEditor
        """
        if not self.loaded:
            self.load_all()
        
        for editor in self.editors:
            func(editor)


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Ejemplo: Editar un archivo YAML
    print("📝 Ejemplo de uso - YAMLBlockEditor\n")
    
    # Crear archivo de ejemplo
    example_file = Path('example_agent.yaml')
    example_data = {
        'agent_name': 'Example Agent',
        'version': '3.5',
        'blocks': {
            'BLK-001': {
                'sid': 'antiguo.sid.valor',
                'content': 'Contenido del bloque'
            }
        }
    }
    
    with open(example_file, 'w') as f:
        yaml.dump(example_data, f)
    
    # Usar el editor
    editor = YAMLBlockEditor(example_file)
    editor.load()
    
    print(f"SID original: {editor.get_field('blocks.BLK-001.sid')}")
    
    editor.set_field('blocks.BLK-001.sid', 'verificar.control.guard')
    
    print(f"SID actualizado: {editor.get_field('blocks.BLK-001.sid')}")
    
    editor.save()
    
    print(f"✅ Archivo guardado con backup en {example_file}.bak")
    
    # Limpiar
    example_file.unlink()
    Path(str(example_file) + '.bak').unlink()
