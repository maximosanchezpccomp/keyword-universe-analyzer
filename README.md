# 🌌 Keyword Universe Analyzer

Herramienta profesional de análisis SEO que utiliza IA (Claude de Anthropic) para crear universos de keywords completos y estratégicos. Automatiza el proceso de análisis competitivo y agrupación temática de keywords.

## 🎯 Características

- ✅ **Carga múltiple de archivos**: Soporta CSV y Excel de Ahrefs, Semrush y otras herramientas SEO
- 🤖 **Análisis con IA flexible**: 
  - Claude Sonnet 4.5 para análisis profundo y estratégico
  - GPT-4o/GPT-4 Turbo para análisis rápido y económico
  - Validación cruzada con ambos modelos
- 🔍 **Integración Semrush**: Obtén keywords directamente desde la API
- 📊 **Visualizaciones interactivas**: Bubble charts, treemaps, sunburst y más
- 🎯 **Agrupación inteligente**: Agrupa keywords por temas, intención o funnel
- 📈 **Detección de tendencias**: Identifica keywords emergentes y oportunidades
- 💾 **Exportación flexible**: Excel, CSV o JSON con todos los insights
- 🔒 **Seguro**: Tus datos nunca salen de tu máquina excepto para las llamadas API

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.9 o superior
- Cuenta de Anthropic (para API de Claude)
- (Opcional) Cuenta de Semrush

### Instalación

1. **Clona el repositorio**
```bash
git clone https://github.com/tu-usuario/keyword-universe-analyzer.git
cd keyword-universe-analyzer
```

2. **Crea un entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

4. **Configura las variables de entorno**
```bash
cp .env.example .env
# Edita .env con tu editor favorito y añade tus API keys
```

5. **Ejecuta la aplicación**
```bash
streamlit run app/main.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

## 📖 Uso

### 1. Carga de Datos

#### Opción A: Archivos locales
- Sube archivos CSV o Excel exportados de Ahrefs, Semrush, etc.
- La herramienta detectará automáticamente las columnas relevantes
- Soporta múltiples archivos simultáneamente

#### Opción B: API de Semrush
- Ingresa tu API key en la barra lateral
- Lista los dominios competidores (uno por línea)
- Haz clic en "Obtener Keywords"

### 2. Análisis con IA

1. Configura los parámetros:
   - **Tipo de agrupación**: Temática, Intención o Funnel
   - **Número de tiers**: 2-5 niveles de prioridad
   - **Opciones avanzadas**: Análisis semántico, tendencias, gaps

2. Añade instrucciones personalizadas (opcional):
   - "Enfócate en keywords transaccionales"
   - "Agrupa por categoría de producto"
   - "Identifica keywords B2B vs B2C"

3. Haz clic en "Analizar con Claude"

### 3. Visualización

Explora tu Keyword Universe con:
- **Bubble Chart**: Visión general del universo completo
- **Treemap**: Distribución de volumen por topic
- **Sunburst**: Jerarquía de tiers y topics
- **Matriz de prioridad**: Volumen vs dificultad

### 4. Exportación

Descarga tus resultados en:
- **Excel**: Con múltiples hojas y gráficos integrados
- **CSV**: Para procesamiento adicional
- **JSON**: Para integración con otras herramientas

## 📁 Estructura del Proyecto

```
keyword-universe-analyzer/
├── app/
│   ├── main.py                    # Aplicación principal
│   ├── components/
│   │   ├── data_processor.py      # Procesamiento de datos
│   │   └── visualizer.py          # Visualizaciones
│   ├── services/
│   │   ├── anthropic_service.py   # Integración Claude
│   │   ├── openai_service.py      # Integración OpenAI (opcional)
│   │   └── semrush_service.py     # Integración Semrush
│   └── utils/
│       ├── helpers.py              # Funciones auxiliares
│       └── prompts.py              # Templates de prompts
├── data/
│   ├── raw/                        # Datos originales
│   └── processed/                  # Datos procesados
├── tests/                          # Tests unitarios
├── .env.example                    # Plantilla de variables
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔧 Configuración Avanzada

### Personalización del Prompt

Edita `app/utils/prompts.py` para personalizar cómo Claude analiza tus keywords:

```python
CUSTOM_PROMPT_TEMPLATE = """
Tu prompt personalizado aquí...
"""
```

### Añadir Nuevas Fuentes de Datos

1. Añade un nuevo servicio en `app/services/`
2. Implementa el método `get_organic_keywords()`
3. Integra en `app/components/data_processor.py`

### Visualizaciones Personalizadas

