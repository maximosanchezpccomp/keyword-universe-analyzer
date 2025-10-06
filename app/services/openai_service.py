"""
Servicio para integración con OpenAI API
Alternativa o complemento a Claude para análisis de keywords
"""

from openai import OpenAI
import pandas as pd
import json
from typing import Dict, List, Any

class OpenAIService:
    """Servicio para interactuar con la API de OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = 16000 if model in ["gpt-4o", "gpt-4-turbo"] else 4096
    
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
        """Crea los mensajes para OpenAI en formato chat"""
        
        # Preparar datos
        top_keywords = df.nlargest(1000, 'volume')[['keyword', 'volume', 'traffic']].to_dict('records')
        
        stats = {
            'total_keywords': len(df),
            'total_volume': int(df['volume'].sum()),
            'avg_volume': int(df['volume'].mean()),
            'unique_keywords': df['keyword'].nunique()
        }
        
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
        
        system_message = """Eres un experto en SEO y análisis estratégico de keywords. 
Tu especialidad es identificar patrones, oportunidades y crear estrategias data-driven.
Siempre respondes con JSON válido y análisis profundos."""
        
        user_message = f"""Analiza las siguientes keywords y crea un "Keyword Universe" completo.

# CONTEXTO
- Total keywords: {stats['total_keywords']:,}
- Volumen total: {stats['total_volume']:,}
- Volumen promedio: {stats['avg_volume']:,}
- Keywords únicas: {stats['unique_keywords']:,}

# TIPO DE ANÁLISIS
{analysis_type}

{analysis_instructions}

# TU TAREA
Crea un análisis con {num_tiers} tiers (niveles) de prioridad:
- Tier 1: Alto volumen y máxima prioridad estratégica
- Tier {num_tiers}: Menor volumen pero oportunidades específicas

{custom_instructions}

{"IMPORTANTE: Realiza análisis semántico profundo para entender la intención real detrás de cada keyword." if include_semantic else ""}
{"IMPORTANTE: Identifica tendencias emergentes y keywords en crecimiento." if include_trends else ""}
{"IMPORTANTE: Detecta gaps de contenido - topics con alto volumen pero poca cobertura competitiva." if include_gaps else ""}

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

# KEYWORDS A ANALIZAR
{json.dumps(top_keywords[:1000], indent=2)}

CRÍTICO: Responde SOLO con el JSON válido, sin texto adicional antes o después."""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    def _get_analysis_instructions(self, analysis_type: str) -> str:
        """Retorna instrucciones específicas según el tipo de análisis"""
        
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
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Intentar extraer JSON del texto
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No se pudo extraer JSON válido de la respuesta")
            
            # Enriquecer resultados
            result = self._enrich_results(result, df)
            
            return result
            
        except Exception as e:
            raise Exception(f"Error al analizar con OpenAI: {str(e)}")
    
    def _enrich_results(self, result: Dict, df: pd.DataFrame) -> Dict:
        """Enriquece los resultados con datos adicionales"""
        
        if 'topics' in result:
            for topic in result['topics']:
                # Asegurar tipos correctos
                topic['keyword_count'] = int(topic.get('keyword_count', 0))
                topic['volume'] = int(topic.get('volume', 0))
                topic['traffic'] = int(topic.get('traffic', 0))
                
                # Calcular métricas adicionales
                if topic['keyword_count'] > 0:
                    topic['avg_volume_per_keyword'] = topic['volume'] / topic['keyword_count']
                else:
                    topic['avg_volume_per_keyword'] = 0
                
                # Asegurar que tier sea int
                topic['tier'] = int(topic.get('tier', 1))
        
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
{json.dumps(claude_result.get('topics', [])[:20], indent=2)}

KEYWORDS DISPONIBLES (muestra):
{json.dumps(df.nlargest(200, 'volume')[['keyword', 'volume']].to_dict('records'), indent=2)}

Responde en JSON:
{{
    "validation": "Evaluación general del análisis (2-3 párrafos)",
    "missing_topics": ["topic1 no identificado", "topic2 no identificado"],
    "improvements": ["mejora sugerida 1", "mejora sugerida 2"],
    "agreement_score": 85,
    "key_differences": "Principales diferencias con tu análisis"
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
            return {
                "validation": "No se pudo completar la validación cruzada",
                "missing_topics": [],
                "improvements": [],
                "error": str(e)
            }
    
    def get_topic_details(self, topic_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica keywords específicas que pertenecen a un topic"""
        
        sample_keywords = df.nlargest(500, 'volume')[['keyword', 'volume']].to_dict('records')
        
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
{json.dumps(sample_keywords, indent=2)}"""
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
            
            return df[df['keyword'].isin(matching_keywords)]
            
        except Exception as e:
            print(f"Error obteniendo detalles del topic: {str(e)}")
            return pd.DataFrame()
