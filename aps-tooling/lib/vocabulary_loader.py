"""
Vocabulary Loader - APS Tooling
================================

Carga y gestiona el vocabulario centralizado de SIDs desde sid_vocabulary_v1.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional


class VocabularyLoader:
    """
    Carga y proporciona acceso al vocabulario centralizado de SIDs.
    
    Ejemplo:
        >>> vocab = VocabularyLoader()
        >>> acciones = vocab.get_acciones_permitidas()
        >>> if vocab.is_accion_deprecated('calcular'):
        ...     replacement = vocab.get_replacement('calcular')
    """
    
    def __init__(self, vocab_path: Optional[str] = None):
        """
        Inicializa el cargador de vocabulario.
        
        Args:
            vocab_path: Ruta al archivo sid_vocabulary_v1.yaml
                       Si es None, usa la ruta por defecto
        """
        if vocab_path is None:
            # Ruta por defecto relativa al módulo
            lib_dir = Path(__file__).parent
            vocab_path = lib_dir.parent / 'schemas' / 'sid_vocabulary_v1.yaml'
        
        self.vocab_path = Path(vocab_path)
        self._vocab = None
        self._load()
    
    def _load(self):
        """Carga el vocabulario desde el archivo YAML."""
        if not self.vocab_path.exists():
            raise FileNotFoundError(
                f"Vocabulario no encontrado: {self.vocab_path}\n"
                f"Asegúrate de que sid_vocabulary_v1.yaml existe en aps-tooling/schemas/"
            )
        
        with open(self.vocab_path, 'r', encoding='utf-8') as f:
            self._vocab = yaml.safe_load(f)
    
    @property
    def version(self) -> str:
        """Versión del vocabulario."""
        return self._vocab.get('version', 'unknown')
    
    @property
    def aps_version(self) -> str:
        """Versión APS asociada."""
        return self._vocab.get('aps_version', 'unknown')
    
    # =========================================================================
    # ACCIONES
    # =========================================================================
    
    def get_acciones_permitidas(self) -> List[str]:
        """Retorna lista de acciones permitidas."""
        return self._vocab.get('acciones', {}).get('permitidas', [])
    
    def get_acciones_deprecated(self) -> List[str]:
        """Retorna lista de acciones deprecated."""
        return self._vocab.get('acciones', {}).get('deprecated', [])
    
    def is_accion_permitida(self, accion: str) -> bool:
        """Verifica si una acción está permitida."""
        return accion in self.get_acciones_permitidas()
    
    def is_accion_deprecated(self, accion: str) -> bool:
        """Verifica si una acción está deprecated."""
        return accion in self.get_acciones_deprecated()
    
    # =========================================================================
    # RELACIONES
    # =========================================================================
    
    def get_relaciones_permitidas(self) -> List[str]:
        """Retorna lista de relaciones permitidas."""
        return self._vocab.get('relaciones', {}).get('permitidas', [])
    
    def get_relaciones_deprecated(self) -> List[str]:
        """Retorna lista de relaciones deprecated."""
        return self._vocab.get('relaciones', {}).get('deprecated', [])
    
    def is_relacion_permitida(self, relacion: str) -> bool:
        """Verifica si una relación está permitida."""
        return relacion in self.get_relaciones_permitidas()
    
    def is_relacion_deprecated(self, relacion: str) -> bool:
        """Verifica si una relación está deprecated."""
        return relacion in self.get_relaciones_deprecated()
    
    # =========================================================================
    # NIVELES
    # =========================================================================
    
    def get_niveles_permitidos(self) -> List[str]:
        """Retorna lista de niveles permitidos."""
        return self._vocab.get('niveles', {}).get('permitidas', [])
    
    def get_niveles_deprecated(self) -> List[str]:
        """Retorna lista de niveles deprecated."""
        return self._vocab.get('niveles', {}).get('deprecated', [])
    
    def is_nivel_permitido(self, nivel: str) -> bool:
        """Verifica si un nivel está permitido."""
        return nivel in self.get_niveles_permitidos()
    
    def is_nivel_deprecated(self, nivel: str) -> bool:
        """Verifica si un nivel está deprecated."""
        return nivel in self.get_niveles_deprecated()
    
    # =========================================================================
    # SINÓNIMOS
    # =========================================================================
    
    def get_sinonimos_accion(self, accion: str) -> List[str]:
        """
        Retorna sinónimos de una acción.
        
        Returns:
            Lista de sinónimos, o lista vacía si no hay.
        """
        sinonimos = self._vocab.get('sinonimos', {}).get('acciones', {})
        for canonical, variants in sinonimos.items():
            if accion == canonical or accion in variants:
                return [canonical] + variants
        return []
    
    def get_canonical_accion(self, accion: str) -> Optional[str]:
        """
        Retorna la forma canónica de una acción (si es sinónimo).
        
        Returns:
            Acción canónica, o None si no es sinónimo.
        """
        sinonimos = self._vocab.get('sinonimos', {}).get('acciones', {})
        for canonical, variants in sinonimos.items():
            if accion in variants:
                return canonical
        return None
    
    # =========================================================================
    # VALIDACIÓN INTEGRAL
    # =========================================================================
    
    def validate_sid_components(self, accion: str, relacion: str, nivel: str) -> Dict:
        """
        Valida todos los componentes de un SID.
        
        Returns:
            {
                'valid': bool,
                'warnings': [str],
                'errors': [str],
                'suggestions': [str]
            }
        """
        result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # Validar acción
        if self.is_accion_deprecated(accion):
            result['warnings'].append(f"Acción '{accion}' está DEPRECATED")
            result['valid'] = False
            # TODO: Buscar replacement en metadata
        elif not self.is_accion_permitida(accion):
            canonical = self.get_canonical_accion(accion)
            if canonical:
                result['warnings'].append(
                    f"Acción '{accion}' es sinónimo de '{canonical}'"
                )
                result['suggestions'].append(f"Usar '{canonical}' para consistencia")
            else:
                result['errors'].append(
                    f"Acción '{accion}' no está en vocabulario (término nuevo?)"
                )
                result['valid'] = False
        
        # Validar relación
        if self.is_relacion_deprecated(relacion):
            result['warnings'].append(f"Relación '{relacion}' está DEPRECATED")
            result['valid'] = False
        elif not self.is_relacion_permitida(relacion):
            result['errors'].append(
                f"Relación '{relacion}' no está en vocabulario"
            )
            result['valid'] = False
        
        # Validar nivel
        if self.is_nivel_deprecated(nivel):
            result['warnings'].append(f"Nivel '{nivel}' está DEPRECATED")
            result['valid'] = False
        elif not self.is_nivel_permitido(nivel):
            result['errors'].append(f"Nivel '{nivel}' no está en vocabulario")
            result['valid'] = False
        
        return result
    
    def get_all_vocabulary(self) -> Dict:
        """Retorna el vocabulario completo (para debugging)."""
        return self._vocab


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Cargar vocabulario
    vocab = VocabularyLoader()
    
    print(f"📚 Vocabulario v{vocab.version} (APS v{vocab.aps_version})")
    print(f"\n✅ Acciones permitidas: {len(vocab.get_acciones_permitidas())}")
    print(f"✅ Relaciones permitidas: {len(vocab.get_relaciones_permitidas())}")
    print(f"✅ Niveles permitidos: {len(vocab.get_niveles_permitidos())}")
    
    # Ejemplo: validar componentes SID
    result = vocab.validate_sid_components(
        accion='verificar',
        relacion='control.active_agent',
        nivel='guard'
    )
    
    if result['valid']:
        print("\n✅ SID válido")
    else:
        print("\n❌ SID con problemas:")
        for error in result['errors']:
            print(f"  ERROR: {error}")
        for warning in result['warnings']:
            print(f"  WARNING: {warning}")
