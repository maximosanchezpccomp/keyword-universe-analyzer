"""
Servicio para generar arquitectura web basada en análisis de keywords
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import json


class WebArchitectureService:
    """Genera propuestas de arquitectura web basadas en análisis de keywords"""
    
    def __init__(self, anthropic_service=None, openai_service=None):
        """
        Inicializa el servicio con los proveedores de IA disponibles
        
        Args:
            anthropic_service: Instancia de AnthropicService
            openai_service: Instancia de OpenAIService
        """
        self.anthropic_service = anthropic_service
        self.openai_service = openai_service
    
    def create_architecture_prompt(
        self,
        analysis_results: List[Dict[str, Any]],
        df: pd.DataFrame,
        custom_instructions: str = ""
    ) -> str:
        """
        Crea el prompt para generar la arquitectura web
        
        Args:
            analysis_results: Lista de resultados de análisis previos
            df: DataFrame con todas las keywords
            custom_instructions: Instrucciones adicionales del usuario
        """
        
        # Extraer insights de todos los análisis
        all_topics = []
        analysis_summaries = []
        
        for i, analysis in enumerate(analysis_results, 1):
            analysis_summaries.append(f"**Análisis {i}:** {analysis.get('summary', 'N/A')}")
            if 'topics' in analysis:
                all_topics.extend(analysis['topics'])
        
        # Stats globales
        total_keywords = len(df)
        total_volume = int(df['volume'].sum())
        
        # Top keywords por volumen
        top_keywords = df.nlargest(100, 'volume')[['keyword', 'volume']].to_dict('records')
        
        prompt = f"""Eres un experto en arquitectura de información y SEO. Tu tarea es crear una propuesta de ARQUITECTURA WEB completa basada en múltiples análisis de keywords.

# CONTEXTO GLOBAL
- Total de keywords analizadas: {total_keywords:,}
- Volumen total de búsqueda: {total_volume:,}
- Número de análisis realizados: {len(analysis_results)}

# RESÚMENES DE ANÁLISIS PREVIOS
{chr(10).join(analysis_summaries)}

# TOPICS IDENTIFICADOS (De todos los análisis)
{json.dumps(all_topics[:50], indent=2)}

# TOP KEYWORDS POR VOLUMEN
{json.dumps(top_keywords, indent=2)}

# TU MISIÓN
Crear una PROPUESTA DE ARQUITECTURA WEB estructurada en:

1. **FAMILIAS**: Categorías principales del sitio web (nivel 1 de navegación)
2. **SUBFAMILIAS**: Subcategorías dentro de cada familia (nivel 2)
3. **MARCAS**: Si aplica, agrupaciones por marca/fabricante
4. **CASOS DE USO**: Agrupaciones por uso/aplicación específica

# CRITERIOS CLAVE
- Cada familia debe tener coherencia semántica
- Priorizar por volumen de búsqueda y relevancia estratégica
- Considerar la intención del usuario en cada nivel
- Crear una jerarquía lógica y navegable
- Balancear SEO con usabilidad

{f"# INSTRUCCIONES ADICIONALES\\n{custom_instructions}" if custom_instructions else ""}

# FORMATO DE RESPUESTA (JSON)
Responde ÚNICAMENTE con un JSON válido con esta estructura:

