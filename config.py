import os
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv es opcional en producción (Streamlit Cloud usa secrets)
    pass

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

# Crear directorios si no existen
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: No se pudo crear directorio {directory}: {e}")

# API Keys - con fallback a None
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")

# Logo configuration (para evitar errores)
LOGO_URL = None
LOGO_BASE64 = None

# Configuración de la aplicación
APP_CONFIG = {
    "title": os.getenv("APP_TITLE", "Keyword Universe Analyzer"),
    "version": "1.0.0",
    "author": "PC Componentes",
    "description": "Herramienta de análisis SEO con IA"
}

# Configuración de Claude
CLAUDE_CONFIG = {
    "model": os.getenv("DEFAULT_MODEL", "claude-sonnet-4-5-20250929"),
    "max_tokens": 16000,
    "temperature": 0.3,
    "models_available": [
        "claude-sonnet-4-5-20250929",
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514"
    ]
}

# Configuración de OpenAI
OPENAI_CONFIG = {
    "model": "gpt-4o",
    "max_tokens": 16000,
    "temperature": 0.3,
    "models_available": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]
}

# Configuración de Semrush
SEMRUSH_CONFIG = {
    "base_url": "https://api.semrush.com/",
    "default_database": os.getenv("DEFAULT_DATABASE", "us"),
    "rate_limit_delay": 1.0,  # segundos entre requests
    "max_keywords_per_request": 10000
}

# Configuración de análisis
ANALYSIS_CONFIG = {
    "max_keywords_per_file": int(os.getenv("MAX_KEYWORDS_PER_FILE", "1000")),
    "default_tiers": int(os.getenv("DEFAULT_TIERS", "3")),
    "min_volume": int(os.getenv("MIN_VOLUME", "10")),
    "sample_size_for_ai": 1000,  # Número de keywords a enviar a IA
    "enable_cache": os.getenv("ENABLE_CACHE", "true").lower() == "true",
    "cache_ttl": int(os.getenv("CACHE_TTL", "3600"))
}

# Configuración de caché
CACHE_CONFIG = {
    "enabled": os.getenv("ENABLE_CACHE", "true").lower() == "true",
    "cache_dir": os.getenv("CACHE_DIR", "cache"),
    "default_ttl_hours": int(os.getenv("CACHE_TTL_HOURS", "24")),
    "max_size_mb": int(os.getenv("CACHE_MAX_SIZE_MB", "500")),
    "auto_cleanup_days": int(os.getenv("CACHE_AUTO_CLEANUP_DAYS", "30"))
}

# Estimaciones de coste por modelo (costes actualizados octubre 2025)
COST_ESTIMATES = {
    "claude-sonnet-4-5-20250929": {
        "input_per_1k": 0.003,   # $3 / 1M tokens
        "output_per_1k": 0.015,  # $15 / 1M tokens
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },
    "claude-opus-4-20250514": {
        "input_per_1k": 0.015,   # $15 / 1M tokens
        "output_per_1k": 0.075,  # $75 / 1M tokens
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },
    "claude-sonnet-4-20250514": {
        "input_per_1k": 0.003,   # $3 / 1M tokens
        "output_per_1k": 0.015,  # $15 / 1M tokens
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },
    "gpt-4o": {
        "input_per_1k": 0.005,   # $5 / 1M tokens
        "output_per_1k": 0.015,  # $15 / 1M tokens
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },
    "gpt-4-turbo": {
        "input_per_1k": 0.010,   # $10 / 1M tokens
        "output_per_1k": 0.030,  # $30 / 1M tokens
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },
    "gpt-4": {
        "input_per_1k": 0.030,   # $30 / 1M tokens
        "output_per_1k": 0.060,  # $60 / 1M tokens
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    },
    "gpt-3.5-turbo": {
        "input_per_1k": 0.0005,  # $0.5 / 1M tokens
        "output_per_1k": 0.0015, # $1.5 / 1M tokens
        "avg_input_tokens": 10000,
        "avg_output_tokens": 5000
    }
}

