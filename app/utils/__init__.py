"""
Utilidades y funciones auxiliares
"""

from app.utils.helpers import (
    export_to_excel,
    export_to_json,
    calculate_metrics,
    format_number,
    categorize_keyword_intent,
    filter_keywords_by_intent,
    detect_keyword_patterns,
    create_content_calendar,
    validate_dataframe
)

from app.utils.prompts import (
    build_prompt,
    THEMATIC_ANALYSIS_PROMPT,
    INTENT_ANALYSIS_PROMPT,
    FUNNEL_ANALYSIS_PROMPT,
    COMPETITIVE_ANALYSIS_PROMPT,
    GAPS_DETECTION_PROMPT,
    TRENDS_DETECTION_PROMPT
)

__all__ = [
    # helpers
    'export_to_excel',
    'export_to_json',
    'calculate_metrics',
    'format_number',
    'categorize_keyword_intent',
    'filter_keywords_by_intent',
    'detect_keyword_patterns',
    'create_content_calendar',
    'validate_dataframe',
    'CacheManager',
    
    # prompts
    'build_prompt',
    'THEMATIC_ANALYSIS_PROMPT',
    'INTENT_ANALYSIS_PROMPT',
    'FUNNEL_ANALYSIS_PROMPT',
    'COMPETITIVE_ANALYSIS_PROMPT',
    'GAPS_DETECTION_PROMPT',
    'TRENDS_DETECTION_PROMPT',
]
