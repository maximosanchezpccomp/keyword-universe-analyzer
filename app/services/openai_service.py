"""
Servicio para integración con OpenAI API (opcional)
Puede usarse como alternativa o complemento a Claude
"""

from openai import OpenAI
import pandas as pd
import json
from typing import Dict, List, Any

class OpenAIService:
    """Servicio para interactuar con la API de OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = 4000
    
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
        """Crea los mensajes para OpenAI (formato chat)"""
        
        # Preparar datos
        top_keywords = df.nlargest(1000, 'volume')[['keyword', 'volume', 'traffic']].to_dict('records')
        
        stats = {
            'total_keywords': len(df),
            'total_volume': int(df['volume'].sum()),
            'avg_volume': int(df['volume'].mean()),
        }
        
        system_message = """Eres un experto en SEO y análisis de keywords. 
Tu tarea es crear un "Keyword Universe" completo y estratégico.
Debes responder ÚNICAMENTE con JSON válido."""
        
        user_message = f"""Analiza las siguientes keywords y crea un Keyword Universe.

# DATOS
- Total keywords: {stats['total_keywords']:,}
- Volumen total: {stats['total_volume']:,}
- Tipo de análisis: {analysis_type}
- Número de tiers: {num_tiers}

# INSTRUCCIONES
1. Agrupa keywords por tema semántico
2. Asigna {num_tiers} tiers de prioridad (1 = máxima)
3. Calcula métricas por topic

{custom_instructions}

# FORMATO DE RESPUESTA (JSON)
{{
    "summary": "Resumen ejecutivo del análisis",
    "topics": [
        {{
            "topic": "Nombre del topic",
            "tier": 1,
            "keyword_count": 50,
            "volume": 150000,
            "traffic": 45000,
            "priority": "high",
            "description": "Descripción",
            "example_keywords": ["kw1", "kw2", "kw3"]
        }}
    ]
}}

# KEYWORDS
{json.dumps(top_keywords[:500], indent=2)}

Responde SOLO con el JSON."""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    def analyze_keywords(self, messages: List[Dict[str, str]], df: pd.DataFrame) -> Dict[str, Any]:
        """Envía el prompt a OpenAI y procesa la respuesta"""
        
        try:
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
            result = json.loads(response_text)
            
            # Enriquecer resultados
            result = self._enrich_results(result, df)
            
            return result
            
        except Exception as e:
            raise Exception(f"Error al analizar con OpenAI: {str(e)}")
    
    def _enrich_results(self, result: Dict, df: pd.DataFrame) -> Dict:
        """Enriquece los resultados con datos adicionales"""
        
        if 'topics' in result:
            for topic in result['topics']:
                topic['keyword_count'] = int(topic.get('keyword_count', 0))
                topic['volume'] = int(topic.get('volume', 0))
                topic['traffic'] = int(topic.get('traffic', 0))
                
                if topic['keyword_count'] > 0:
                    topic['avg_volume_per_keyword'] = topic['volume'] / topic['keyword_count']
                else:
                    topic['avg_volume_per_keyword'] = 0
        
        return result
    
    def compare_with_claude(
        self, 
        claude_result: Dict[str, Any], 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Compara resultados de Claude con OpenAI para validación cruzada
        
        Args:
            claude_result: Resultado del análisis de Claude
            df: DataFrame con las keywords
        
        Returns:
            Análisis comparativo
        """
        
        messages = [
            {
                "role": "system",
                "content": "Eres un experto en SEO que valida y complementa análisis de keywords."
            },
            {
                "role": "user",
                "content": f"""Revisa este análisis de keywords y proporciona:
1. Validación de los topics identificados
2. Topics adicionales que podrían haberse pasado por alto
3. Mejoras sugeridas a la clasificación

ANÁLISIS ORIGINAL:
{json.dumps(claude_result, indent=2)}

Responde en JSON con:
{{
    "validation": "Evaluación general",
    "missing_topics": ["topic1", "topic2"],
    "improvements": ["mejora1", "mejora2"]
}}"""
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
            
        except Exception as e:
            print(f"Error en comparación: {str(e)}")
            return {}