def estimate_analysis_cost(model: str, num_keywords: int = 1000) -> Dict[str, Any]:
    """
    Estima el coste de un análisis basado en el modelo y número de keywords
    
    Args:
        model: Nombre del modelo (ej: 'claude-sonnet-4-5-20250929', 'gpt-4o')
        num_keywords: Número de keywords a analizar
        
    Returns:
        Dict con estimación de coste y tokens:
        {
            'cost': float,           # Coste total estimado en USD
            'input_tokens': int,     # Tokens de input estimados
            'output_tokens': int,    # Tokens de output estimados
            'input_cost': float,     # Coste de input en USD
            'output_cost': float     # Coste de output en USD
        }
    """
    if model not in COST_ESTIMATES:
        return {
            "cost": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "input_cost": 0,
            "output_cost": 0,
            "error": f"Modelo '{model}' no encontrado en estimaciones"
        }
    
    config = COST_ESTIMATES[model]
    
    # Escalar tokens basado en número de keywords
    # Asumimos escala lineal: 1000 keywords = tokens promedio configurados
    scale_factor = num_keywords / 1000
    input_tokens = int(config["avg_input_tokens"] * scale_factor)
    output_tokens = int(config["avg_output_tokens"] * scale_factor)
    
    # Calcular costes
    input_cost = (input_tokens / 1000) * config["input_per_1k"]
    output_cost = (output_tokens / 1000) * config["output_per_1k"]
    total_cost = input_cost + output_cost
    
    return {
        "cost": round(total_cost, 4),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": round(input_cost, 4),
        "output_cost": round(output_cost, 4)
    }

def compare_model_costs(num_keywords: int = 1000) -> Dict[str, Dict[str, Any]]:
    """
    Compara los costes de todos los modelos disponibles
    
    Args:
        num_keywords: Número de keywords para la comparación
        
    Returns:
        Dict con estimaciones por modelo
    """
    comparisons = {}
    
    for model in COST_ESTIMATES.keys():
        comparisons[model] = estimate_analysis_cost(model, num_keywords)
    
    return comparisons

# Configuración de visualización - Colores corporativos PC Componentes
VIZ_CONFIG = {
    "color_scheme": {
        1: "#FF6000",  # Naranja principal - Tier 1 (máxima prioridad)
        2: "#170453",  # Azul oscuro - Tier 2
        3: "#51437E",  # Azul medio - Tier 3
        4: "#8B81A9",  # Azul claro - Tier 4
        5: "#C5C0D4"   # Azul muy claro - Tier 5 (mínima prioridad)
    },
    "pc_colors": {
        "orange": "#FF6000",
        "orange_light": "#FF8640",
        "orange_lighter": "#FFD7BF",
        "blue_dark": "#090029",
        "blue_medium": "#170453",
        "blue_light": "#51437E",
        "blue_lighter": "#8B81A9",
        "blue_lightest": "#C5C0D4",
        "gray_dark": "#999999",
        "gray_medium": "#CCCCCC",
        "white": "#FFFFFF"
    },
    "default_chart_height": 600,
    "bubble_size_multiplier": 0.5
}

