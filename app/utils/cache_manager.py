"""
Sistema de caché para análisis de keywords
Permite guardar y recuperar análisis sin consumir créditos adicionales
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

class CacheManager:
    """Gestor de caché para análisis de keywords"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.analyses_dir = self.cache_dir / "analyses"
        self.analyses_dir.mkdir(exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Carga el índice de análisis guardados"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = []
    
    def _save_index(self):
        """Guarda el índice actualizado"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self, data: Dict) -> str:
        """Genera un ID único para el análisis"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Crear hash del contenido para evitar duplicados exactos
        content_str = json.dumps(data, sort_keys=True)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()[:8]
        
        return f"{timestamp}_{content_hash}"
    
    def save_analysis(
        self,
        keyword_universe: Dict[str, Any],
        processed_data: Any,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Guarda un análisis completo en caché
        
        Args:
            keyword_universe: Resultado del análisis de IA
            processed_data: DataFrame procesado (convertido a dict)
            metadata: Información adicional (nombre, descripción, etc.)
        
        Returns:
            ID del análisis guardado
        """
        
        # Generar ID
        analysis_id = self._generate_id(keyword_universe)
        
        # Preparar datos para guardar
        analysis_data = {
            'id': analysis_id,
            'timestamp': datetime.now().isoformat(),
            'keyword_universe': keyword_universe,
            'metadata': metadata,
            'stats': {
                'total_topics': len(keyword_universe.get('topics', [])),
                'total_keywords': metadata.get('total_keywords', 0),
                'total_volume': metadata.get('total_volume', 0),
                'provider': keyword_universe.get('provider', 'Unknown'),
                'model': keyword_universe.get('model', 'Unknown')
            }
        }
        
        # Guardar archivo del análisis
        analysis_file = self.analyses_dir / f"{analysis_id}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        # Guardar datos procesados por separado (puede ser grande)
        if processed_data is not None:
            data_file = self.analyses_dir / f"{analysis_id}_data.json"
            # Convertir DataFrame a dict si es necesario
            if hasattr(processed_data, 'to_dict'):
                processed_data = processed_data.to_dict('records')
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        # Actualizar índice
        index_entry = {
            'id': analysis_id,
            'timestamp': analysis_data['timestamp'],
            'name': metadata.get('name', 'Análisis sin nombre'),
            'description': metadata.get('description', ''),
            'stats': analysis_data['stats']
        }
        
        self.index.append(index_entry)
        self._save_index()
        
        return analysis_id
    
    def load_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Carga un análisis desde caché
        
        Args:
            analysis_id: ID del análisis a cargar
        
        Returns:
            Dict con el análisis completo o None si no existe
        """
        
        analysis_file = self.analyses_dir / f"{analysis_id}.json"
        
        if not analysis_file.exists():
            return None
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Cargar datos procesados si existen
        data_file = self.analyses_dir / f"{analysis_id}_data.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                processed_data = json.load(f)
                analysis_data['processed_data'] = processed_data
        
        return analysis_data
    
    def list_analyses(self, sort_by: str = 'timestamp', reverse: bool = True) -> List[Dict]:
        """
        Lista todos los análisis guardados
        
        Args:
            sort_by: Campo por el que ordenar ('timestamp', 'name', etc.)
            reverse: Si ordenar de forma descendente
        
        Returns:
            Lista de análisis con metadata
        """
        
        # Recargar índice por si hubo cambios
        self._load_index()
        
        # Ordenar
        sorted_index = sorted(
            self.index,
            key=lambda x: x.get(sort_by, ''),
            reverse=reverse
        )
        
        return sorted_index
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Elimina un análisis de la caché
        
        Args:
            analysis_id: ID del análisis a eliminar
        
        Returns:
            True si se eliminó correctamente
        """
        
        analysis_file = self.analyses_dir / f"{analysis_id}.json"
        data_file = self.analyses_dir / f"{analysis_id}_data.json"
        
        # Eliminar archivos
        deleted = False
        if analysis_file.exists():
            analysis_file.unlink()
            deleted = True
        
        if data_file.exists():
            data_file.unlink()
        
        # Actualizar índice
        self.index = [item for item in self.index if item['id'] != analysis_id]
        self._save_index()
        
        return deleted
    
    def get_cache_size(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el tamaño de la caché
        
        Returns:
            Dict con estadísticas de la caché
        """
        
        total_size = 0
        file_count = 0
        
        for file in self.analyses_dir.glob('*.json'):
            total_size += file.stat().st_size
            file_count += 1
        
        return {
            'total_analyses': len(self.index),
            'total_files': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
    
    def clear_cache(self) -> int:
        """
        Elimina toda la caché
        
        Returns:
            Número de análisis eliminados
        """
        
        count = 0
        for file in self.analyses_dir.glob('*.json'):
            file.unlink()
            count += 1
        
        self.index = []
        self._save_index()
        
        return count // 2  # Cada análisis tiene 2 archivos
    
    def search_analyses(self, query: str) -> List[Dict]:
        """
        Busca análisis por nombre o descripción
        
        Args:
            query: Texto a buscar
        
        Returns:
            Lista de análisis que coinciden
        """
        
        query_lower = query.lower()
        
        results = [
            item for item in self.index
            if query_lower in item.get('name', '').lower()
            or query_lower in item.get('description', '').lower()
        ]
        
        return results
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas agregadas de todos los análisis
        
        Returns:
            Dict con estadísticas globales
        """
        
        if not self.index:
            return {
                'total_analyses': 0,
                'total_keywords_analyzed': 0,
                'total_topics_created': 0,
                'providers_used': [],
                'date_range': None
            }
        
        total_keywords = sum(item['stats'].get('total_keywords', 0) for item in self.index)
        total_topics = sum(item['stats'].get('total_topics', 0) for item in self.index)
        
        providers = list(set(item['stats'].get('provider', 'Unknown') for item in self.index))
        
        timestamps = [item['timestamp'] for item in self.index]
        date_range = {
            'oldest': min(timestamps),
            'newest': max(timestamps)
        }
        
        return {
            'total_analyses': len(self.index),
            'total_keywords_analyzed': total_keywords,
            'total_topics_created': total_topics,
            'providers_used': providers,
            'date_range': date_range
        }
