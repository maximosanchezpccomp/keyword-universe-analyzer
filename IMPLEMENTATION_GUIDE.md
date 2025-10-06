# 🎨 Guía de Implementación - Branding PC Componentes

## 📋 Resumen de Cambios

Se ha actualizado la aplicación **Keyword Universe Analyzer** con el branding corporativo completo de PC Componentes, incluyendo:

✅ Paleta de colores corporativos
✅ Diseño de UI coherente y profesional
✅ Integración del logo
✅ Visualizaciones con colores de marca
✅ Accesibilidad y usabilidad mejoradas

---

## 🚀 Implementación Rápida (5 minutos)

### Paso 1: Actualizar Archivos
```bash
# Si ya tienes el repositorio clonado
git pull origin main

# O descarga los archivos actualizados
```

### Paso 2: Añadir el Logo
```bash
# Opción A: Si tienes el logo
mkdir -p assets
cp /ruta/a/tu/logo.png assets/pc_logo.png

# Opción B: Usar el script automático
python scripts/add_logo.py /ruta/a/tu/logo.png

# Opción C: Crear placeholder mientras consigues el logo
python scripts/add_logo.py
```

### Paso 3: Verificar Configuración
```bash
# Asegúrate de que existe .streamlit/config.toml
ls .streamlit/config.toml

# Si no existe, créalo (ya está incluido en los archivos)
```

### Paso 4: Ejecutar
```bash
streamlit run app/main.py
```

¡Listo! La aplicación debería tener el nuevo branding de PC Componentes.

---

## 📁 Archivos Modificados

### Archivos de Configuración

1. **`.streamlit/config.toml`** ✅ NUEVO
   - Colores principales de Streamlit
   - Tema personalizado
   
2. **`config.py`** ✅ MODIFICADO
   - Colores en VIZ_CONFIG actualizados
   - Paleta completa PC Componentes

### Archivos de Código

3. **`app/main.py`** ✅ MODIFICADO
   - CSS personalizado completo
   - Header con logo
   - Branding en toda la UI
   
4. **`app/components/visualizer.py`** ✅ MODIFICADO
   - Colores PC en gráficos
   - Esquema de colores por tier
   
5. **`app/__init__.py`** ✅ MODIFICADO
   - Info corporativa actualizada

### Documentación Nueva

6. **`docs/BRANDING_SETUP.md`** ✅ NUEVO
   - Guía completa de branding
   - Especificaciones de colores
   - Reglas de uso

7. **`scripts/add_logo.py`** ✅ NUEVO
   - Script para preparar logos
   - Optimización automática
   - Generación de favicon

---

## 🎨 Colores Implementados

### Visualización de Paleta

```
NARANJA (Principal)
████ #FF6000 - Naranja principal (Tier 1, CTAs)
████ #FF8640 - Naranja claro (Hover, gradientes)
████ #FFD7BF - Naranja muy claro (Backgrounds)

AZUL MEDIO
████ #170453 - Azul oscuro (Sidebar, Tier 2)
████ #51437E - Azul medio (Tier 3)
████ #8B81A9 - Azul claro (Tier 4)
████ #C5C0D4 - Azul muy claro (Tier 5)

AZUL OSCURO
████ #090029 - Azul oscuro principal (Textos)
████ #46405E - Azul oscuro medio
████ #848094 - Azul gris
████ #C1BFC9 - Azul gris claro

NEUTROS
████ #FFFFFF - Blanco (Backgrounds)
████ #CCCCCC - Gris medio (Borders)
████ #999999 - Gris oscuro (Textos secundarios)
```

---

## 🖼️ Estructura de Assets

Crea esta estructura:

```
assets/
├── pc_logo.png          # Logo principal (usado en header)
├── pc_logo_small.png    # Logo pequeño (generado automáticamente)
└── favicon.ico          # Favicon (generado automáticamente)
```

### Especificaciones del Logo

**Logo Principal (`pc_logo.png`):**
- Formato: PNG con transparencia
- Tamaño recomendado: 400x150px
- Se mostrará a 120px de ancho
- Fondo transparente

**Generación Automática:**
Si usas el script `add_logo.py`, se generan automáticamente:
- Logo principal optimizado
- Logo pequeño (150px)
- Favicon (32x32px ICO)

---

## 🎯 Elementos de UI Actualizados

### Header
- Logo PC Componentes (izquierda)
- Título con gradiente naranja
- Subtítulo con color azul medio

### Sidebar
- Fondo degradado azul oscuro
- Textos en blanco
- Labels destacados en naranja claro
- Expanders con fondo naranja translúcido

