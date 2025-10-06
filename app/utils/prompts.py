"""
Templates de prompts para diferentes tipos de análisis de keywords
"""

# Prompt base para análisis temático
THEMATIC_ANALYSIS_PROMPT = """Eres un experto en SEO y análisis de keywords. Tu tarea es crear un "Keyword Universe" completo y estratégico agrupando keywords por temas semánticos.

# CONTEXTO
- Total de keywords analizadas: {total_keywords}
- Volumen total de búsqueda: {total_volume}
- Objetivo: Identificar {num_tiers} tiers de prioridad

# INSTRUCCIONES
1. Analiza las keywords proporcionadas y agrúpalas en topics temáticos coherentes
2. Cada topic debe representar un área temática clara y diferenciada
3. Asigna tiers (1 = máxima prioridad, {num_tiers} = menor prioridad) basándote en:
   - Volumen de búsqueda total
   - Relevancia estratégica
   - Oportunidad de competir
4. Identifica 5-15 topics principales por tier
5. Para cada topic, incluye ejemplos de keywords representativas

{custom_instructions}

# FORMATO DE RESPUESTA (JSON)
Responde ÚNICAMENTE con un JSON válido con esta estructura:

{{
    "summary": "Resumen ejecutivo del análisis en 3-4 párrafos explicando los hallazgos principales",
    "topics": [
        {{
            "topic": "Nombre descriptivo del topic",
            "tier": 1,
            "keyword_count": 50,
            "volume": 150000,
            "traffic": 45000,
            "priority": "high|medium|low",
            "description": "Descripción detallada del topic y su importancia estratégica",
            "example_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
        }}
    ]
    {gaps_section}
    {trends_section}
}}

# KEYWORDS A ANALIZAR
{keywords_data}
"""

# Prompt para análisis por intención de búsqueda
INTENT_ANALYSIS_PROMPT = """Eres un experto en SEO y análisis de intención de búsqueda. Analiza las siguientes keywords y agrúpalas según la intención del usuario.

# TIPOS DE INTENCIÓN
1. **Informacional**: El usuario busca información, aprender algo
   - Ejemplos: "cómo hacer", "qué es", "guía de"
   
2. **Navegacional**: El usuario busca un sitio específico
   - Ejemplos: "login", "descargar", nombre de marca
   
3. **Comercial**: El usuario investiga antes de comprar
   - Ejemplos: "mejor", "review", "comparar", "alternativas"
   
4. **Transaccional**: El usuario está listo para comprar/actuar
   - Ejemplos: "comprar", "precio", "descuento", "gratis"

# DATOS
- Total keywords: {total_keywords}
- Volumen total: {total_volume}
- Tiers a generar: {num_tiers}

# INSTRUCCIONES
1. Clasifica cada keyword por su intención principal
2. Dentro de cada intención, agrupa por sub-temas
3. Asigna tiers basándote en volumen y valor estratégico
4. Las keywords transaccionales suelen ser tier 1 aunque tengan menor volumen

{custom_instructions}

# FORMATO DE RESPUESTA (JSON)
{{
    "summary": "Análisis de la distribución de intenciones y su importancia estratégica",
    "topics": [
        {{
            "topic": "Nombre del sub-tema",
            "intent": "informational|navigational|commercial|transactional",
            "tier": 1,
            "keyword_count": 50,
            "volume": 150000,
            "traffic": 45000,
            "priority": "high",
            "description": "Por qué este grupo es importante",
            "example_keywords": ["keyword1", "keyword2", "keyword3"]
        }}
    ]
}}

# KEYWORDS
{keywords_data}
"""

