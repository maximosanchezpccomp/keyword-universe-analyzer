"""
Servicio para generar arquitectura de contenido web basada en análisis de keywords
"""

from openai import OpenAI
from anthropic import Anthropic
import pandas as pd
import json
from typing import Dict, List, Any, Optional

class ArchitectureService:
    """Servicio para generar arquitecturas de sitios web basadas en keyword analysis"""
    
    def __init__(
        self, 
        anthropic_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        claude_model: str = "claude-sonnet-4-5-20250929",
        openai_model: str = "gpt-4o"
    ):
        self.anthropic_client = Anthropic(api_key=anthropic_key) if anthropic_key else None
        self.openai_client = OpenAI(api_key=openai_key) if openai_key else None
        self.claude_model = claude_model
        self.openai_model = openai_model
        self.max_tokens = 16000
    
    def generate_architecture(
        self,
        analysis_results: Dict[str, Any],
        df: pd.DataFrame,
        provider: str = "Claude",
        custom_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Genera arquitectura de sitio web basada en análisis de keywords
        
        Args:
            analysis_results: Resultados del análisis de keywords
            df: DataFrame con las keywords
            provider: "Claude", "OpenAI", o "Ambos"
            custom_instructions: Instrucciones adicionales
        
        Returns:
            Diccionario con la arquitectura generada
        """
        
        # Crear prompt
        prompt = self._create_architecture_prompt(
            analysis_results,
            df,
            custom_instructions
        )
        
        # Generar según proveedor
        if provider == "Claude":
            if not self.anthropic_client:
                raise ValueError("Claude API key no configurada")
            return self._generate_with_claude(prompt, analysis_results, df)
        
        elif provider == "OpenAI":
            if not self.openai_client:
                raise ValueError("OpenAI API key no configurada")
            return self._generate_with_openai(prompt)
        
        elif provider == "Ambos":
            if not self.anthropic_client or not self.openai_client:
                raise ValueError("Ambas API keys son necesarias para validación cruzada")
            return self._generate_with_both(prompt, analysis_results, df)
        
        else:
            raise ValueError(f"Proveedor no válido: {provider}")
    
    def _create_architecture_prompt(
        self,
        analysis_results: Dict[str, Any],
        df: pd.DataFrame,
        custom_instructions: str = ""
    ) -> str:
        """Crea el prompt para generar arquitectura"""
        
        # Extraer topics del análisis
        topics = analysis_results.get('topics', [])
        
        # Crear resumen de topics
        topics_summary = []
        for topic in topics[:50]:  # Limitar a top 50 para no exceder tokens
            topics_summary.append({
                'topic': topic.get('topic', 'N/A'),
                'tier': topic.get('tier', 0),
                'keyword_count': topic.get('keyword_count', 0),
                'volume': topic.get('volume', 0),
                'priority': topic.get('priority', 'medium')
            })
        
        prompt = f"""Eres un experto en arquitectura de información y SEO. Tu tarea es crear una arquitectura de sitio web optimizada basada en el análisis de keywords.

# CONTEXTO
- Total keywords analizadas: {len(df):,}
- Topics identificados: {len(topics)}
- Volumen total: {df['volume'].sum():,.0f}

# TOPICS PRINCIPALES
{json.dumps(topics_summary, indent=2)}

# TU MISIÓN
Crea una arquitectura de sitio web jerárquica que:
1. Organice el contenido de forma lógica y SEO-friendly
2. Establezca una estructura de URL clara
3. Defina la navegación principal
4. Identifique páginas pillar y páginas de soporte
5. Considere la intención del usuario y el customer journey

{custom_instructions}

# FORMATO DE RESPUESTA (CRÍTICO - JSON VÁLIDO)
Responde ÚNICAMENTE con un JSON válido con esta estructura:

{{
    "overview": "Resumen ejecutivo de la arquitectura propuesta (2-3 párrafos)",
    "site_structure": {{
        "home": {{
            "title": "Homepage",
            "description": "Descripción y propósito",
            "target_keywords": ["keyword1", "keyword2"],
            "priority": "critical"
        }},
        "main_sections": [
            {{
                "section_name": "Nombre de la sección",
                "url_structure": "/section-name",
                "description": "Propósito de esta sección",
                "navigation_label": "Label en menú",
                "target_topics": ["topic1", "topic2"],
                "estimated_volume": 100000,
                "page_type": "category|hub|landing",
                "priority": "high|medium|low",
                "subsections": [
                    {{
                        "name": "Subsección",
                        "url": "/section-name/subsection",
                        "description": "Propósito",
                        "target_keywords": ["keyword1", "keyword2"],
                        "page_type": "article|guide|comparison"
                    }}
                ]
            }}
        ]
    }},
    "navigation": {{
        "primary_menu": [
            {{
                "label": "Label del menú",
                "url": "/url",
                "dropdown": ["Opción 1", "Opción 2"]
            }}
        ],
        "footer_sections": [
            {{
                "title": "Título del grupo",
                "links": ["Link 1", "Link 2"]
            }}
        ]
    }},
    "content_strategy": {{
        "pillar_pages": [
            {{
                "title": "Título de página pillar",
                "url": "/url",
                "target_topics": ["topic1", "topic2"],
                "estimated_word_count": 3000,
                "supporting_articles": 10,
                "priority": "high"
            }}
        ],
        "content_clusters": [
            {{
                "cluster_name": "Nombre del cluster",
                "pillar_page": "/url-pillar",
                "cluster_articles": [
                    {{
                        "title": "Título del artículo",
                        "url": "/url",
                        "target_keywords": ["keyword1"],
                        "word_count": 1500
                    }}
                ]
            }}
        ]
    }},
    "internal_linking": {{
        "strategy": "Descripción de la estrategia de linking interno",
        "hub_pages": ["URL 1", "URL 2"],
        "linking_opportunities": [
            {{
                "from": "/page-a",
                "to": "/page-b",
                "anchor_text": "texto del enlace",
                "reason": "por qué este enlace es importante"
            }}
        ]
    }},
    "implementation_roadmap": [
        {{
            "phase": 1,
            "duration": "1-2 meses",
            "focus": "Descripción del foco de esta fase",
            "pages_to_create": 10,
            "priority_pages": ["URL 1", "URL 2"],
            "estimated_effort": "80 horas"
        }}
    ],
    "technical_recommendations": [
        "Recomendación técnica 1",
        "Recomendación técnica 2"
    ],
    "url_naming_conventions": {{
        "pattern": "Patrón de URLs (ej: /categoria/subcategoria/articulo)",
        "examples": ["Ejemplo 1", "Ejemplo 2"],
        "rules": ["Regla 1", "Regla 2"]
    }}
}}

CRÍTICO: 
- Responde SOLO con el JSON, sin texto antes o después
- Asegúrate de que el JSON es válido y está completo
- No uses comillas simples, solo comillas dobles
- No incluyas comentarios en el JSON"""

        return prompt
    
    def _generate_with_claude(
        self, 
        prompt: str,
        analysis_results: Dict[str, Any],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Genera arquitectura con Claude"""
        
        try:
            message = self.anthropic_client.messages.create(
                model=self.claude_model,
                max_tokens=self.max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extraer contenido
            response_text = message.content[0].text
            
            # Parsear JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Intentar extraer JSON del texto
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"No se pudo extraer JSON válido: {str(e)}")
            
            # Añadir metadata
            result['provider'] = 'Claude'
            result['model'] = self.claude_model
            
            return result
            
        except Exception as e:
            raise Exception(f"Error generando arquitectura con Claude: {str(e)}")
    
    def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Genera arquitectura con OpenAI"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en arquitectura de información y SEO. Siempre respondes con JSON válido y completo."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # CRÍTICO: Verificar que hay contenido antes de parsear
            content = response.choices[0].message.content
            
            if content is None or content.strip() == "":
                # Si no hay contenido, puede ser por:
                # 1. Contenido filtrado por políticas de OpenAI
                # 2. Límite de tokens excedido
                # 3. Error en el modelo
                
                finish_reason = response.choices[0].finish_reason
                
                if finish_reason == "content_filter":
                    raise ValueError(
                        "OpenAI filtró el contenido. "
                        "Intenta simplificar el prompt o usar menos datos."
                    )
                elif finish_reason == "length":
                    raise ValueError(
                        "Se alcanzó el límite de tokens. "
                        "Intenta reducir el número de topics o usar un límite menor."
                    )
                else:
                    raise ValueError(
                        f"OpenAI devolvió respuesta vacía. "
                        f"Reason: {finish_reason}. "
                        "Intenta con menos datos o con Claude."
                    )
            
            # Parsear JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                # Intentar extraer JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(
                        f"No se pudo parsear JSON de OpenAI: {str(e)}\n"
                        f"Contenido recibido: {content[:500]}..."
                    )
            
            # Añadir metadata
            result['provider'] = 'OpenAI'
            result['model'] = self.openai_model
            
            return result
            
        except Exception as e:
            raise Exception(f"Error generando arquitectura con OpenAI: {str(e)}")
    
    def _generate_with_both(
        self,
        prompt: str,
        analysis_results: Dict[str, Any],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Genera arquitectura con ambos proveedores para validación cruzada"""
        
        try:
            # Generar con Claude primero (más confiable)
            claude_result = self._generate_with_claude(prompt, analysis_results, df)
            
            # Generar con OpenAI
            try:
                openai_result = self._generate_with_openai(prompt)
            except Exception as e:
                # Si OpenAI falla, solo usar Claude pero informar
                print(f"OpenAI falló, usando solo Claude: {str(e)}")
                claude_result['validation_note'] = f"OpenAI no disponible: {str(e)}"
                return claude_result
            
            # Combinar resultados
            combined = {
                'overview': f"**Análisis de Claude:**\n{claude_result.get('overview', '')}\n\n**Análisis de OpenAI:**\n{openai_result.get('overview', '')}",
                'site_structure': claude_result.get('site_structure', {}),
                'site_structure_openai': openai_result.get('site_structure', {}),
                'navigation': claude_result.get('navigation', {}),
                'content_strategy': claude_result.get('content_strategy', {}),
                'internal_linking': claude_result.get('internal_linking', {}),
                'implementation_roadmap': claude_result.get('implementation_roadmap', []),
                'technical_recommendations': claude_result.get('technical_recommendations', []),
                'url_naming_conventions': claude_result.get('url_naming_conventions', {}),
                'provider': 'Ambos',
                'models': f"Claude: {self.claude_model} | OpenAI: {self.openai_model}",
                'validation': self._compare_architectures(claude_result, openai_result)
            }
            
            return combined
            
        except Exception as e:
            raise Exception(f"Error en validación cruzada: {str(e)}")
    
    def _compare_architectures(
        self,
        claude_result: Dict[str, Any],
        openai_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compara las arquitecturas generadas por ambos proveedores"""
        
        comparison = {
            'agreement': 'high',  # high, medium, low
            'differences': [],
            'recommendations': []
        }
        
        # Comparar número de secciones principales
        claude_sections = len(claude_result.get('site_structure', {}).get('main_sections', []))
        openai_sections = len(openai_result.get('site_structure', {}).get('main_sections', []))
        
        if abs(claude_sections - openai_sections) > 3:
            comparison['differences'].append(
                f"Claude sugiere {claude_sections} secciones, "
                f"OpenAI sugiere {openai_sections}"
            )
            comparison['agreement'] = 'medium'
        
        # Comparar fases de implementación
        claude_phases = len(claude_result.get('implementation_roadmap', []))
        openai_phases = len(openai_result.get('implementation_roadmap', []))
        
        if abs(claude_phases - openai_phases) > 1:
            comparison['differences'].append(
                f"Claude sugiere {claude_phases} fases, "
                f"OpenAI sugiere {openai_phases} fases"
            )
        
        # Generar recomendaciones
        if comparison['agreement'] == 'high':
            comparison['recommendations'].append(
                "Ambos modelos coinciden en la estructura general. "
                "Puedes proceder con confianza."
            )
        else:
            comparison['recommendations'].append(
                "Hay diferencias significativas. "
                "Revisa ambas propuestas y combina lo mejor de cada una."
            )
        
        return comparison
    
    def export_to_document(self, architecture: Dict[str, Any]) -> str:
        """Exporta la arquitectura a un documento markdown"""
        
        doc = f"""# Arquitectura de Sitio Web

{architecture.get('overview', '')}

## Estructura del Sitio

### Homepage
{json.dumps(architecture.get('site_structure', {}).get('home', {}), indent=2)}

### Secciones Principales
"""
        
        for section in architecture.get('site_structure', {}).get('main_sections', []):
            doc += f"\n#### {section.get('section_name', 'N/A')}\n"
            doc += f"- **URL:** {section.get('url_structure', 'N/A')}\n"
            doc += f"- **Tipo:** {section.get('page_type', 'N/A')}\n"
            doc += f"- **Prioridad:** {section.get('priority', 'N/A')}\n"
            doc += f"- **Descripción:** {section.get('description', 'N/A')}\n"
            
            if section.get('subsections'):
                doc += "\n**Subsecciones:**\n"
                for subsection in section['subsections']:
                    doc += f"- {subsection.get('name', 'N/A')} ({subsection.get('url', 'N/A')})\n"
        
        doc += "\n## Navegación\n\n"
        doc += json.dumps(architecture.get('navigation', {}), indent=2)
        
        doc += "\n\n## Estrategia de Contenido\n\n"
        doc += json.dumps(architecture.get('content_strategy', {}), indent=2)
        
        doc += "\n\n## Roadmap de Implementación\n\n"
        
        for phase in architecture.get('implementation_roadmap', []):
            doc += f"\n### Fase {phase.get('phase', 0)}\n"
            doc += f"- **Duración:** {phase.get('duration', 'N/A')}\n"
            doc += f"- **Foco:** {phase.get('focus', 'N/A')}\n"
            doc += f"- **Páginas a crear:** {phase.get('pages_to_create', 0)}\n"
            doc += f"- **Esfuerzo estimado:** {phase.get('estimated_effort', 'N/A')}\n"
        
        return doc
