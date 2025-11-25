"""
Confidence System - APS Tooling
================================

Sistema de confianza para inferencias semánticas (HIGH/MEDIUM/LOW)
"""

from enum import Enum
from typing import Dict, Optional, Tuple
from .vocabulary_loader import VocabularyLoader


class ConfidenceLevel(Enum):
    """Niveles de confianza para inferencias semánticas."""
    HIGH = "HIGH"      # Match exacto en vocabulario
    MEDIUM = "MEDIUM"  # Sinónimo reconocido o patrón heurístico
    LOW = "LOW"        # Inferencia semántica sin match


class ConfidenceSystem:
    """
    Sistema de confianza para clasificar inferencias semánticas.
    
    Ejemplo:
        >>> cs = ConfidenceSystem()
        >>> confidence, method, note = cs.evaluate_accion('verificar', content)
        >>> if confidence == ConfidenceLevel.LOW:
        ...     print(f"⚠️ Revisar: {note}")
    """
    
    def __init__(self, vocab_loader: Optional[VocabularyLoader] = None):
        """
        Inicializa el sistema de confianza.
        
        Args:
            vocab_loader: Instancia de VocabularyLoader.
                         Si es None, crea una nueva.
        """
        self.vocab = vocab_loader or VocabularyLoader()
    
    def evaluate_accion(
        self,
        accion: str,
        content: str
    ) -> Tuple[ConfidenceLevel, str, Optional[str]]:
        """
        Evalúa la confianza de una acción inferida.
        
        Args:
            accion: Acción inferida
            content: Contenido del bloque (para análisis contextual)
        
        Returns:
            (confidence_level, inference_method, note)
        """
        # 1. Match exacto en vocabulario → HIGH
        if self.vocab.is_accion_permitida(accion):
            return (
                ConfidenceLevel.HIGH,
                "vocabulary",
                None
            )
        
        # 2. Sinónimo reconocido → MEDIUM
        canonical = self.vocab.get_canonical_accion(accion)
        if canonical:
            return (
                ConfidenceLevel.MEDIUM,
                "synonym_mapping",
                f"Sinónimo de '{canonical}'. Sugerido usar forma canónica."
            )
        
        # 3. Heurística contextual → MEDIUM (si hay alta correlación)
        heuristic_confidence = self._evaluate_heuristic(accion, content)
        if heuristic_confidence:
            return (
                ConfidenceLevel.MEDIUM,
                "heuristic_pattern",
                f"Inferido por patrón: {heuristic_confidence}"
            )
        
        # 4. Inferencia semántica → LOW
        return (
            ConfidenceLevel.LOW,
            "semantic_similarity",
            f"No hay match en vocabulario. Revisar si '{accion}' es apropiado o usar término estándar."
        )
    
    def evaluate_relacion(
        self,
        relacion: str,
        content: str
    ) -> Tuple[ConfidenceLevel, str, Optional[str]]:
        """Evalúa la confianza de una relación inferida."""
        if self.vocab.is_relacion_permitida(relacion):
            return (ConfidenceLevel.HIGH, "vocabulary", None)
        
        # TODO: Implementar sinónimos para relaciones
        
        return (
            ConfidenceLevel.LOW,
            "semantic_similarity",
            f"Relación '{relacion}' no en vocabulario"
        )
    
    def evaluate_nivel(
        self,
        nivel: str,
        block_type: str
    ) -> Tuple[ConfidenceLevel, str, Optional[str]]:
        """Evalúa la confianza de un nivel inferido."""
        if self.vocab.is_nivel_permitido(nivel):
            return (ConfidenceLevel.HIGH, "vocabulary", None)
        
        return (
            ConfidenceLevel.LOW,
            "semantic_similarity",
            f"Nivel '{nivel}' no en vocabulario"
        )
    
    def evaluate_sid_complete(
        self,
        accion: str,
        relacion: str,
        nivel: str,
        content: str,
        block_type: str
    ) -> Dict:
        """
        Evaluación completa de confianza para un SID.
        
        Returns:
            {
                'overall_confidence': ConfidenceLevel,
                'accion': (confidence, method, note),
                'relacion': (confidence, method, note),
                'nivel': (confidence, method, note),
                'should_review': bool
            }
        """
        accion_eval = self.evaluate_accion(accion, content)
        relacion_eval = self.evaluate_relacion(relacion, content)
        nivel_eval = self.evaluate_nivel(nivel, block_type)
        
        # Confianza global = mínima de las tres
        confidences = [accion_eval[0], relacion_eval[0], nivel_eval[0]]
        overall = min(confidences, key=lambda c: c.value)
        
        return {
            'overall_confidence': overall,
            'accion': accion_eval,
            'relacion': relacion_eval,
            'nivel': nivel_eval,
            'should_review': overall == ConfidenceLevel.LOW
        }
    
    def _evaluate_heuristic(self, accion: str, content: str) -> Optional[str]:
        """
        Evalúa si hay correlación heurística fuerte.
        
        Returns:
            Descripción del patrón detectado, o None
        """
        content_lower = content.lower()
        
        # Patrones conocidos
        patterns = {
            'verificar': ['verificación', 'validar', 'comprobar', 'revisar'],
            'capturar': ['captura', 'extracción', 'obtener', 'recopilar'],
            'generar': ['generación', 'crear', 'producir', 'construir'],
            'prohibir': ['prohibición', 'no hacer', 'nunca', 'denegar'],
            'informar': ['informar', 'notificar', 'comunicar', 'reportar'],
        }
        
        if accion in patterns:
            for keyword in patterns[accion]:
                if keyword in content_lower:
                    return f"Contenido contiene '{keyword}'"
        
        return None
    
    def format_metadata(self, evaluation: Dict) -> Dict:
        """
        Formatea la evaluación para metadata YAML.
        
        Returns:
            {
                'confidence': 'HIGH'|'MEDIUM'|'LOW',
                'inference_method': str,
                'inference_note': str (optional)
            }
        """
        metadata = {
            'confidence': evaluation['overall_confidence'].value,
            'inference_method': evaluation['accion'][1]  # Tomar método de acción
        }
        
        # Añadir notas si hay
        notes = []
        for component in ['accion', 'relacion', 'nivel']:
            note = evaluation[component][2]
            if note:
                notes.append(f"{component}: {note}")
        
        if notes:
            metadata['inference_note'] = '; '.join(notes)
        
        return metadata


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    cs = ConfidenceSystem()
    
    # Ejemplo 1: Acción canónica (HIGH)
    conf, method, note = cs.evaluate_accion('verificar', 'Verificar el estado')
    print(f"✅ 'verificar': {conf.value} ({method})")
    
    # Ejemplo 2: Sinónimo (MEDIUM)
    conf, method, note = cs.evaluate_accion('chequear', 'Chequear el estado')
    print(f"⚠️  'chequear': {conf.value} ({method}) - {note}")
    
    # Ejemplo 3: Término nuevo (LOW)
    conf, method, note = cs.evaluate_accion('monitorizar', 'Monitorizar sistema')
    print(f"❌ 'monitorizar': {conf.value} ({method}) - {note}")
    
    # Ejemplo 4: Evaluación completa
    eval_result = cs.evaluate_sid_complete(
        accion='verificar',
        relacion='control.active_agent',
        nivel='guard',
        content='Verificar que el agente activo es correcto',
        block_type='BLK'
    )
    
    print(f"\n📊 Confianza global: {eval_result['overall_confidence'].value}")
    print(f"   ¿Requiere revisión? {'Sí' if eval_result['should_review'] else 'No'}")
