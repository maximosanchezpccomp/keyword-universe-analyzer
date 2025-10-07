import anthropic
import pandas as pd
import json
from typing import Dict, List, Any

class AnthropicService:
    """Servicio para interactuar con la API de Anthropic (Claude)"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
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
        """Crea el prompt optimizado para analizar keywords"""
        
        # Seleccionar solo columnas disponibles
        columns_to_use = ['keyword', 'volume']
        if 'traffic' in df.columns:
            columns_to_use.append('traffic')
        
        # Preparar datos de keywords (top por volumen)
        top_keywords = df.nlargest(1000, 'volume')[columns_to_use].to_dict('records')
        
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
        
        # ARREGLO: Construir secciones opcionales ANTES del f-string
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
        
        # Instrucciones adicionales
        extra_instructions = ""
        if custom_instructions:
            extra_instructions = f"\n5. {custom_instructions}"
        
        if include_semantic:
            extra_instructions += "\n6. Realiza análisis semántico profundo para entender intención real del usuario"
        
        if include_trends:
            extra_instructions += "\n7. Identifica tendencias emergentes y keywords en crecimiento"
        
        if include_gaps:
            extra_instructions += "\n8. Detecta gaps de contenido: topics con alto volumen pero poca cobertura competitiva"
        
        # Formatear stats de traffic si existe
        traffic_stats = ""
        if 'total_traffic' in stats:
            traffic_stats = f"\n- Tráfico total: {stats['total_traffic']:,}"
        
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
4. Identifica 5-10 topics principales por tier{extra_instructions}

# KEYWORDS A ANALIZAR (TOP 1000 POR VOLUMEN)
{json.dumps(top_keywords[:1000], indent=2)}

IMPORTANTE: Responde SOLO con el JSON, sin texto adicional antes o después."""

        return prompt
    
    def analyze_keywords(self, prompt: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Envía el prompt a Claude y procesa la respuesta"""
        
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
            except json.JSONDecodeError:
                # Si falla, intentar extraer el JSON del texto
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No se pudo extraer JSON válido de la respuesta")
            
            # Validar y enriquecer resultados
            result = self._enrich_results(result, df)
            
            return result
            
        except Exception as e:
            raise Exception(f"Error al analizar con Claude: {str(e)}")
    
    def _enrich_results(self, result: Dict, df: pd.DataFrame) -> Dict:
        """Enriquece los resultados con datos adicionales"""
        
        if 'topics' in result:
            for topic in result['topics']:
                # Asegurar que todos los campos numéricos sean int/float
                topic['keyword_count'] = int(topic.get('keyword_count', 0))
                topic['volume'] = int(topic.get('volume', 0))
                
                # Traffic puede no existir si la columna no estaba en el DF original
                if 'traffic' not in topic:
                    # Estimar basado en volumen
                    topic['traffic'] = int(topic['volume'] * 0.3)
                else:
                    topic['traffic'] = int(topic.get('traffic', 0))
                
                # Calcular métricas adicionales
                if topic['keyword_count'] > 0:
                    topic['avg_volume_per_keyword'] = topic['volume'] / topic['keyword_count']
                else:
                    topic['avg_volume_per_keyword'] = 0
        
        return result
    
    def get_topic_details(self, topic_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Obtiene las keywords específicas de un topic usando Claude"""
        
        # Preparar datos de forma segura
        columns_to_use = ['keyword', 'volume']
        if 'traffic' in df.columns:
            columns_to_use.append('traffic')
        
        sample_data = df[columns_to_use].head(500).to_json(orient='records')
        
        prompt = f"""Dado el topic "{topic_name}", identifica qué keywords del siguiente dataset pertenecen a este topic.

Responde SOLO con un JSON con esta estructura:
{{
    "keywords": ["keyword1", "keyword2", ...]
}}

Dataset:
{sample_data}
"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            result = json.loads(response_text)
            
            # Filtrar el dataframe
            matching_keywords = result.get('keywords', [])
            return df[df['keyword'].isin(matching_keywords)]
            
        except Exception as e:
            print(f"Error obteniendo detalles del topic: {str(e)}")
            return pd.DataFrame()
