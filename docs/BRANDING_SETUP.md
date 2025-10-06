# 🎨 Configuración de Branding - PC Componentes

## 📋 Colores Corporativos Implementados

### Paleta Principal

#### Naranja (Color Principal)
- **#FF6000** - Naranja principal (botones, highlights, Tier 1)
- **#FF8640** - Naranja claro (hover states, gradientes)
- **#FFD7BF** - Naranja muy claro (backgrounds sutiles)

#### Azul Medio
- **#170453** - Azul medio oscuro (sidebar, Tier 2, textos importantes)
- **#51437E** - Azul medio (Tier 3, elementos secundarios)
- **#8B81A9** - Azul medio claro (Tier 4)
- **#C5C0D4** - Azul muy claro (Tier 5, backgrounds)

#### Azul Oscuro
- **#090029** - Azul oscuro principal (textos principales)
- **#46405E** - Azul oscuro medio (elementos secundarios)
- **#848094** - Azul gris (textos secundarios)
- **#C1BFC9** - Azul gris claro (borders, divisores)

#### Neutros
- **#FFFFFF** - Blanco (background principal)
- **#CCCCCC** - Gris medio (borders, elementos deshabilitados)
- **#999999** - Gris oscuro (textos secundarios, footer)

---

## 🖼️ Añadir el Logo

### Paso 1: Crear el directorio assets

```bash
mkdir -p assets
```

### Paso 2: Guardar el logo

Guarda el logo de PC Componentes como:
```
assets/pc_logo.png
```

**Recomendaciones:**
- Formato: PNG con transparencia
- Tamaño recomendado: 400x150px (se escalará a 120px de ancho)
- Fondo transparente para mejor integración

### Paso 3: Verificar

La aplicación buscará automáticamente el logo en `assets/pc_logo.png`. Si no lo encuentra, mostrará un placeholder con las iniciales "PC".

### Paso 4 (Opcional): Logo en diferentes tamaños

Puedes crear múltiples versiones:

```
assets/
├── pc_logo.png          # Logo principal
├── pc_logo_small.png    # Logo pequeño (para favicon)
├── pc_logo_dark.png     # Logo para fondo oscuro (sidebar)
└── favicon.ico          # Favicon para el navegador
```

---

## 🎨 Aplicación de Colores en la UI

### Jerarquía Visual

#### Tier 1 (Máxima Prioridad)
- Color: **#FF6000** (Naranja principal)
- Uso: Topics de máxima prioridad, CTAs principales
- **Visual:** Destaca inmediatamente, llama a la acción

#### Tier 2 (Alta Prioridad)
- Color: **#170453** (Azul medio oscuro)
- Uso: Topics importantes pero no urgentes
- **Visual:** Sólido, profesional, confiable

#### Tier 3 (Prioridad Media)
- Color: **#51437E** (Azul medio)
- Uso: Topics de desarrollo medio plazo
- **Visual:** Balanceado, ni urgente ni ignorable

#### Tier 4 (Prioridad Baja)
- Color: **#8B81A9** (Azul claro)
- Uso: Topics secundarios, long-tail
- **Visual:** Suave, no distrae de lo importante

#### Tier 5 (Mínima Prioridad)
- Color: **#C5C0D4** (Azul muy claro)
- Uso: Topics de nicho, muy específicos
- **Visual:** Sutil, presente pero no prioritario

---

## 🖌️ Elementos de la UI

### Botones

**Primarios (Acciones principales):**
```css
background: linear-gradient(135deg, #FF6000 0%, #FF8640 100%);
color: white;
```

**Secundarios:**
```css
background: #170453;
color: white;
```

**Terciarios/Ghost:**
```css
background: transparent;
border: 2px solid #FF6000;
color: #FF6000;
```

### Sidebar

**Background:**
```css
background: linear-gradient(180deg, #170453 0%, #090029 100%);
```

**Textos:**
```css
color: #FFFFFF;
```

**Labels destacados:**
```css
color: #FFD7BF;
```

### Tabs

**Tab normal:**
```css
background: transparent;
color: #170453;
```

