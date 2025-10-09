"""
Servicio para integración con OpenAI API con sistema de caché
"""

from openai import OpenAI, OpenAIError
import pandas as pd
import json
from typing import Dict, List, Any, Optional
import logging

# Importar cache manager
from app.utils.cache_manager import get_cache_manager
from config import CACHE_CONFIG, estimate_analysis_cost

logger = logging.getLogger(__name__)


class OpenAIService:
    """Servicio para interactuar con la API de OpenAI con caché inteligente"""
    
    # Modelos válidos de OpenAI
    VALID_MODELS = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Inicializa el servicio de OpenAI
        
        Args:
            api_key: API key de OpenAI
            model: Modelo de GPT a utilizar
        
        Raises:
            ValueError: Si el API key está vacío o el modelo no es válido
        """
        if not api_key:
            raise ValueError("API key de OpenAI es requerida")
        
        if model not in self.VALID_MODELS:
            logger.warning(f"Modelo '{model}' no está en la lista de modelos válidos. Intentando de todas formas...")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = 16000 if model in ["gpt-4o", "gpt-4-turbo"] else 4096
        
        # Cache manager
        self.cache_manager = get_cache_manager()
        self.cache_enabled = CACHE_CONFIG.get('enabled', True)
        
        logger.info(f"OpenAIService inicializado - Modelo: {model}, Caché: {self.cache_enabled}")
    
    def create_universe_prompt(
        self,
        df: pd.DataFrame,
        analysis_type: str = "Temática (Topics)",
        num_tiers: int = 3,
        custom_instructions: str = "",
        include_semantic: bool = True,
        include_trends: bool = True,
        include_gaps: bool = True
    ) -> List[Dict[str, str]]:
        """
        Crea los mensajes para OpenAI en formato chat
        
        Args:
            df: DataFrame con las keywords
            analysis_type: Tipo de análisis a realizar
            num_tiers: Número de niveles de prioridad
            custom_instructions: Instrucciones adicionales personalizadas
            include_semantic: Si incluir análisis semántico
            include_trends: Si incluir detección de tendencias
            include_gaps: Si incluir detección de gaps
        
        Returns:
            Lista de mensajes en formato chat de OpenAI
        
        Raises:
            ValueError: Si el DataFrame está vacío o no tiene las columnas necesarias
        """
        # Validar DataFrame
        if df.empty:
            raise ValueError("El DataFrame está vacío")
        
        if 'keyword' not in df.columns or 'volume' not in df.columns:
            raise ValueError("El DataFrame debe contener al menos las columnas 'keyword' y 'volume'")
        
        # Seleccionar columnas disponibles de forma segura
        columns_to_use = ['keyword', 'volume']
        has_traffic = 'traffic' in df.columns
        if has_traffic:
            columns_to_use.append('traffic')
        
        # Preparar datos
        sample_size = min(1000, len(df))
        top_keywords = df.nlargest(sample_size, 'volume')[columns_to_use].to_dict('records')
        
        # Crear resumen estadístico
        stats = {
            'total_keywords': len(df),
            'total_volume': int(df['volume'].sum()),
            'avg_volume': int(df['volume'].mean()),
            'unique_keywords': df['keyword'].nunique()
        }
        
        # Añadir stats de traffic si existe
        if has_traffic:
            stats['total_traffic'] = int(df['traffic'].sum())
            stats['avg_traffic'] = int(df['traffic'].mean())
        
        # Determinar tipo de análisis
        analysis_instructions = self._get_analysis_instructions(analysis_type)
        
        # Secciones opcionales
        gaps_section = ""
        if include_gaps:
            gaps_section = """,
    "gaps": [
        {
            "topic": "Nombre del gap/oportunidad",
            "volume": 50000,
            "keyword_count": 25,
            "description": "Por qué es una oportunidad",
            "difficulty": "low|medium|high"
        }
    ]"""
        
        trends_section = ""
        if include_trends:
            trends_section = """,
    "trends": [
        {
            "trend": "Nombre de la tendencia",
            "keywords": ["keyword1", "keyword2"],
            "total_volume": 50000,
            "insight": "Por qué es relevante"
        }
    ]"""
        
        # Construir instrucciones opcionales
        optional_instructions = []
        if include_semantic:
            optional_instructions.append(
                "IMPORTANTE: Realiza análisis semántico profundo para entender la intención real detrás de cada keyword."
            )
        if include_trends:
            optional_instructions.append(
                "IMPORTANTE: Identifica tendencias emergentes y keywords en crecimiento."
            )
        if include_gaps:
            optional_instructions.append(
                "IMPORTANTE: Detecta gaps de contenido - topics con alto volumen pero poca cobertura competitiva."
            )
        
        optional_instructions_text = "\n".join(optional_instructions) if optional_instructions else ""
        
        # Formatear custom instructions
        custom_instructions_text = f"\n{custom_instructions}" if custom_instructions else ""
        
        # Formatear stats de traffic
        traffic_stats_text = ""
        if has_traffic:
            traffic_stats_text = f"\n- Tráfico total: {stats['total_traffic']:,}\n- Tráfico promedio: {stats['avg_traffic']:,}"
        
        system_message = """Eres un experto en SEO y análisis estratégico de keywords. 