Extiende `KeywordVisualizer` en `app/components/visualizer.py`:

```python
def create_custom_chart(self, topics_df: pd.DataFrame) -> go.Figure:
    # Tu código aquí
    pass
```

## 🤝 Casos de Uso

### 1. Análisis Competitivo
Identifica gaps de contenido comparando tu sitio con competidores:
```python
competitors = ["competitor1.com", "competitor2.com", "competitor3.com"]
# Carga keywords de cada competidor y analiza
```

### 2. Planificación de Contenido
Genera un plan de contenido basado en volumen y oportunidad:
- Tier 1: Contenido prioritario (alto volumen)
- Tier 2: Contenido de soporte
- Tier 3: Long-tail específico

### 3. Estrategia de Link Building
Identifica topics de alta autoridad para estrategias de enlaces:
- Analiza keywords con alto CPC
- Filtra por intención comercial
- Prioriza por dificultad

## 📊 Ejemplos de Resultados

### Output de Análisis
```json
{
  "summary": "Se identificaron 45 topics principales...",
  "topics": [
    {
      "topic": "E-Signature Software",
      "tier": 1,
      "keyword_count": 342,
      "volume": 424760,
      "traffic": 127428,
      "priority": "high",
      "description": "Keywords relacionadas con software de firma electrónica..."
    }
  ],
  "gaps": [
    {
      "topic": "API Integration",
      "volume": 50000,
      "description": "Oportunidad de contenido técnico..."
    }
  ]
}
```

## 🧪 Testing

Ejecuta los tests:
```bash
pytest tests/ -v --cov=app
```

## 🤖 APIs Soportadas

### Anthropic (Claude)
- **Modelos recomendados**: 
  - `claude-sonnet-4-5-20250929` (Más inteligente, análisis profundo)
  - `claude-opus-4-20250514` (Alternativa premium)
- **Uso**: Análisis semántico y agrupación estratégica de keywords
- **Costos**: ~$0.15-0.30 por análisis de 1,000 keywords
- **Cuándo usar**: Estrategia compleja, análisis profundo, reportes para clientes

### OpenAI
- **Modelos recomendados**:
  - `gpt-4o` (Más rápido y económico)
  - `gpt-4-turbo` (Balance calidad-velocidad)
- **Uso**: Análisis rápido, exploratorio y económico
- **Costos**: ~$0.10-0.20 por análisis de 1,000 keywords
- **Cuándo usar**: Quick wins, análisis exploratorio, presupuesto limitado

### Validación Cruzada (Ambos)
- **Uso**: Máxima confianza en resultados
- **Costos**: Suma de ambos (~$0.25-0.50)
- **Cuándo usar**: Decisiones importantes, grandes inversiones

📚 **Ver comparación detallada**: [docs/AI_PROVIDERS_COMPARISON.md](docs/AI_PROVIDERS_COMPARISON.md)

## 🔐 Seguridad y Privacidad

- ✅ Las API keys se almacenan en `.env` (git-ignored)
- ✅ Los datos se procesan localmente
- ✅ Solo se envían muestras de keywords a las APIs
- ✅ Sin tracking ni analytics

## 📝 Roadmap

- [ ] Integración con Google Search Console
- [ ] Análisis de tendencias históricas
- [ ] Alertas automáticas de oportunidades
- [ ] Dashboard multi-proyecto
- [ ] Exportación a Data Studio
- [ ] CLI para automatización

## 🐛 Solución de Problemas

### Error: "API key no válida"
- Verifica que tu `.env` esté configurado correctamente
- Revisa que la API key sea válida en el dashboard correspondiente

### Error: "No se pueden leer los archivos"
- Asegúrate de que los archivos tengan columnas: `keyword`, `volume`
- Prueba con archivos de ejemplo en `/data/raw/`

### La aplicación se cierra inesperadamente
- Revisa los logs en la terminal
- Asegúrate de tener suficiente memoria (datasets grandes)

## 🤝 Contribución

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@maximosanchezpccomp](https://github.com/maximosanchezpccomp)
- LinkedIn: [Max Sanchez](https://linkedin.com/in/max-sanchez-tendero)

## 🙏 Agradecimientos

- Basado en el concepto de [Kevin Indig](https://www.kevin-indig.com/)
- Inspirado en el artículo de [Nectiv Digital](https://nectivdigital.com/)
- Powered by [Anthropic Claude](https://www.anthropic.com/)

## 📞 Soporte

¿Necesitas ayuda? 
- 📧 Email: maximo.sanchez@pccomponentes.com

---

⭐ Si este proyecto te resultó útil, considera darle una estrella en GitHub!