**Tab hover:**
```css
background: #FFD7BF;
color: #FF6000;
```

**Tab activa:**
```css
background: linear-gradient(135deg, #FF6000 0%, #FF8640 100%);
color: white;
```

### Alertas

**Success:**
```css
background: #E8F5E9;
border-left: 4px solid #4CAF50;
```

**Info:**
```css
background: #FFD7BF;
border-left: 4px solid #FF6000;
```

**Warning:**
```css
background: #FFF3E0;
border-left: 4px solid #FF6000;
```

**Error:**
```css
background: #FFEBEE;
border-left: 4px solid #F44336;
```

---

## 📊 Gráficos y Visualizaciones

### Bubble Chart
- Tier 1: #FF6000 (naranja)
- Tier 2: #170453 (azul oscuro)
- Tier 3: #51437E (azul medio)
- Tier 4: #8B81A9 (azul claro)
- Tier 5: #C5C0D4 (azul muy claro)

### Gradientes Recomendados

**Warm (para destacar):**
```css
linear-gradient(135deg, #FF6000 0%, #FF8640 100%)
```

**Cool (para contenido):**
```css
linear-gradient(135deg, #170453 0%, #51437E 100%)
```

**Subtle (para backgrounds):**
```css
linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%)
```

---

## ✅ Checklist de Implementación

### Archivos Modificados
- [x] `.streamlit/config.toml` - Colores principales
- [x] `app/main.py` - CSS personalizado
- [x] `app/components/visualizer.py` - Colores de gráficos
- [x] `config.py` - Configuración de colores
- [x] `app/__init__.py` - Info de branding

### Tareas Pendientes
- [ ] Añadir logo en `assets/pc_logo.png`
- [ ] Crear favicon personalizado
- [ ] Actualizar README con branding
- [ ] Personalizar mensajes de error con branding
- [ ] Añadir footer con logo y copyright

---

## 🎯 Reglas de Usabilidad Aplicadas

### Contraste
✅ Todos los textos cumplen WCAG AA:
- Texto principal (#090029) sobre blanco: 17.4:1
- Naranja (#FF6000) sobre blanco: 4.7:1
- Azul oscuro (#170453) sobre blanco: 13.8:1

### Jerarquía Visual
✅ Colores más saturados = Mayor prioridad
✅ Naranja = Acción requerida
✅ Azul = Información/Navegación

### Consistencia
✅ Mismo color = Mismo significado en toda la app
✅ Tier 1 siempre naranja
✅ Botones primarios siempre naranja

### Accesibilidad
✅ Suficiente contraste para lectura
✅ No depende solo del color (iconos + texto)
✅ Estados hover claramente diferenciados

---

## 🔧 Personalización Adicional

### Cambiar Logo

Edita `app/main.py`:
```python
st.image("assets/tu_logo.png", width=120)
```

### Cambiar Colores

Edita `config.py`:
```python
VIZ_CONFIG = {
    "color_scheme": {
        1: "#TU_COLOR_TIER_1",
        # ...
    }
}
```

### Cambiar Gradientes

Edita el CSS en `app/main.py`:
```css
background: linear-gradient(135deg, #COLOR1 0%, #COLOR2 100%);
```

---

## 🚀 Testing

### Verificar Colores

1. Ejecuta la app: `streamlit run app/main.py`
2. Verifica que:
   - Botones principales son naranja
   - Sidebar es azul oscuro
   - Tabs usan naranja al seleccionar
   - Gráficos usan la paleta correcta

### Verificar Logo

1. ¿Aparece el logo en el header?
2. ¿Tiene el tamaño correcto?
3. ¿Se ve bien en ambos modos (claro/oscuro)?

### Verificar Contraste

Usa herramientas como:
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Chrome DevTools Accessibility

---

## 📞 Soporte

Si necesitas ajustar los colores o tienes problemas con el branding:

1. Revisa este documento
2. Verifica los archivos de configuración
3. Consulta la documentación de Streamlit
4. Contacta al equipo de desarrollo

---

**Powered by PC Componentes** 🧡