Tu especialidad es identificar patrones, oportunidades y crear estrategias data-driven.
Siempre respondes con JSON válido y análisis profundos."""
        
        user_message = f"""Analiza las siguientes keywords y crea un "Keyword Universe" completo.

# CONTEXTO
- Total keywords: {stats['total_keywords']:,}
- Volumen total: {stats['total_volume']:,}
- Volumen promedio: {stats['avg_volume']:,}
- Keywords únicas: {stats['unique_keywords']:,}{traffic_stats_text}

# TIPO DE ANÁLISIS
{analysis_type}

{analysis_instructions}

# TU TAREA
Crea un análisis con {num_tiers} tiers (niveles) de prioridad:
- Tier 1: Alto volumen y máxima prioridad estratégica
- Tier {num_tiers}: Menor volumen pero oportunidades específicas{custom_instructions_text}

{optional_instructions_text}

# FORMATO DE RESPUESTA (CRÍTICO - RESPONDER SOLO CON JSON)
Responde ÚNICAMENTE con un JSON válido con esta estructura:

{{
    "summary": "Resumen ejecutivo del análisis en 3-4 párrafos explicando hallazgos clave, oportunidades principales y recomendaciones estratégicas",
    "topics": [
        {{
            "topic": "Nombre descriptivo del topic",
            "tier": 1,
            "keyword_count": 50,
            "volume": 150000,
            "traffic": 45000,
            "priority": "high|medium|low",
            "description": "Descripción detallada: por qué es importante, qué representa, estrategia recomendada",
            "example_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
        }}
    ]{gaps_section}{trends_section}
}}

# KEYWORDS A ANALIZAR (TOP {len(top_keywords)})
{json.dumps(top_keywords, indent=2, ensure_ascii=False)}

CRÍTICO: Responde SOLO con el JSON válido, sin texto adicional antes o después."""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    def _get_analysis_instructions(self, analysis_type: str) -> str:
        """
        Retorna instrucciones específicas según el tipo de análisis
        
        Args:
            analysis_type: Tipo de análisis solicitado
        
        Returns:
            Instrucciones específicas para el tipo de análisis
        """
        instructions = {
            "Temática (Topics)": """
Agrupa keywords por temas semánticos coherentes. Cada topic debe representar 
un área temática clara. Busca patrones de co-ocurrencia y relevancia semántica.""",
            
            "Intención de búsqueda": """
Clasifica keywords según la intención del usuario:
- Informacional: Busca aprender (cómo, qué es, guía)
- Navegacional: Busca un sitio específico (login, descargar, marca)
- Comercial: Investiga antes de comprar (mejor, review, comparar)
- Transaccional: Listo para actuar (comprar, precio, gratis)

