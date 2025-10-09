import anthropic
import pandas as pd
import json
from typing import Dict, List, Any, Optional

class AnthropicService:
    """Servicio para interactuar con la API de Anthropic (Claude)"""
    
    # Modelos válidos de Claude
    VALID_MODELS = [
        "claude-sonnet-4-5-20250929",
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514"
    ]
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Inicializa el servicio de Anthropic
        
        Args:
            api_key: API key de Anthropic
            model: Modelo de Claude a utilizar
        
        Raises:
            ValueError: Si el modelo no es válido
        """
        if not api_key:
            raise ValueError("API key de Anthropic es requerida")
        
        if model not in self.VALID_MODELS:
            raise ValueError(f"Modelo '{model}' no válido. Modelos disponibles: {', '.join(self.VALID_MODELS)}")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = 16000
    
    def create_universe_prompt(
        self,
        df: pd.DataFrame,
        analysis_type: str = "Temática (Topics)",
        num_tiers: int = 3,
        custom_instructions: str = "",
        include_semantic: bool = True,
        include_trends: bool = True,
        include_gaps: bool = True
    ) -> str:
        """
        Crea el prompt optimizado para analizar keywords
        
        Args:
            df: DataFrame con las keywords
            analysis_type: Tipo de análisis a realizar
            num_tiers: Número de niveles de prioridad
            custom_instructions: Instrucciones adicionales personalizadas
            include_semantic: Si incluir análisis semántico
            include_trends: Si incluir detección de tendencias
            include_gaps: Si incluir detección de gaps
        
        Returns:
            Prompt completo para enviar a Claude
        """
        # Validar DataFrame
        if df.empty:
            raise ValueError("El DataFrame está vacío")
        
        if 'keyword' not in df.columns or 'volume' not in df.columns:
            raise ValueError("El DataFrame debe contener al menos las columnas 'keyword' y 'volume'")
        
        # Seleccionar solo columnas disponibles
        columns_to_use = ['keyword', 'volume']
        if 'traffic' in df.columns:
            columns_to_use.append('traffic')
        
        # Preparar datos de keywords (top por volumen)
        top_keywords = df.nlargest(min(1000, len(df)), 'volume')[columns_to_use].to_dict('records')
        
        # Crear resumen estadístico
        stats = {
            'total_keywords': len(df),
            'total_volume': int(df['volume'].sum()),
            'avg_volume': int(df['volume'].mean()),
            'unique_keywords': df['keyword'].nunique()
        }
        
        # Añadir stats de traffic si existe
        if 'traffic' in df.columns:
            stats['total_traffic'] = int(df['traffic'].sum())
            stats['avg_traffic'] = int(df['traffic'].mean())
        
        # Construir secciones opcionales ANTES del f-string
        gaps_section = ""
        if include_gaps:
            gaps_section = """,
    "gaps": [
        {
            "topic": "Nombre del gap/oportunidad",
            "volume": 50000,
            "description": "Por qué es una oportunidad",
            "difficulty": "medium"
        }
    ]"""
        
        trends_section = ""
        if include_trends:
            trends_section = """,
    "trends": [
        {
            "trend": "Nombre de la tendencia",
            "keywords": ["keyword1", "keyword2"],
            "insight": "Insight sobre la tendencia"
        }
    ]"""
        
        # Construir instrucciones adicionales
        extra_instructions = []
        instruction_number = 5
        
        if custom_instructions:
            extra_instructions.append(f"{instruction_number}. {custom_instructions}")
            instruction_number += 1
        
        if include_semantic:
            extra_instructions.append(
                f"{instruction_number}. Realiza análisis semántico profundo para entender intención real del usuario"
            )
            instruction_number += 1
        
        if include_trends:
            extra_instructions.append(
                f"{instruction_number}. Identifica tendencias emergentes y keywords en crecimiento"
            )
            instruction_number += 1
        
        if include_gaps:
            extra_instructions.append(
                f"{instruction_number}. Detecta gaps de contenido: topics con alto volumen pero poca cobertura competitiva"
            )
        
        # Formatear instrucciones adicionales
        extra_instructions_text = ""
        if extra_instructions:
            extra_instructions_text = "\n" + "\n".join(extra_instructions)
        
        # Formatear stats de traffic si existe
        traffic_stats = ""
        if 'total_traffic' in stats:
            traffic_stats = f"\n- Tráfico total: {stats['total_traffic']:,}\n- Tráfico promedio: {stats['avg_traffic']:,}"
        
        # Construir el prompt
        prompt = f"""Eres un experto en SEO y análisis de keywords. Tu tarea es crear un "Keyword Universe" completo y estratégico.

# DATOS PROPORCIONADOS
- Total de keywords: {stats['total_keywords']:,}
- Volumen total de búsqueda: {stats['total_volume']:,}
- Volumen promedio: {stats['avg_volume']:,}
- Keywords únicas: {stats['unique_keywords']:,}{traffic_stats}

# TIPO DE ANÁLISIS
{analysis_type}

# TU MISIÓN
Analiza las siguientes keywords y agrúpalas en {num_tiers} tiers (niveles) de prioridad:
- Tier 1: Alto volumen y máxima prioridad estratégica
- Tier {num_tiers}: Menor volumen pero oportunidades específicas

# FORMATO DE RESPUESTA (CRÍTICO - RESPONDER EN JSON)
Debes responder ÚNICAMENTE con un JSON válido con esta estructura exacta:

{{
    "summary": "Resumen ejecutivo del universo de keywords en 3-4 párrafos",
    "topics": [
        {{
            "topic": "Nombre del topic",
            "tier": 1,
            "keyword_count": 50,
            "volume": 150000,
            "traffic": 45000,
            "priority": "high",
            "description": "Descripción del topic y por qué es importante",
            "example_keywords": ["keyword1", "keyword2", "keyword3"]
        }}
    ]{gaps_section}{trends_section}
}}