# Stopwords para análisis - Expansión multiidioma completa
STOPWORDS = {
    'en': [
        # Artículos
        'the', 'a', 'an',
        # Conjunciones
        'and', 'or', 'but', 'nor', 'yet', 'so',
        # Preposiciones
        'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up',
        'about', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'under', 'since', 'without', 'within', 'along',
        'toward', 'against', 'among', 'throughout', 'despite', 'towards',
        'upon', 'concerning', 'off', 'out', 'over', 'around', 'across',
        # Pronombres
        'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
        'we', 'us', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'i', 'me', 'my', 'mine', 'myself',
        'this', 'that', 'these', 'those',
        # Verbos auxiliares y comunes
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'having', 'do', 'does', 'did', 'doing', 'will', 'would',
        'should', 'could', 'might', 'must', 'can', 'may', 'shall',
        # Adverbios comunes
        'not', 'no', 'nor', 'too', 'very', 'just', 'now', 'then', 'there',
        'here', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
        'both', 'few', 'more', 'most', 'other', 'some', 'such',
        # Otros
        'as', 'if', 'than', 'because', 'while', 'who', 'what', 'which',
        'whom', 'whose', 'whether'
    ],
    
    'es': [
        # Artículos
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        # Conjunciones
        'y', 'e', 'o', 'u', 'pero', 'sino', 'aunque', 'mas', 'ni',
        # Preposiciones
        'en', 'de', 'del', 'por', 'para', 'con', 'sin', 'sobre', 'entre',
        'desde', 'hasta', 'hacia', 'durante', 'mediante', 'contra', 'bajo',
        'tras', 'ante', 'según', 'a', 'al',
        # Pronombres
        'él', 'ella', 'ellos', 'ellas', 'lo', 'le', 'les', 'se', 'me', 'te',
        'nos', 'os', 'yo', 'tú', 'tu', 'su', 'sus', 'mi', 'mis', 'nuestro',
        'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros',
        'vuestras', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos',
        'esas', 'aquel', 'aquella', 'aquellos', 'aquellas', 'esto', 'eso',
        'aquello', 'cual', 'cuales', 'quien', 'quienes',
        # Verbos auxiliares y comunes
        'es', 'son', 'ser', 'está', 'están', 'estar', 'era', 'eran', 'fue',
        'fueron', 'ha', 'han', 'haber', 'he', 'has', 'hay', 'había', 'habían',
        'siendo', 'sido', 'estando', 'estado', 'habiendo', 'habido',
        # Adverbios
        'no', 'sí', 'también', 'tampoco', 'muy', 'más', 'menos', 'mucho',
        'poco', 'ya', 'aún', 'todavía', 'siempre', 'nunca', 'ahora', 'entonces',
        'aquí', 'ahí', 'allí', 'donde', 'cuando', 'como', 'porque', 'si',
        'cada', 'todo', 'todos', 'toda', 'todas', 'otro', 'otra', 'otros',
        'otras', 'mismo', 'misma', 'mismos', 'mismas', 'tal', 'tales',
        # Otros
        'que', 'qué', 'cual', 'cuál', 'cuales', 'cuáles', 'algo', 'alguien',
        'alguno', 'alguna', 'algunos', 'algunas', 'ninguno', 'ninguna',
        'nada', 'nadie'
    ],
    
    'fr': [
        # Articles
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'au', 'aux',
        # Conjonctions
        'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car',
        # Prépositions
        'de', 'à', 'en', 'dans', 'par', 'pour', 'avec', 'sans', 'sur',
        'sous', 'vers', 'chez', 'contre', 'entre', 'parmi', 'pendant',
        'depuis', 'avant', 'après', 'devant', 'derrière', 'durant', 'dès',
        'jusque', 'hors', 'hormis', 'malgré', 'selon', 'sauf', 'outre',
        'envers', 'travers',
        # Pronoms
        'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
        'me', 'te', 'se', 'le', 'la', 'les', 'lui', 'leur', 'eux',
        'moi', 'toi', 'soi', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes',
        'son', 'sa', 'ses', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs',
        'ce', 'cet', 'cette', 'ces', 'celui', 'celle', 'ceux', 'celles',
        'ceci', 'cela', 'ça', 'quel', 'quelle', 'quels', 'quelles',
        'qui', 'que', 'quoi', 'dont', 'où',
        # Verbes auxiliaires et communs
        'être', 'avoir', 'faire', 'dire', 'aller', 'voir', 'savoir',
        'pouvoir', 'vouloir', 'venir', 'devoir', 'prendre', 'trouver',
        'donner', 'falloir', 'parler', 'mettre', 'passer', 'croire',
        'est', 'sont', 'était', 'étaient', 'été', 'étant', 'suis', 'es',
        'a', 'ont', 'avait', 'avaient', 'eu', 'ayant', 'ai', 'as',
        'fait', 'font', 'faisait', 'faisaient', 'faisant',
        # Adverbes
        'ne', 'pas', 'non', 'plus', 'aussi', 'très', 'bien', 'encore',
        'déjà', 'jamais', 'toujours', 'souvent', 'parfois', 'maintenant',
        'alors', 'ainsi', 'donc', 'puis', 'ensuite', 'enfin', 'ici', 'là',
        'tout', 'tous', 'toute', 'toutes', 'même', 'mêmes', 'autre', 'autres',
        'quelque', 'quelques', 'plusieurs', 'chaque', 'certain', 'certains',
        'certaine', 'certaines', 'tel', 'telle', 'tels', 'telles',
        # Autres
        'si', 'y', 'en', 'on', 'quand', 'comme', 'comment', 'pourquoi',
        'combien', 'rien', 'personne', 'aucun', 'aucune', 'nul', 'nulle'
    ],
    
    'pt': [
        # Artigos (Português de Portugal)
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
        # Conjunções
        'e', 'ou', 'mas', 'porém', 'contudo', 'todavia', 'entretanto',
        'porque', 'pois', 'logo', 'portanto', 'nem', 'que', 'se',
        # Preposições
        'de', 'a', 'em', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
        'após', 'ante', 'até', 'contra', 'desde', 'durante', 'entre',
        'mediante', 'perante', 'segundo', 'trás', 'do', 'da', 'dos',
        'das', 'ao', 'aos', 'à', 'às', 'no', 'na', 'nos', 'nas',
        'pelo', 'pela', 'pelos', 'pelas', 'dum', 'duma', 'duns', 'dumas',
        'num', 'numa', 'nuns', 'numas',
        # Pronomes
        'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas',
        'me', 'te', 'se', 'lhe', 'lhes', 'o', 'a', 'os', 'as',
        'mim', 'ti', 'si', 'meu', 'minha', 'meus', 'minhas',
        'teu', 'tua', 'teus', 'tuas', 'seu', 'sua', 'seus', 'suas',
        'nosso', 'nossa', 'nossos', 'nossas', 'vosso', 'vossa',
        'vossos', 'vossas', 'este', 'esta', 'estes', 'estas',
        'esse', 'essa', 'esses', 'essas', 'aquele', 'aquela',
        'aqueles', 'aquelas', 'isto', 'isso', 'aquilo',
        'qual', 'quais', 'quem', 'que', 'onde', 'quanto', 'quanta',
        'quantos', 'quantas',
        # Verbos auxiliares e comuns
        'ser', 'estar', 'ter', 'haver', 'fazer', 'poder', 'dizer',
        'ir', 'ver', 'dar', 'saber', 'querer', 'ficar', 'pôr',
        'vir', 'levar', 'passar', 'trazer', 'deixar', 'pensar',
        'é', 'são', 'era', 'eram', 'foi', 'foram', 'sido', 'sendo',
        'está', 'estão', 'estava', 'estavam', 'esteve', 'estiveram',
        'estado', 'estando', 'tem', 'têm', 'tinha', 'tinham',
        'teve', 'tiveram', 'tido', 'tendo', 'há', 'havia', 'houve',
        'houveram', 'havido', 'havendo',
        # Advérbios
        'não', 'sim', 'também', 'já', 'ainda', 'mais', 'menos',
        'muito', 'pouco', 'bastante', 'sempre', 'nunca', 'jamais',
        'talvez', 'quiçá', 'porventura', 'acaso', 'agora', 'então',
        'hoje', 'ontem', 'amanhã', 'cedo', 'tarde', 'antes', 'depois',
        'logo', 'aqui', 'aí', 'ali', 'lá', 'cá', 'acolá', 'donde',
        'aonde', 'bem', 'mal', 'melhor', 'pior', 'assim', 'como',
        'quando', 'onde', 'só', 'somente', 'apenas',
        # Outros
        'todo', 'toda', 'todos', 'todas', 'outro', 'outra', 'outros',
        'outras', 'mesmo', 'mesma', 'mesmos', 'mesmas', 'próprio',
        'própria', 'próprios', 'próprias', 'algum', 'alguma', 'alguns',
        'algumas', 'nenhum', 'nenhuma', 'nenhuns', 'nenhumas', 'tal',
        'tais', 'tanto', 'tanta', 'tantos', 'tantas', 'quanto', 'quanta',
        'quantos', 'quantas', 'cada', 'qualquer', 'quaisquer',
        'nada', 'ninguém', 'alguém', 'algo', 'tudo', 'outrem'
    ],
    
    'it': [
        # Articoli
        'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una',
        'del', 'dello', 'della', 'dei', 'degli', 'delle',
        'al', 'allo', 'alla', 'ai', 'agli', 'alle',
        'dal', 'dallo', 'dalla', 'dai', 'dagli', 'dalle',
        'nel', 'nello', 'nella', 'nei', 'negli', 'nelle',
        'sul', 'sullo', 'sulla', 'sui', 'sugli', 'sulle',
        # Congiunzioni
        'e', 'ed', 'o', 'od', 'ma', 'però', 'oppure', 'ossia', 'ovvero',
        'cioè', 'né', 'anche', 'pure', 'inoltre', 'tuttavia', 'eppure',
        'anzi', 'dunque', 'quindi', 'pertanto', 'infatti', 'perciò',
        # Preposizioni
        'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra',
        'sopra', 'sotto', 'dentro', 'fuori', 'davanti', 'dietro',
        'presso', 'lungo', 'verso', 'contro', 'durante', 'mediante',
        'tramite', 'circa', 'oltre', 'senza', 'secondo', 'prima',
        'dopo', 'attraverso', 'fino',
        # Pronomi
        'io', 'tu', 'egli', 'lui', 'ella', 'lei', 'esso', 'essa',
        'noi', 'voi', 'essi', 'esse', 'loro', 'me', 'te', 'mi', 'ti',
        'si', 'ci', 'vi', 'lo', 'la', 'li', 'le', 'ne', 'gli',
        'mio', 'mia', 'miei', 'mie', 'tuo', 'tua', 'tuoi', 'tue',
        'suo', 'sua', 'suoi', 'sue', 'nostro', 'nostra', 'nostri',
        'nostre', 'vostro', 'vostra', 'vostri', 'vostre',
        'questo', 'questa', 'questi', 'queste', 'codesto', 'codesta',
        'codesti', 'codeste', 'quello', 'quella', 'quelli', 'quelle',
        'ciò', 'chi', 'che', 'quale', 'quali', 'quanto', 'quanta',
        'quanti', 'quante', 'cui',
        # Verbi ausiliari e comuni
        'essere', 'avere', 'fare', 'dire', 'andare', 'stare', 'dare',
        'venire', 'potere', 'dovere', 'volere', 'sapere', 'vedere',
        'prendere', 'uscire', 'mettere', 'parlare', 'trovare',
        'è', 'sono', 'era', 'erano', 'stato', 'stata', 'stati', 'state',
        'essendo', 'sia', 'siano', 'fosse', 'fossero', 'sarà', 'saranno',
        'ha', 'hanno', 'aveva', 'avevano', 'avuto', 'avuta', 'avuti',
        'avute', 'avendo', 'abbia', 'abbiano', 'avesse', 'avessero',
        'avrà', 'avranno', 'fa', 'fanno', 'fece', 'fecero', 'fatto',
        'fatta', 'fatti', 'fatte', 'facendo',
        # Avverbi
        'non', 'sì', 'no', 'anche', 'ancora', 'già', 'mai', 'più',
        'sempre', 'spesso', 'molto', 'poco', 'troppo', 'tanto', 'quanto',
        'assai', 'abbastanza', 'bene', 'male', 'meglio', 'peggio',
        'ora', 'adesso', 'allora', 'poi', 'prima', 'dopo', 'subito',
        'presto', 'tardi', 'oggi', 'ieri', 'domani', 'qui', 'qua',
        'lì', 'là', 'lassù', 'quaggiù', 'dove', 'ovunque', 'dovunque',
        'come', 'così', 'altrimenti', 'altrimenti', 'forse', 'magari',
        'quasi', 'appena', 'solo', 'solamente', 'soltanto',
        # Altri
        'tutto', 'tutta', 'tutti', 'tutte', 'altro', 'altra', 'altri',
        'altre', 'stesso', 'stessa', 'stessi', 'stesse', 'medesimo',
        'medesima', 'medesimi', 'medesime', 'tale', 'tali', 'alcuno',
        'alcuna', 'alcuni', 'alcune', 'nessuno', 'nessuna', 'ciascuno',
        'ciascuna', 'ogni', 'qualche', 'qualcuno', 'qualcuna',
        'niente', 'nulla', 'qualcosa', 'chiunque', 'quando', 'mentre',
        'perché', 'poiché', 'siccome', 'sebbene', 'benché', 'affinché',
        'purché', 'qualora', 'se'
    ]
}