{{
    "summary": "Resumen ejecutivo de la arquitectura propuesta (3-4 párrafos explicando la estrategia)",
    "families": [
        {{
            "name": "Nombre de la Familia",
            "slug": "url-slug",
            "description": "Descripción detallada de esta familia",
            "priority": "high|medium|low",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "keyword_count": 250,
            "total_volume": 500000,
            "tier": 1,
            "content_strategy": "Estrategia de contenido recomendada",
            "subfamilies": [
                {{
                    "name": "Nombre de Subfamilia",
                    "slug": "subfamilia-slug",
                    "description": "Descripción",
                    "keywords": ["keyword1", "keyword2"],
                    "keyword_count": 50,
                    "total_volume": 100000,
                    "content_type": "Hub page|Category page|Collection"
                }}
            ],
            "brands": [
                {{
                    "name": "Nombre de Marca",
                    "slug": "marca-slug",
                    "keywords": ["keyword1", "keyword2"],
                    "keyword_count": 30,
                    "total_volume": 50000,
                    "strategy": "Estrategia para esta marca"
                }}
            ],
            "use_cases": [
                {{
                    "name": "Caso de uso",
                    "slug": "caso-uso-slug",
                    "description": "Descripción del caso de uso",
                    "keywords": ["keyword1", "keyword2"],
                    "keyword_count": 20,
                    "total_volume": 30000,
                    "content_type": "Guide|Tutorial|Comparison"
                }}
            ]
        }}
    ],
    "url_structure": {{
        "pattern": "Patrón de URLs recomendado",
        "examples": [
            "/familia/subfamilia/producto",
            "/familia/marca/producto",
            "/casos-uso/nombre-caso"
        ]
    }},
    "navigation_recommendations": {{
        "primary_nav": ["Familia 1", "Familia 2", "..."],
        "secondary_nav": "Recomendaciones para navegación secundaria",
        "breadcrumbs": "Estructura de breadcrumbs recomendada"
    }},
    "internal_linking": {{
        "strategy": "Estrategia de enlazado interno",
        "hub_pages": ["Página 1", "Página 2"],
        "cluster_approach": "Descripción del modelo cluster"
    }},
    "content_priorities": [
        {{
            "phase": "Fase 1 (0-3 meses)",
            "families": ["Familia prioritaria 1", "..."],
            "rationale": "Por qué empezar por aquí"
        }},
        {{
            "phase": "Fase 2 (3-6 meses)",
            "families": ["Familia 2", "..."],
            "rationale": "Por qué continuar con esto"
        }}
    ],
    "seo_opportunities": [
        {{
            "opportunity": "Descripción de la oportunidad",
            "potential_volume": 50000,
            "difficulty": "low|medium|high",
            "recommendation": "Qué hacer"
        }}
    ]
}}