# INSTRUCCIONES ESPECÍFICAS
1. Agrupa keywords por tema semántico y relevancia
2. Calcula el volumen total y número de keywords por topic
3. Asigna tiers basándote en: volumen, competencia y oportunidad estratégica
4. Identifica 5-10 topics principales por tier{extra_instructions_text}

# KEYWORDS A ANALIZAR (TOP {len(top_keywords)} POR VOLUMEN)
{json.dumps(top_keywords, indent=2, ensure_ascii=False)}

IMPORTANTE: Responde SOLO con el JSON, sin texto adicional antes o después."""

        return prompt
    
    def analyze_keywords(self, prompt: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Envía el prompt a Claude y procesa la respuesta
        
        Args:
            prompt: Prompt completo a enviar
            df: DataFrame original con las keywords
        
        Returns:
            Diccionario con los resultados del análisis
        
        Raises:
            Exception: Si hay error en la API o en el parsing
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extraer el contenido de la respuesta
            response_text = message.content[0].text
            
            # Intentar parsear el JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Si falla, intentar extraer el JSON del texto
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        raise ValueError(
                            f"No se pudo parsear JSON de la respuesta. "
                            f"Error original: {str(e)}\n"
                            f"Respuesta de Claude: {response_text[:500]}..."
                        )
                else:
                    raise ValueError(
                        f"No se encontró JSON válido en la respuesta de Claude.\n"
                        f"Respuesta: {response_text[:500]}..."
                    )
            
            # Validar estructura básica
            if 'topics' not in result:
                raise ValueError("La respuesta de Claude no contiene la clave 'topics'")
            
            # Validar y enriquecer resultados
            result = self._enrich_results(result, df)
            
            return result
            
        except anthropic.APIError as e:
            raise Exception(f"Error en la API de Anthropic: {str(e)}")
        except Exception as e:
            raise Exception(f"Error al analizar con Claude: {str(e)}")
    
    def _enrich_results(self, result: Dict, df: pd.DataFrame) -> Dict:
        """
        Enriquece los resultados con datos adicionales y validación
        
        Args:
            result: Resultados crudos de Claude
            df: DataFrame original con las keywords
        
        Returns:
            Resultados enriquecidos y validados
        """
        has_traffic_column = 'traffic' in df.columns
        
        if 'topics' in result:
            for i, topic in enumerate(result['topics']):
                try:
                    # Asegurar que todos los campos numéricos sean int/float
                    topic['keyword_count'] = int(topic.get('keyword_count', 0))
                    topic['volume'] = int(topic.get('volume', 0))
                    topic['tier'] = int(topic.get('tier', 1))
                    
                    # Manejar traffic: usar valor de Claude o estimar
                    if 'traffic' in topic and topic['traffic'] is not None:
                        topic['traffic'] = int(topic['traffic'])
                    elif has_traffic_column:
                        # Si no lo proporcionó Claude pero existe en el DF, estimar
                        topic['traffic'] = int(topic['volume'] * 0.3)
                    else:
                        # Si no existe la columna traffic, estimar basado en volumen
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
                    if 'priority' not in topic:
                        # Inferir prioridad basada en tier
                        if topic['tier'] == 1:
                            topic['priority'] = 'high'
                        elif topic['tier'] == 2:
                            topic['priority'] = 'medium'
                        else:
                            topic['priority'] = 'low'
                    
                    # Asegurar que example_keywords existe y es una lista
                    if 'example_keywords' not in topic:
                        topic['example_keywords'] = []
                    elif not isinstance(topic['example_keywords'], list):
                        topic['example_keywords'] = []
                    
                except (ValueError, KeyError, TypeError) as e:
                    print(f"Warning: Error procesando topic {i}: {str(e)}")
                    # Continuar con el siguiente topic en vez de fallar completamente
                    continue
        
        return result
    
    def get_topic_details(self, topic_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Obtiene las keywords específicas de un topic usando Claude
        
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
        
        # Limitar a 500 keywords para evitar exceder límites de tokens
        sample_df = df.nlargest(min(500, len(df)), 'volume')
        sample_data = sample_df[columns_to_use].to_json(orient='records', force_ascii=False)
        
        prompt = f"""Dado el topic "{topic_name}", identifica qué keywords del siguiente dataset pertenecen a este topic.

Responde SOLO con un JSON con esta estructura:
{{
    "keywords": ["keyword1", "keyword2", ...]
}}

Dataset:
{sample_data}

IMPORTANTE: Responde ÚNICAMENTE con el JSON, sin explicaciones adicionales."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Intentar parsear JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Intentar extraer JSON
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    print(f"Warning: No se pudo parsear respuesta para topic '{topic_name}'")
                    return pd.DataFrame()
            
            # Filtrar el dataframe
            matching_keywords = result.get('keywords', [])
            if not matching_keywords:
                return pd.DataFrame()
            
            return df[df['keyword'].isin(matching_keywords)]
            
        except anthropic.APIError as e:
            print(f"Error en API obteniendo detalles del topic '{topic_name}': {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error obteniendo detalles del topic '{topic_name}': {str(e)}")
            return pd.DataFrame()
    
    def validate_api_key(self) -> bool:
        """
        Valida que la API key funcione correctamente
        
        Returns:
            True si la API key es válida, False en caso contrario
        """
        try:
            # Hacer una llamada simple de prueba
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Hello"}
                ]
            )
            return True
        except anthropic.APIError:
            return False
        except Exception:
            return False