### Botones
- **Primarios:** Gradiente naranja (#FF6000 → #FF8640)
- **Hover:** Efecto de elevación y sombra
- **Estados claros:** Cambio de color y transformación

### Tabs
- Tab activa: Gradiente naranja con texto blanco
- Tab normal: Texto azul oscuro
- Hover: Fondo naranja claro

### Métricas/Cards
- Border izquierdo naranja
- Fondo con gradiente sutil
- Sombra suave
- Hover: Elevación

### Gráficos
- **Tier 1:** Naranja #FF6000 (máxima prioridad)
- **Tier 2:** Azul oscuro #170453
- **Tier 3:** Azul medio #51437E
- **Tier 4:** Azul claro #8B81A9
- **Tier 5:** Azul muy claro #C5C0D4

---

## ✅ Checklist de Verificación

Después de implementar, verifica:

### Visual
- [ ] El logo aparece en el header
- [ ] Los botones principales son naranjas
- [ ] La sidebar tiene fondo azul oscuro
- [ ] Los gráficos usan los colores PC
- [ ] Las tabs cambian a naranja al seleccionar
- [ ] Los hover states funcionan correctamente

### Funcional
- [ ] La aplicación carga sin errores
- [ ] Todas las visualizaciones se generan
- [ ] Los colores son consistentes en todos los gráficos
- [ ] El texto es legible en todos los backgrounds

### Accesibilidad
- [ ] Contraste suficiente en textos (WCAG AA)
- [ ] Botones claramente diferenciados
- [ ] Estados hover visibles
- [ ] Navegación clara

---

## 🔧 Solución de Problemas

### El logo no aparece

**Problema:** Se muestra un placeholder "PC" en vez del logo.

**Solución:**
```bash
# Verifica que el logo existe
ls assets/pc_logo.png

# Si no existe, añádelo
cp /ruta/al/logo.png assets/pc_logo.png

# O usa el script
python scripts/add_logo.py /ruta/al/logo.png
```

### Los colores no se aplican

**Problema:** La app sigue usando colores antiguos.

**Solución:**
```bash
# 1. Limpia cache de Streamlit
rm -rf ~/.streamlit/cache

# 2. Fuerza recarga completa
streamlit run app/main.py --server.runOnSave false

# 3. O reinicia completamente
# Ctrl+C y vuelve a ejecutar
```

### Error: "Module not found"

**Problema:** Error al importar módulos.

**Solución:**
```bash
# Asegúrate de tener todas las dependencias
pip install -r requirements.txt --upgrade

# Verifica Pillow (para el logo)
pip install Pillow
```

### Los gráficos tienen colores incorrectos

**Problema:** Visualizaciones con colores viejos.

**Solución:**
```bash
# 1. Verifica que visualizer.py está actualizado
cat app/components/visualizer.py | grep "#FF6000"

# 2. Si no aparece, descarga la versión nueva
# 3. Reinicia la aplicación
```

---

## 🎨 Personalización Adicional

### Cambiar el Logo

Edita `app/main.py` línea ~35:
```python
st.image("assets/tu_logo_personalizado.png", width=120)
```

### Ajustar Colores de Tier

Edita `config.py`:
```python
VIZ_CONFIG = {
    "color_scheme": {
        1: "#FF6000",  # Cambia este valor
        # ...
    }
}
```

### Modificar CSS

Edita el bloque `st.markdown("""<style>...</style>""")` en `app/main.py`.

### Cambiar Tamaño del Logo

En `app/main.py`:
```python
st.image("assets/pc_logo.png", width=150)  # Ajusta el width
```

---

## 📊 Testing en Diferentes Pantallas

### Desktop (1920x1080)
```bash
streamlit run app/main.py --server.port 8501
# Abre http://localhost:8501
```

### Tablet (1024x768)
```bash
# Usa Chrome DevTools
# F12 → Toggle device toolbar
# Selecciona iPad
```

### Mobile (375x667)
```bash
# Chrome DevTools
# F12 → Toggle device toolbar
# Selecciona iPhone SE
```

---

## 🚢 Deploy con Branding

### Streamlit Cloud

1. **Push todo a GitHub:**
```bash
git add .
git commit -m "feat: add PC Componentes branding"
git push origin main
```

2. **Subir logo como secret file:**
   - En Streamlit Cloud: Settings → Secrets
   - Tab "Files"
   - Upload `assets/pc_logo.png`

3. **Deploy:**
   - Se aplicará automáticamente el branding

### Docker

El `Dockerfile` ya está configurado. El logo se copiará automáticamente:

```bash
docker build -t keyword-analyzer-pc .
docker run -p 8501:8501 keyword-analyzer-pc
```

---

## 📈 Antes y Después

### ANTES
- Colores genéricos (púrpura, morado)
- Sin logo
- UI básica de Streamlit
- Sin identidad corporativa

### DESPUÉS
- ✅ Colores PC Componentes (naranja, azul)
- ✅ Logo en header
- ✅ UI personalizada y profesional
- ✅ Identidad corporativa completa
- ✅ Accesibilidad mejorada (WCAG AA)
- ✅ Consistencia visual en toda la app

---

## 🎉 ¡Listo!

Tu aplicación ahora tiene el branding completo de PC Componentes.

### Próximos pasos:
1. Ejecuta la app y verifica todo
2. Prueba en diferentes navegadores
3. Comparte con el equipo para feedback
4. Deploy a producción

### Recursos adicionales:
- `docs/BRANDING_SETUP.md` - Guía detallada de branding
- `scripts/add_logo.py` - Script para preparar logos
- `.streamlit/config.toml` - Configuración de colores

---

**¿Preguntas o problemas?**
Consulta `docs/BRANDING_SETUP.md` o contacta al equipo de desarrollo.

**Powered by PC Componentes** 🧡
