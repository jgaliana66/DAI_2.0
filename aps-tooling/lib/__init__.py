"""
APS Tooling Library
===================

Biblioteca compartida para el sistema de validación APS v3.5.

Módulos:
- vocabulary_loader: Carga vocabulario centralizado
- confidence_system: Sistema de confianza HIGH/MEDIUM/LOW
- yaml_editor: Manipulación robusta de YAML mediante AST
- schema_validator: Validación contra schemas formales
"""

__version__ = "2.0.0"
__aps_version__ = "3.5"

from .vocabulary_loader import VocabularyLoader
from .confidence_system import ConfidenceSystem, ConfidenceLevel
from .yaml_editor import YAMLBlockEditor, YAMLBatchEditor

# SchemaValidator requiere jsonschema (opcional)
try:
    from .schema_validator import SchemaValidator
except ImportError:
    SchemaValidator = None

__all__ = [
    'VocabularyLoader',
    'ConfidenceSystem',
    'YAMLBlockEditor',
    'SchemaValidator',
]