# Configuración de exportación
EXPORT_CONFIG = {
    "excel_engine": "openpyxl",
    "csv_encoding": "utf-8",
    "include_index": False,
    "formats": {
        "excel": {
            "extension": ".xlsx",
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        "csv": {
            "extension": ".csv",
            "mime_type": "text/csv"
        },
        "json": {
            "extension": ".json",
            "mime_type": "application/json"
        }
    }
}

# Mensajes y textos de la UI
UI_MESSAGES = {
    "welcome": "👋 Bienvenido al Keyword Universe Analyzer",
    "upload_prompt": "Sube tus archivos de keywords para comenzar",
    "analyzing": "🧠 Analizando tus keywords con IA...",
    "success": "✅ Análisis completado exitosamente",
    "error": "❌ Ocurrió un error durante el análisis",
    "no_data": "📁 No hay datos disponibles. Por favor carga archivos primero.",
    "api_key_missing": "⚠️ Por favor configura tu API key en la barra lateral",
    "processing": "⚙️ Procesando datos...",
    "validating": "🔍 Validando configuración...",
    "exporting": "💾 Exportando resultados..."
}

# Validación de configuración
def validate_config() -> Dict[str, Any]:
    """
    Valida que la configuración esté correcta y completa
    
    Returns:
        Dict con resultado de validación:
        {
            'valid': bool,
            'issues': List[str],
            'warnings': List[str]
        }
    """
    issues = []
    warnings = []
    
    # Validar API keys
    if not ANTHROPIC_API_KEY:
        warnings.append("ANTHROPIC_API_KEY no está configurada")
    
    if not OPENAI_API_KEY:
        warnings.append("OPENAI_API_KEY no está configurada (opcional)")
    
    if not SEMRUSH_API_KEY:
        warnings.append("SEMRUSH_API_KEY no está configurada (opcional)")
    
    # Validar configuración de análisis
    if ANALYSIS_CONFIG["max_keywords_per_file"] < 100:
        issues.append("max_keywords_per_file debe ser al menos 100")
    
    if ANALYSIS_CONFIG["default_tiers"] < 2 or ANALYSIS_CONFIG["default_tiers"] > 5:
        issues.append("default_tiers debe estar entre 2 y 5")
    
    if ANALYSIS_CONFIG["min_volume"] < 0:
        issues.append("min_volume no puede ser negativo")
    
    # Validar directorios
    required_dirs = [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]
    for directory in required_dirs:
        if not directory.exists():
            warnings.append(f"Directorio no existe: {directory}")
    
    # Validar configuración de caché
    if CACHE_CONFIG["enabled"]:
        cache_dir = Path(CACHE_CONFIG["cache_dir"])
        if not cache_dir.exists():
            warnings.append(f"Directorio de caché no existe: {cache_dir}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "config_complete": len(warnings) == 0
    }

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "detailed",
            "level": "DEBUG"
        },
        "error_file": {
            "class": "logging.FileHandler",
            "filename": "logs/errors.log",
            "formatter": "detailed",
            "level": "ERROR"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        }
    }
}