Dentro de cada intención, agrupa por sub-temas.""",
            
            "Funnel de conversión": """
Clasifica keywords según la etapa del funnel:
- TOFU (Top): Awareness - descubrimiento del problema
- MOFU (Middle): Consideration - evaluación de soluciones  
- BOFU (Bottom): Decision - listo para decidir

Asigna tiers considerando el valor estratégico de cada etapa."""
        }
        
        return instructions.get(analysis_type, instructions["Temática (Topics)"])
    
    def analyze_keywords(
        self,
        messages: List[Dict[str, str]],
        df: pd.DataFrame,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Envía el prompt a OpenAI y procesa la respuesta con sistema de caché
        
        Args:
            messages: Mensajes en formato chat
            df: DataFrame con keywords
            use_cache: Si usar el sistema de caché
            **kwargs: Parámetros adicionales del análisis (analysis_type, num_tiers, etc.)
        
        Returns:
            Diccionario con los resultados del análisis
        
        Raises:
            Exception: Si hay error en la API o en el procesamiento
        """
        # Validar DataFrame
        if df.empty:
            raise ValueError("El DataFrame está vacío")
        
        # Generar hash para caché
        cache_hash = None
        if self.cache_enabled and use_cache:
            try:
                cache_hash = self.cache_manager.generate_hash(
                    df=df,
                    analysis_type=kwargs.get('analysis_type', 'Temática (Topics)'),
                    num_tiers=kwargs.get('num_tiers', 3),
                    custom_instructions=kwargs.get('custom_instructions', ''),
                    include_semantic=kwargs.get('include_semantic', True),
                    include_trends=kwargs.get('include_trends', True),
                    include_gaps=kwargs.get('include_gaps', True)
                )
                
                logger.info(f"Cache hash generado: {cache_hash}")
                
                # Intentar recuperar del caché
                ttl_hours = CACHE_CONFIG.get('default_ttl_hours', 24)
                cached_result = self.cache_manager.get_cached_analysis(cache_hash, ttl_hours)
                
                if cached_result is not None:
                    cache_metadata = cached_result.get('_cache_metadata', {})
                    saved_cost = cache_metadata.get('cost', 0)
                    logger.info(f"✅ Resultado recuperado del caché (ahorro de ${saved_cost:.4f})")
                    return cached_result
                
                logger.info("❌ Cache miss - Realizando análisis nuevo")
            except Exception as e:
                logger.warning(f"Error en sistema de caché: {str(e)}. Continuando sin caché...")
                cache_hash = None
        
        # Estimar costo
        try:
            cost_estimate = estimate_analysis_cost(self.model, len(df))
            logger.info(f"Costo estimado: ${cost_estimate.get('cost', 0):.4f}")
        except Exception as e:
            logger.warning(f"No se pudo estimar costo: {str(e)}")
            cost_estimate = {'cost': 0, 'input_tokens': 0, 'output_tokens': 0}
        
        try:
            # Llamada real a la API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Extraer contenido
            response_text = response.choices[0].message.content
            
            # Parsear JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Intentar extraer JSON del texto
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        raise ValueError(
                            f"No se pudo parsear JSON de la respuesta. "
                            f"Error: {str(e)}\n"
                            f"Respuesta: {response_text[:500]}..."
                        )
                else:
                    raise ValueError(
                        f"No se encontró JSON válido en la respuesta.\n"
                        f"Respuesta: {response_text[:500]}..."
                    )
            
            # Validar estructura básica
            if 'topics' not in result:
                raise ValueError("La respuesta no contiene la clave 'topics'")
            
            # Enriquecer resultados
            result = self._enrich_results(result, df)
            
            # Guardar en caché si está habilitado
            if self.cache_enabled and use_cache and cache_hash:
                try:
                    saved = self.cache_manager.save_analysis(
                        cache_hash=cache_hash,
                        result=result,
                        provider='OpenAI',
                        model=self.model,
                        estimated_cost=cost_estimate.get('cost', 0),
                        estimated_credits=cost_estimate.get('input_tokens', 0) + cost_estimate.get('output_tokens', 0),
                        parameters=kwargs
                    )
                    
                    if saved:
                        logger.info(f"💾 Análisis guardado en caché: {cache_hash}")
                except Exception as e:
                    logger.warning(f"No se pudo guardar en caché: {str(e)}")
            
            return result
            
        except OpenAIError as e:
            logger.error(f"Error en la API de OpenAI: {str(e)}")
            raise Exception(f"Error en la API de OpenAI: {str(e)}")
        except Exception as e:
            logger.error(f"Error al analizar con OpenAI: {str(e)}")
            raise Exception(f"Error al analizar con OpenAI: {str(e)}")
    
    def _enrich_results(self, result: Dict, df: pd.DataFrame) -> Dict:
        """
        Enriquece los resultados con datos adicionales y validación
        
        Args:
            result: Resultados crudos de OpenAI
            df: DataFrame original con las keywords
        
        Returns:
            Resultados enriquecidos y validados
        """
        has_traffic = 'traffic' in df.columns
        
        if 'topics' in result:
            for i, topic in enumerate(result['topics']):
                try:
                    # Asegurar tipos correctos
                    topic['keyword_count'] = int(topic.get('keyword_count', 0))
                    topic['volume'] = int(topic.get('volume', 0))
                    topic['tier'] = int(topic.get('tier', 1))
                    
                    # Manejar traffic de forma segura
                    if 'traffic' in topic and topic['traffic'] is not None:
                        topic['traffic'] = int(topic['traffic'])
                    elif has_traffic:
                        # Estimar si no lo proporcionó pero existe en el DF
                        topic['traffic'] = int(topic['volume'] * 0.3)
                    else:
                        # Estimar basado en volumen
                        topic['traffic'] = int(topic['volume'] * 0.3)
                    
                    # Calcular métricas adicionales
                    if topic['keyword_count'] > 0:
                        topic['avg_volume_per_keyword'] = round(
                            topic['volume'] / topic['keyword_count'],
                            2
                        )
                    else:
                        topic['avg_volume_per_keyword'] = 0
                    
                    # Asegurar que priority existe
                    if 'priority' not in topic or not topic['priority']:
                        # Inferir prioridad del tier
                        if topic['tier'] == 1:
                            topic['priority'] = 'high'
                        elif topic['tier'] == 2:
                            topic['priority'] = 'medium'
                        else:
                            topic['priority'] = 'low'
                    
                    # Asegurar que example_keywords existe y es lista
                    if 'example_keywords' not in topic:
                        topic['example_keywords'] = []
                    elif not isinstance(topic['example_keywords'], list):
                        topic['example_keywords'] = []
                    
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Error procesando topic {i}: {str(e)}")
                    continue
        
        return result
    
    def compare_with_claude(
        self, 
        claude_result: Dict[str, Any], 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Compara y valida resultados de Claude con análisis de OpenAI
        
        Args:
            claude_result: Resultado del análisis de Claude
            df: DataFrame con las keywords
        
        Returns:
            Análisis comparativo y recomendaciones
        """
        if df.empty:
            return {
                "validation": "No se pudo realizar la comparación: DataFrame vacío",
                "missing_topics": [],
                "improvements": [],
                "error": "DataFrame vacío"
            }
        
        # Preparar datos de forma segura
        columns_to_use = ['keyword', 'volume']
        if 'traffic' in df.columns:
            columns_to_use.append('traffic')
        
        sample_data = df.nlargest(min(200, len(df)), 'volume')[columns_to_use].to_dict('records')
        
        messages = [
            {
                "role": "system",
                "content": """Eres un experto en SEO que valida y complementa análisis de keywords.
Tu rol es identificar fortalezas, debilidades y oportunidades perdidas en análisis existentes."""
            },
            {
                "role": "user",
                "content": f"""Revisa este análisis de keywords y proporciona:

1. **Validación general**: ¿Es completo y preciso el análisis?
2. **Topics perdidos**: ¿Hay temas importantes que no se identificaron?
3. **Mejoras sugeridas**: ¿Cómo mejorar la clasificación o priorización?

ANÁLISIS A REVISAR:
{json.dumps(claude_result.get('topics', [])[:20], indent=2, ensure_ascii=False)}

KEYWORDS DISPONIBLES (muestra):
{json.dumps(sample_data, indent=2, ensure_ascii=False)}

Responde en JSON:
{{
    "validation": "Evaluación general del análisis (2-3 párrafos)",
    "missing_topics": ["topic1 no identificado", "topic2 no identificado"],
    "improvements": ["mejora sugerida 1", "mejora sugerida 2"],
    "agreement_score": 85,
    "key_differences": "Principales diferencias con tu análisis"
}}

IMPORTANTE: Responde ÚNICAMENTE con el JSON, sin texto adicional."""
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except OpenAIError as e:
            logger.error(f"Error en API durante comparación: {str(e)}")
            return {
                "validation": "No se pudo completar la validación cruzada (error de API)",
                "missing_topics": [],
                "improvements": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error en comparación: {str(e)}")
            return {
                "validation": "No se pudo completar la validación cruzada",
                "missing_topics": [],
                "improvements": [],
                "error": str(e)
            }
    
    def get_topic_details(self, topic_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica keywords específicas que pertenecen a un topic
        
        Args:
            topic_name: Nombre del topic
            df: DataFrame con todas las keywords
        
        Returns:
            DataFrame filtrado con las keywords del topic
        """
        if df.empty:
            return pd.DataFrame()
        
        # Preparar datos de forma segura
        columns_to_use = ['keyword', 'volume']
        if 'traffic' in df.columns:
            columns_to_use.append('traffic')
        
        sample_size = min(500, len(df))
        sample_keywords = df.nlargest(sample_size, 'volume')[columns_to_use].to_dict('records')
        
        messages = [
            {
                "role": "system",
                "content": "Eres un experto en clasificación semántica de keywords."
            },
            {
                "role": "user",
                "content": f"""Dado el topic "{topic_name}", identifica qué keywords del siguiente 
dataset pertenecen a este topic.

Responde SOLO con JSON:
{{
    "keywords": ["keyword1", "keyword2", ...]
}}

Dataset:
{json.dumps(sample_keywords, indent=2, ensure_ascii=False)}

IMPORTANTE: Responde ÚNICAMENTE con el JSON, sin explicaciones adicionales."""
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            matching_keywords = result.get('keywords', [])
            
            if not matching_keywords:
                return pd.DataFrame()
            
            return df[df['keyword'].isin(matching_keywords)]
            
        except OpenAIError as e:
            logger.error(f"Error en API obteniendo detalles del topic '{topic_name}': {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error obteniendo detalles del topic '{topic_name}': {str(e)}")
            return pd.DataFrame()
    
    def validate_api_key(self) -> bool:
        """
        Valida que la API key funcione correctamente
        
        Returns:
            True si la API key es válida, False en caso contrario
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )
            return True
        except OpenAIError:
            return False
        except Exception:
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema de caché
        
        Returns:
            Diccionario con estadísticas del caché
        """
        if self.cache_manager:
            return self.cache_manager.get_cache_stats()
        return {
            "enabled": False,
            "message": "Cache no disponible"
        }
    
    def clear_cache(self, older_than_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Limpia el caché
        
        Args:
            older_than_hours: Si se especifica, solo limpia análisis más antiguos que estas horas
        
        Returns:
            Resultado de la operación de limpieza
        """
        if self.cache_manager:
            return self.cache_manager.clear_cache(older_than_hours)
        return {
            "success": False,
            "message": "Cache no disponible"
        }