# Prompt para análisis de funnel
FUNNEL_ANALYSIS_PROMPT = """Eres un experto en marketing digital y funnel de conversión. Analiza estas keywords y clasifícalas según su posición en el funnel de ventas.

# ETAPAS DEL FUNNEL
1. **TOFU (Top of Funnel)** - Awareness
   - Usuario descubre el problema o necesidad
   - Alto volumen, baja intención de compra
   - Ejemplos: "qué es", "por qué", "cómo funciona"

2. **MOFU (Middle of Funnel)** - Consideration
   - Usuario evalúa soluciones
   - Volumen medio, intención creciente
   - Ejemplos: "mejores", "comparar", "tipos de", "beneficios"

3. **BOFU (Bottom of Funnel)** - Decision
   - Usuario listo para decidir
   - Menor volumen, alta intención
   - Ejemplos: "precio", "comprar", "demo", "trial", "vs competitor"

# DATOS
- Total keywords: {total_keywords}
- Volumen total: {total_volume}
- Tiers a generar: {num_tiers}

# ESTRATEGIA
- TOFU: Enfoque en contenido educativo y awareness
- MOFU: Enfoque en comparaciones y casos de uso
- BOFU: Enfoque en conversión y diferenciación

{custom_instructions}

# FORMATO DE RESPUESTA (JSON)
{{
    "summary": "Análisis de la distribución del funnel y estrategia recomendada para cada etapa",
    "topics": [
        {{
            "topic": "Nombre del tema",
            "funnel_stage": "TOFU|MOFU|BOFU",
            "tier": 1,
            "keyword_count": 50,
            "volume": 150000,
            "traffic": 45000,
            "conversion_potential": "high|medium|low",
            "content_type": "blog post|guide|comparison|landing page",
            "description": "Estrategia de contenido para este grupo",
            "example_keywords": ["keyword1", "keyword2", "keyword3"]
        }}
    ]
}}

# KEYWORDS
{keywords_data}
"""

# Prompt para detección de gaps
GAPS_DETECTION_PROMPT = """Analiza las keywords proporcionadas e identifica gaps de contenido - oportunidades donde hay alto volumen de búsqueda pero poca cobertura competitiva.

# CRITERIOS PARA GAPS
1. Alto volumen de búsqueda (relativo)
2. Baja competencia implícita (muchas variaciones sin cubrir)
3. Relevancia temática con el negocio
4. Potencial de ranking realista

# DATOS
{keywords_data}

# RESPUESTA (JSON)
{{
    "gaps": [
        {{
            "topic": "Nombre del gap/oportunidad",
            "volume": 50000,
            "keyword_count": 25,
            "difficulty": "low|medium|high",
            "description": "Por qué es una oportunidad",
            "recommended_action": "Crear guía completa|Series de blog posts|Landing page",
            "example_keywords": ["keyword1", "keyword2"]
        }}
    ]
}}
"""

# Prompt para análisis de tendencias
TRENDS_DETECTION_PROMPT = """Analiza las keywords e identifica tendencias emergentes, patrones de búsqueda y temas en crecimiento.

# QUÉ BUSCAR
1. Nuevas tecnologías o términos emergentes
2. Cambios en nomenclatura de la industria
3. Necesidades del usuario no satisfechas
4. Términos relacionados con innovación

# DATOS
{keywords_data}

# RESPUESTA (JSON)
{{
    "trends": [
        {{
            "trend": "Nombre de la tendencia",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "total_volume": 50000,
            "growth_potential": "high|medium|low",
            "insight": "Por qué esta tendencia es relevante y cómo capitalizarla",
            "recommended_timeline": "Prioridad inmediata|3-6 meses|6-12 meses"
        }}
    ]
}}
"""