# Crear directorio de logs si no existe
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

# Info del sistema (útil para debugging)
SYSTEM_INFO = {
    "base_dir": str(BASE_DIR),
    "data_dir": str(DATA_DIR),
    "output_dir": str(OUTPUT_DIR),
    "python_version": os.sys.version,
    "platform": os.sys.platform
}

def get_config_summary() -> str:
    """
    Retorna un resumen legible de la configuración actual
    
    Returns:
        String con resumen de configuración
    """
    validation = validate_config()
    
    summary = f"""
╔════════════════════════════════════════════════════════╗
║   KEYWORD UNIVERSE ANALYZER - CONFIGURACIÓN           ║
╚════════════════════════════════════════════════════════╝

📊 APLICACIÓN:
   Versión: {APP_CONFIG['version']}
   Autor: {APP_CONFIG['author']}

🔑 API KEYS:
   Anthropic: {'✓ Configurada' if ANTHROPIC_API_KEY else '✗ No configurada'}
   OpenAI: {'✓ Configurada' if OPENAI_API_KEY else '✗ No configurada'}
   Semrush: {'✓ Configurada' if SEMRUSH_API_KEY else '✗ No configurada'}

⚙️ ANÁLISIS:
   Max keywords/archivo: {ANALYSIS_CONFIG['max_keywords_per_file']:,}
   Tiers por defecto: {ANALYSIS_CONFIG['default_tiers']}
   Volumen mínimo: {ANALYSIS_CONFIG['min_volume']}

💾 CACHÉ:
   Habilitada: {'Sí' if CACHE_CONFIG['enabled'] else 'No'}
   TTL: {CACHE_CONFIG['default_ttl_hours']} horas

📁 DIRECTORIOS:
   Base: {BASE_DIR}
   Datos: {DATA_DIR}
   Salida: {OUTPUT_DIR}

🌍 IDIOMAS STOPWORDS:
   Disponibles: {', '.join(STOPWORDS.keys())}
   Total palabras: {sum(len(words) for words in STOPWORDS.values())}

✅ VALIDACIÓN:
   Estado: {'✓ Válida' if validation['valid'] else '✗ Con errores'}
   Issues: {len(validation['issues'])}
   Warnings: {len(validation['warnings'])}
"""
    
    if validation['issues']:
        summary += "\n❌ ERRORES:\n"
        for issue in validation['issues']:
            summary += f"   - {issue}\n"
    
    if validation['warnings']:
        summary += "\n⚠️ ADVERTENCIAS:\n"
        for warning in validation['warnings']:
            summary += f"   - {warning}\n"
    
    return summary

# Ejecutar validación al importar (solo en desarrollo)
if os.getenv("ENV") == "development":
    validation = validate_config()
    if not validation['valid']:
        import warnings
        warnings.warn(f"Configuración con errores: {validation['issues']}")
