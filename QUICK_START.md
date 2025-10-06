# 🚀 Guía Rápida - Keyword Universe Analyzer

Esta guía te ayudará a empezar a usar la herramienta en menos de 10 minutos.

## ⚡ Instalación Rápida

### Opción 1: Con Script Automático (Recomendado)

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/keyword-universe-analyzer.git
cd keyword-universe-analyzer

# 2. Ejecuta el script de setup
bash setup.sh

# 3. Edita tu archivo .env
nano .env
# Añade tu ANTHROPIC_API_KEY

# 4. Inicia la aplicación
streamlit run app/main.py
```

### Opción 2: Manual

```bash
# 1. Clona y navega al directorio
git clone https://github.com/tu-usuario/keyword-universe-analyzer.git
cd keyword-universe-analyzer

# 2. Crea entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Configura .env
cp .env.example .env
# Edita .env y añade tus API keys

# 5. Ejecuta
streamlit run app/main.py
```

### Opción 3: Con Docker

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/keyword-universe-analyzer.git
cd keyword-universe-analyzer

# 2. Crea archivo .env con tus API keys
cp .env.example .env
nano .env

# 3. Construye y ejecuta con Docker Compose
docker-compose up -d

# 4. Accede a http://localhost:8501
```

## 🎯 Primer Análisis en 5 Pasos

### Paso 1: Obtén tus Datos de Keywords

Tienes dos opciones:

**A. Exporta desde Ahrefs/Semrush:**
1. Ve a tu herramienta SEO favorita
2. Busca el dominio competidor
3. Ve a "Organic Keywords"
4. Filtra "Non-branded"
5. Exporta a CSV o Excel

**B. Usa la API de Semrush (incluida en la app):**
- Solo necesitas tu API key

### Paso 2: Abre la Aplicación

```bash
streamlit run app/main.py
```

Se abrirá automáticamente en `http://localhost:8501`

### Paso 3: Configura tu API Key

En la barra lateral:
1. Expande "🔑 API Keys"
2. Pega tu Anthropic API Key
3. (Opcional) Añade tu Semrush API Key

### Paso 4: Carga tus Datos

**Opción A - Archivos locales:**
1. Ve a la pestaña "📁 Carga de Datos"
2. Arrastra o selecciona tus archivos CSV/Excel
3. Revisa el preview de los datos

**Opción B - Semrush API:**
1. Ve a "Opción 2: Semrush API"
2. Lista tus competidores (uno por línea):
   ```
   competitor1.com
   competitor2.com
   competitor3.com
   ```
3. Haz clic en "🔍 Obtener Keywords"

### Paso 5: Analiza con Claude

1. Ve a la pestaña "🧠 Análisis con IA"
2. Configura los parámetros:
   - **Tipo de agrupación**: Temática (recomendado para empezar)
   - **Número de tiers**: 3
3. Haz clic en "🚀 Analizar con Claude"
4. Espera 30-60 segundos
5. ¡Listo! Explora tus resultados

## 📊 Entendiendo los Resultados

### Resumen Ejecutivo
- Visión general del análisis
- Insights principales
- Recomendaciones estratégicas

### Topics por Tier

**Tier 1**: Máxima prioridad
- Alto volumen de búsqueda
- Alta relevancia estratégica
- Oportunidad de impacto inmediato

**Tier 2**: Prioridad media
- Volumen moderado
- Importancia complementaria
- Construyen autoridad temática

**Tier 3**: Long-tail y específico
- Menor volumen individual
- Alta especificidad
- Fácil de rankear

### Métricas Clave

- **Keyword Count**: Número de keywords en el topic
- **Volume**: Volumen total de búsqueda mensual
- **Traffic**: Tráfico estimado potencial
- **Priority**: Nivel de prioridad estratégica

## 🎨 Visualizaciones

### Bubble Chart
- **Eje X**: Número de keywords
- **Eje Y**: Volumen total
- **Tamaño**: Tráfico potencial
- **Color**: Tier

**Cómo usarlo**: Busca burbujas grandes en la esquina superior derecha (muchas keywords + alto volumen).

### Treemap
Muestra la distribución proporcional de volumen por topic.