# Prompt para análisis competitivo
COMPETITIVE_ANALYSIS_PROMPT = """Analiza las keywords desde una perspectiva competitiva, identificando donde hay oportunidades frente a la competencia.

# FUENTE DE DATOS
Keywords extraídas de {num_competitors} competidores principales

# ANALIZAR
1. Keywords donde múltiples competidores están posicionados
2. Keywords únicas de competidores específicos
3. Áreas de alta competencia vs baja competencia
4. Oportunidades de diferenciación

# DATOS
{keywords_data}

{custom_instructions}

# RESPUESTA (JSON)
{{
    "summary": "Análisis competitivo y estrategia recomendada",
    "topics": [
        {{
            "topic": "Nombre del tema",
            "tier": 1,
            "keyword_count": 50,
            "volume": 150000,
            "competition_level": "high|medium|low",
            "competitors_ranking": 3,
            "differentiation_opportunity": "high|medium|low",
            "strategy": "Descripción de cómo competir en este tema",
            "example_keywords": ["keyword1", "keyword2"]
        }}
    ],
    "opportunities": [
        {{
            "opportunity": "Descripción de la oportunidad",
            "keywords": ["keyword1", "keyword2"],
            "rationale": "Por qué es una oportunidad"
        }}
    ]
}}
"""

# Función helper para construir el prompt
def build_prompt(
    analysis_type: str,
    keywords_data: str,
    total_keywords: int,
    total_volume: int,
    num_tiers: int = 3,
    custom_instructions: str = "",
    include_gaps: bool = False,
    include_trends: bool = False,
    num_competitors: int = 0
) -> str:
    """
    Construye el prompt apropiado según el tipo de análisis
    
    Args:
        analysis_type: Tipo de análisis (thematic, intent, funnel, competitive)
        keywords_data: JSON string con las keywords
        total_keywords: Número total de keywords
        total_volume: Volumen total de búsqueda
        num_tiers: Número de tiers a generar
        custom_instructions: Instrucciones adicionales del usuario
        include_gaps: Si incluir análisis de gaps
        include_trends: Si incluir análisis de tendencias
        num_competitors: Número de competidores analizados
    
    Returns:
        Prompt completo formateado
    """
    
    # Secciones opcionales
    gaps_section = ""
    if include_gaps:
        gaps_section = """,
    "gaps": [
        {
            "topic": "Nombre del gap",
            "volume": 50000,
            "description": "Descripción",
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
            "insight": "Descripción del insight"
        }
    ]"""
    
    # Formatear custom instructions
    custom_instructions_text = ""
    if custom_instructions:
        custom_instructions_text = f"\n# INSTRUCCIONES ADICIONALES\n{custom_instructions}\n"
    
    # Seleccionar template
    templates = {
        "thematic": THEMATIC_ANALYSIS_PROMPT,
        "intent": INTENT_ANALYSIS_PROMPT,
        "funnel": FUNNEL_ANALYSIS_PROMPT,
        "competitive": COMPETITIVE_ANALYSIS_PROMPT
    }
    
    template = templates.get(analysis_type.lower(), THEMATIC_ANALYSIS_PROMPT)
    
    # Formatear el prompt
    prompt = template.format(
        keywords_data=keywords_data,
        total_keywords=f"{total_keywords:,}",
        total_volume=f"{total_volume:,}",
        num_tiers=num_tiers,
        custom_instructions=custom_instructions_text,
        gaps_section=gaps_section,
        trends_section=trends_section,
        num_competitors=num_competitors
    )
    
    return prompt


# Prompt para enriquecer un topic específico
ENRICH_TOPIC_PROMPT = """Dado el topic "{topic_name}", proporciona un análisis detallado y recomendaciones de contenido.

# TOPIC: {topic_name}
- Keywords asociadas: {keyword_count}
- Volumen total: {volume}

# PROPORCIONA
1. Análisis profundo del topic y subtemas
2. Tipos de contenido recomendados
3. Ángulos de contenido únicos
4. Estructura sugerida de contenido
5. Keywords específicas a targetear

# RESPUESTA (JSON)
{{
    "topic": "{topic_name}",
    "analysis": "Análisis detallado del topic",
    "content_recommendations": [
        {{
            "content_type": "Blog post|Guide|Video|Infographic",
            "title": "Título sugerido",
            "angle": "Ángulo único del contenido",
            "target_keywords": ["keyword1", "keyword2"],
            "estimated_traffic": 5000
        }}
    ],
    "subtopics": ["subtopic1", "subtopic2", "subtopic3"]
}}
"""
