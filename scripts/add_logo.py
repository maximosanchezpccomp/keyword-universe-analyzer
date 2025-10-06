"""
Script para preparar el logo de PC Componentes

Uso:
    python scripts/add_logo.py path/to/pc_logo.png
"""

import sys
import os
from pathlib import Path
from PIL import Image

def prepare_logo(input_path: str):
    """
    Prepara el logo optimizándolo para la aplicación
    
    Args:
        input_path: Ruta al logo original
    """
    
    # Crear directorio assets si no existe
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    try:
        # Abrir imagen
        img = Image.open(input_path)
        print(f"✓ Logo cargado: {img.size[0]}x{img.size[1]}px")
        
        # Verificar que tiene transparencia (modo RGBA)
        if img.mode != 'RGBA':
            print("⚠️  Convirtiendo a RGBA para transparencia...")
            img = img.convert('RGBA')
        
        # Logo principal (para header)
        # Mantener aspect ratio, ancho máximo 400px
        max_width = 400
        if img.size[0] > max_width:
            ratio = max_width / img.size[0]
            new_size = (max_width, int(img.size[1] * ratio))
            img_main = img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            img_main = img
        
        output_main = assets_dir / "pc_logo.png"
        img_main.save(output_main, "PNG", optimize=True)
        print(f"✓ Logo principal guardado: {output_main}")
        print(f"  Tamaño: {img_main.size[0]}x{img_main.size[1]}px")
        
        # Logo pequeño (para sidebar si se necesita)
        small_width = 150
        ratio = small_width / img.size[0]
        new_size = (small_width, int(img.size[1] * ratio))
        img_small = img.resize(new_size, Image.Resampling.LANCZOS)
        
        output_small = assets_dir / "pc_logo_small.png"
        img_small.save(output_small, "PNG", optimize=True)
        print(f"✓ Logo pequeño guardado: {output_small}")
        print(f"  Tamaño: {img_small.size[0]}x{img_small.size[1]}px")
        
        # Crear favicon (32x32)
        favicon_size = (32, 32)
        img_favicon = img.resize(favicon_size, Image.Resampling.LANCZOS)
        
        # Convertir a RGB para ICO (no soporta RGBA bien)
        img_favicon_rgb = Image.new('RGB', favicon_size, (255, 255, 255))
        img_favicon_rgb.paste(img_favicon, mask=img_favicon.split()[3] if img_favicon.mode == 'RGBA' else None)
        
        output_favicon = assets_dir / "favicon.ico"
        img_favicon_rgb.save(output_favicon, format="ICO", sizes=[favicon_size])
        print(f"✓ Favicon guardado: {output_favicon}")
        
        print("\n✅ ¡Logos preparados exitosamente!")
        print("\nArchivos creados:")
        print(f"  - {output_main} (para header)")
        print(f"  - {output_small} (para usos pequeños)")
        print(f"  - {output_favicon} (favicon del navegador)")
        
        print("\n📝 Próximos pasos:")
        print("1. Verifica que los logos se ven bien")
        print("2. Ejecuta: streamlit run app/main.py")
        print("3. El logo debería aparecer en el header")
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error procesando el logo: {str(e)}")
        sys.exit(1)


def create_placeholder_logo():
    """Crea un logo placeholder si no tienes el logo real"""
    
    from PIL import Image, ImageDraw, ImageFont
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Crear imagen
    width, height = 400, 150
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Fondo naranja con gradiente simulado
    for y in range(height):
        color_value = int(255 - (y / height) * 100)
        color = (255, 96 + color_value//5, 0, 255)
        draw.rectangle([0, y, width, y+1], fill=color)
    
    # Texto "PC COMPONENTES"
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Calcular posición centrada
    text = "PC COMPONENTES"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Sombra
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 100))
    # Texto
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # Guardar
    output = assets_dir / "pc_logo.png"
    img.save(output, "PNG")
    print(f"✓ Logo placeholder creado: {output}")
    print("⚠️  Este es un placeholder. Reemplázalo con el logo real usando:")
    print("   python scripts/add_logo.py path/to/pc_logo_real.png")


if __name__ == "__main__":
    print("=" * 60)
    print("  PREPARADOR DE LOGO - PC COMPONENTES")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("ℹ️  No se proporcionó logo. Creando placeholder...")
        print()
        create_placeholder_logo()
        print()
        print("Para usar tu logo real:")
        print("  python scripts/add_logo.py path/to/tu_logo.png")
    else:
        input_path = sys.argv[1]
        print(f"Procesando: {input_path}")
        print()
        prepare_logo(input_path)
    
    print()
    print("=" * 60)