**Cómo usarlo**: Los rectángulos más grandes = mayor volumen = mayor oportunidad.

### Sunburst
Vista jerárquica de tiers y topics.

**Cómo usarlo**: Navega desde el centro (tiers) hacia afuera (topics).

## 💾 Exportar Resultados

1. Ve a la pestaña "📥 Exportar"
2. Selecciona formato:
   - **Excel**: Múltiples hojas, con formato
   - **CSV**: Para procesamiento adicional
   - **JSON**: Para integración técnica
3. Haz clic en "💾 Generar archivo"
4. Descarga tu archivo

## 🔥 Tips Avanzados

### 1. Análisis por Intención
```
Tipo de agrupación: "Intención de búsqueda"
```
Agrupa por: Informacional, Navegacional, Comercial, Transaccional

**Cuándo usar**: Cuando quieres optimizar el funnel de conversión.

### 2. Análisis de Funnel
```
Tipo de agrupación: "Funnel de conversión"
```
Agrupa por: TOFU, MOFU, BOFU

**Cuándo usar**: Cuando planificas contenido para todo el customer journey.

### 3. Instrucciones Personalizadas
Añade contexto específico de tu negocio:

```
Enfócate en keywords B2B
Prioriza términos técnicos
Agrupa por categoría de producto: X, Y, Z
```

### 4. Análisis Profundo
Activa todas las opciones avanzadas:
- ✅ Análisis semántico profundo
- ✅ Identificar tendencias emergentes
- ✅ Detectar gaps de contenido

**Nota**: Esto aumenta el tiempo de análisis pero da insights más profundos.

## 🎯 Casos de Uso Específicos

### Caso 1: Nueva Estrategia de Contenido

**Objetivo**: Identificar qué contenido crear primero.

```
1. Carga keywords de 3-5 competidores
2. Análisis tipo: Temática
3. Tiers: 3
4. Analiza con Claude
5. Exporta a Excel
6. Crea calendario de contenido desde Tier 1
```

### Caso 2: Encontrar Quick Wins

**Objetivo**: Keywords fáciles de rankear con buen volumen.

```
1. Análisis tipo: Intención → Comercial
2. Filtra en visualización por:
   - Volumen medio-alto
   - Tier 2-3 (menos competencia)
3. Identifica topics específicos
4. Crea contenido optimizado
```

### Caso 3: Análisis Competitivo

**Objetivo**: Ver gaps vs competencia.

```
1. Carga keywords de competidores principales
2. Activa: ✅ Detectar gaps de contenido
3. Ve a pestaña Visualización
4. Revisa sección "Oportunidades de Contenido"
5. Prioriza gaps con alto volumen
```

## 🐛 Solución de Problemas

### "Error: API key no válida"
**Solución**: 
- Ve a https://console.anthropic.com/
- Genera nueva API key
- Cópiala completa (empieza con `sk-ant-`)

### "No se pueden leer los archivos"
**Solución**:
- Verifica que el CSV tenga headers
- Debe tener al menos: `keyword` y `volume`
- Prueba exportar de nuevo desde tu herramienta

### "La app se cierra inesperadamente"
**Solución**:
- Revisa los logs en la terminal
- Datasets muy grandes (>10K keywords) pueden causar problemas de memoria
- Reduce el número de keywords por archivo

### "Análisis muy lento"
**Solución**:
- Reduce `max_keywords` en configuración
- Usa menos tiers (2 en vez de 5)
- Desactiva opciones avanzadas

## 📚 Recursos Adicionales

- [Documentación completa](README.md)
- [Ejemplos de prompts](app/utils/prompts.py)
- [API de Anthropic](https://docs.anthropic.com)
- [API de Semrush](https://www.semrush.com/api-analytics/)

## 🤝 Siguiente Nivel

Una vez que domines los básicos:

1. **Personaliza prompts** en `app/utils/prompts.py`
2. **Añade nuevas visualizaciones** en `app/components/visualizer.py`
3. **Integra más fuentes de datos** (Google Search Console, etc.)
4. **Automatiza** con GitHub Actions o cron jobs
5. **Comparte** tus mejoras con la comunidad

---

¿Preguntas? Abre un issue en GitHub o contáctanos.

**¡Feliz análisis de keywords! 🚀**