CRÍTICO: Responde SOLO con el JSON válido, sin texto adicional antes o después."""

        return prompt
    
    def generate_architecture(
        self,
        analysis_results: List[Dict[str, Any]],
        df: pd.DataFrame,
        provider: str = "claude",
        custom_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Genera la arquitectura web usando el proveedor especificado
        
        Args:
            analysis_results: Lista de análisis previos
            df: DataFrame con keywords
            provider: "claude", "openai" o "both"
            custom_instructions: Instrucciones adicionales
        
        Returns:
            Diccionario con la arquitectura web propuesta
        """
        
        prompt = self.create_architecture_prompt(analysis_results, df, custom_instructions)
        
        if provider == "claude" and self.anthropic_service:
            return self._generate_with_claude(prompt)
        elif provider == "openai" and self.openai_service:
            return self._generate_with_openai(prompt)
        elif provider == "both":
            return self._generate_with_both(prompt, analysis_results, df)
        else:
            raise ValueError(f"Proveedor {provider} no disponible")
    
    def _generate_with_claude(self, prompt: str) -> Dict[str, Any]:
        """Genera arquitectura usando Claude"""
        
        try:
            message = self.anthropic_service.client.messages.create(
                model=self.anthropic_service.model,
                max_tokens=16000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parsear JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No se pudo extraer JSON válido")
            
            result['provider'] = 'Claude'
            result['model'] = self.anthropic_service.model
            
            return result
            
        except Exception as e:
            raise Exception(f"Error generando arquitectura con Claude: {str(e)}")
    
    def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Genera arquitectura usando OpenAI"""
        
        try:
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en arquitectura web y SEO."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=16000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result['provider'] = 'OpenAI'
            result['model'] = self.openai_service.model
            
            return result
            
        except Exception as e:
            raise Exception(f"Error generando arquitectura con OpenAI: {str(e)}")
    
    def _generate_with_both(
        self,
        prompt: str,
        analysis_results: List[Dict[str, Any]],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Genera con ambos proveedores y combina resultados"""
        
        # Generar con Claude
        claude_result = self._generate_with_claude(prompt)
        
        # Generar con OpenAI
        openai_result = self._generate_with_openai(prompt)
        
        # Validación cruzada
        validation_prompt = f"""Compara estas dos propuestas de arquitectura web y proporciona:

1. Puntos en común (familias/estructuras que ambos identificaron)
2. Diferencias clave
3. Fortalezas de cada propuesta
4. Recomendación final: qué elementos tomar de cada una

PROPUESTA CLAUDE:
{json.dumps(claude_result.get('families', [])[:10], indent=2)}

PROPUESTA OPENAI:
{json.dumps(openai_result.get('families', [])[:10], indent=2)}

Responde en JSON:
{{
    "comparison": "Análisis comparativo",
    "common_families": ["Familia 1", "..."],
    "unique_to_claude": ["Familia X", "..."],
    "unique_to_openai": ["Familia Y", "..."],
    "recommendation": "Qué propuesta usar o cómo combinarlas"
}}"""

        try:
            comparison_response = self.anthropic_service.client.messages.create(
                model=self.anthropic_service.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": validation_prompt}]
            )
            
            comparison = json.loads(comparison_response.content[0].text)
        except:
            comparison = {
                "comparison": "No se pudo realizar la comparación",
                "recommendation": "Revisar ambas propuestas manualmente"
            }
        
        return {
            'summary': f"**Propuesta Claude:**\n{claude_result.get('summary', '')}\n\n**Propuesta OpenAI:**\n{openai_result.get('summary', '')}",
            'families': claude_result.get('families', []),
            'families_openai': openai_result.get('families', []),
            'comparison': comparison,
            'url_structure': claude_result.get('url_structure', {}),
            'navigation_recommendations': claude_result.get('navigation_recommendations', {}),
            'internal_linking': claude_result.get('internal_linking', {}),
            'provider': 'Ambos',
            'models': f"Claude: {claude_result.get('model')} | OpenAI: {openai_result.get('model')}"
        }
    
    def enrich_architecture_with_keywords(
        self,
        architecture: Dict[str, Any],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Enriquece la arquitectura asignando keywords específicas a cada elemento
        
        Args:
            architecture: Arquitectura generada
            df: DataFrame con todas las keywords
        """
        
        # Este método puede usarse para hacer un segundo paso
        # donde se asignen keywords específicas a cada familia/subfamilia
        # basándose en similitud semántica
        
        return architecture
    
    def export_architecture_to_sitemap(
        self,
        architecture: Dict[str, Any],
        base_url: str = "https://example.com"
    ) -> str:
        """
        Genera un mapa del sitio conceptual basado en la arquitectura
        
        Returns:
            String con la estructura del sitio
        """
        
        sitemap = [f"# Arquitectura Web Propuesta\n\nBase URL: {base_url}\n"]
        
        families = architecture.get('families', [])
        
        for family in families:
            family_slug = family.get('slug', '')
            sitemap.append(f"\n## 📁 /{family_slug}/ - {family['name']}")
            sitemap.append(f"   Volume: {family.get('total_volume', 0):,} | Keywords: {family.get('keyword_count', 0)}")
            
            # Subfamilies
            for subfamily in family.get('subfamilies', []):
                subfamily_slug = subfamily.get('slug', '')
                sitemap.append(f"   └─ 📄 /{family_slug}/{subfamily_slug}/ - {subfamily['name']}")
                sitemap.append(f"      Volume: {subfamily.get('total_volume', 0):,}")
            
            # Brands
            for brand in family.get('brands', []):
                brand_slug = brand.get('slug', '')
                sitemap.append(f"   └─ 🏷️ /{family_slug}/marca/{brand_slug}/ - {brand['name']}")
            
            # Use cases
            for use_case in family.get('use_cases', []):
                case_slug = use_case.get('slug', '')
                sitemap.append(f"   └─ 💡 /{family_slug}/caso-uso/{case_slug}/ - {use_case['name']}")
        
        return '\n'.join(sitemap)
