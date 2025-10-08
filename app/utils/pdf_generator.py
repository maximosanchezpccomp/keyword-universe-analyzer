"""
Generador de PDFs profesionales para Keyword Universe Analyzer
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List
import io
import os
from pathlib import Path

class PDFGenerator:
    """Generador de informes PDF profesionales con branding PC Componentes"""
    
    def __init__(self):
        # Colores PC Componentes
        self.pc_orange = colors.HexColor('#FF6000')
        self.pc_blue_dark = colors.HexColor('#090029')
        self.pc_blue_medium = colors.HexColor('#170453')
        self.pc_blue_light = colors.HexColor('#51437E')
        self.pc_gray = colors.HexColor('#999999')
        
        # Configurar estilos
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.pc_blue_dark,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Capítulo
        self.styles.add(ParagraphStyle(
            name='Chapter',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=self.pc_orange,
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderColor=self.pc_orange,
            borderWidth=2,
            borderPadding=10
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.pc_blue_medium,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=self.pc_blue_dark,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Destacado
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['BodyText'],
            fontSize=12,
            textColor=self.pc_orange,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
    
    def generate_complete_report(
        self,
        analyses: Dict[str, Any],
        output_path: str = None
    ) -> bytes:
        """
        Genera un informe completo con todos los análisis
        
        Args:
            analyses: Diccionario con los análisis {tipo: resultado}
            output_path: Ruta para guardar el PDF (opcional)
        
        Returns:
            Bytes del PDF generado
        """
        
        # Crear buffer
        buffer = io.BytesIO()
        
        # Crear documento
        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Contenedor de elementos
        elements = []
        
        # Portada
        elements.extend(self._create_cover_page(analyses))
        elements.append(PageBreak())
        
        # Índice
        elements.extend(self._create_index(analyses))
        elements.append(PageBreak())
        
        # Resumen Ejecutivo
        elements.extend(self._create_executive_summary(analyses))
        elements.append(PageBreak())
        
        # Capítulos por tipo de análisis
        chapter_num = 1
        
        if 'thematic' in analyses:
            elements.extend(self._create_analysis_chapter(
                analyses['thematic'],
                chapter_num,
                "Análisis Temático",
                "Agrupación de keywords por temas y subtemas semánticos"
            ))
            elements.append(PageBreak())
            chapter_num += 1
        
        if 'intent' in analyses:
            elements.extend(self._create_analysis_chapter(
                analyses['intent'],
                chapter_num,
                "Análisis de Intención de Búsqueda",
                "Clasificación según la intención del usuario (Informacional, Comercial, Transaccional)"
            ))
            elements.append(PageBreak())
            chapter_num += 1
        
        if 'funnel' in analyses:
            elements.extend(self._create_analysis_chapter(
                analyses['funnel'],
                chapter_num,
                "Análisis de Funnel de Conversión",
                "Distribución por etapas del customer journey (TOFU, MOFU, BOFU)"
            ))
            elements.append(PageBreak())
            chapter_num += 1
        
        # Capítulo final: Consolidado de Oportunidades
        elements.extend(self._create_opportunities_chapter(analyses, chapter_num))
        
        # Construir PDF
        doc.build(elements, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        # Si no hay output_path, retornar bytes
        if not output_path:
            buffer.seek(0)
            return buffer.getvalue()
        
        return None
    
    def _create_cover_page(self, analyses: Dict[str, Any]) -> List:
        """Crea la portada del informe"""
        elements = []
        
        # Logo (si existe)
        if os.path.exists("assets/pc_logo.png"):
            try:
                logo = Image("assets/pc_logo.png", width=3*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.5*inch))
            except:
                pass
        
        # Título
        title = Paragraph(
            "Keyword Universe Analyzer<br/>Informe Completo de Análisis SEO",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Subtítulo con fecha
        subtitle = Paragraph(
            f"Generado el {datetime.now().strftime('%d de %B de %Y')}",
            self.styles['CustomHeading2']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 1*inch))
        
        # Resumen de análisis incluidos
        analysis_names = {
            'thematic': 'Análisis Temático',
            'intent': 'Análisis de Intención de Búsqueda',
            'funnel': 'Análisis de Funnel de Conversión'
        }
        
        included = [analysis_names[k] for k in analyses.keys() if k in analysis_names]
        
        if included:
            elements.append(Paragraph(
                "<b>Análisis Incluidos:</b>",
                self.styles['CustomHeading2']
            ))
            
            for analysis in included:
                elements.append(Paragraph(
                    f"✓ {analysis}",
                    self.styles['CustomBody']
                ))
        
        # Powered by
        elements.append(Spacer(1, 1.5*inch))
        elements.append(Paragraph(
            "Powered by PC Componentes",
            self.styles['CustomHeading2']
        ))
        
        return elements
    
    def _create_index(self, analyses: Dict[str, Any]) -> List:
        """Crea el índice del documento"""
        elements = []
        
        elements.append(Paragraph("Índice", self.styles['Chapter']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Crear tabla de contenidos
        toc_data = [
            ['Sección', 'Página'],
            ['Resumen Ejecutivo', '3']
        ]
        
        page_num = 4
        chapter_num = 1
        
        analysis_names = {
            'thematic': 'Análisis Temático',
            'intent': 'Análisis de Intención de Búsqueda',
            'funnel': 'Análisis de Funnel de Conversión'
        }
        
        for key, name in analysis_names.items():
            if key in analyses:
                toc_data.append([f"Capítulo {chapter_num}: {name}", str(page_num)])
                page_num += 1
                chapter_num += 1
        
        toc_data.append([f"Capítulo {chapter_num}: Consolidado de Oportunidades", str(page_num)])
        
        # Crear tabla
        toc_table = Table(toc_data, colWidths=[4.5*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.pc_blue_medium),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.pc_gray),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(toc_table)
        
        return elements
    
    def _create_executive_summary(self, analyses: Dict[str, Any]) -> List:
        """Crea el resumen ejecutivo"""
        elements = []
        
        elements.append(Paragraph("Resumen Ejecutivo", self.styles['Chapter']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Recopilar estadísticas generales
        total_topics = 0
        total_keywords = 0
        total_volume = 0
        
        for analysis in analyses.values():
            if isinstance(analysis, dict) and 'topics' in analysis:
                topics = analysis['topics']
                total_topics += len(topics)
                for topic in topics:
                    total_keywords += topic.get('keyword_count', 0)
                    total_volume += topic.get('volume', 0)
        
        # Tabla de métricas
        metrics_data = [
            ['Métrica', 'Valor'],
            ['Análisis Realizados', str(len(analyses))],
            ['Total Topics Identificados', f"{total_topics:,}"],
            ['Total Keywords Analizadas', f"{total_keywords:,}"],
            ['Volumen Total Mensual', f"{total_volume:,}"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.pc_orange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.pc_gray),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Resumen de cada análisis
        for key, analysis in analyses.items():
            if isinstance(analysis, dict) and 'summary' in analysis:
                analysis_names = {
                    'thematic': 'Análisis Temático',
                    'intent': 'Análisis de Intención',
                    'funnel': 'Análisis de Funnel'
                }
                
                name = analysis_names.get(key, 'Análisis')
                
                elements.append(Paragraph(
                    f"<b>{name}</b>",
                    self.styles['CustomHeading2']
                ))
                
                # Resumen (primeros 500 caracteres)
                summary_text = analysis['summary'][:500] + "..." if len(analysis['summary']) > 500 else analysis['summary']
                
                elements.append(Paragraph(
                    summary_text,
                    self.styles['CustomBody']
                ))
                elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_analysis_chapter(
        self,
        analysis: Dict[str, Any],
        chapter_num: int,
        title: str,
        description: str
    ) -> List:
        """Crea un capítulo para un análisis específico"""
        elements = []
        
        # Título del capítulo
        elements.append(Paragraph(
            f"Capítulo {chapter_num}: {title}",
            self.styles['Chapter']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Descripción
        elements.append(Paragraph(description, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Resumen del análisis
        if 'summary' in analysis:
            elements.append(Paragraph(
                "<b>Resumen del Análisis</b>",
                self.styles['CustomHeading2']
            ))
            elements.append(Paragraph(
                analysis['summary'],
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.3*inch))
        
        # Topics principales
        if 'topics' in analysis:
            elements.append(Paragraph(
                "<b>Topics Identificados</b>",
                self.styles['CustomHeading2']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            topics = analysis['topics']
            
            # Crear tabla de topics por tier
            for tier in sorted(set(t['tier'] for t in topics)):
                tier_topics = [t for t in topics if t['tier'] == tier]
                
                elements.append(Paragraph(
                    f"<b>Tier {tier} - Prioridad {'Alta' if tier == 1 else 'Media' if tier == 2 else 'Baja'}</b>",
                    self.styles['Highlight']
                ))
                
                # Tabla de topics del tier
                table_data = [['Topic', 'Keywords', 'Volumen', 'Prioridad']]
                
                for topic in tier_topics[:10]:  # Top 10 por tier
                    table_data.append([
                        topic['topic'][:40] + '...' if len(topic['topic']) > 40 else topic['topic'],
                        f"{topic.get('keyword_count', 0):,}",
                        f"{topic.get('volume', 0):,}",
                        topic.get('priority', 'medium').upper()
                    ])
                
                topics_table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1*inch])
                topics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.pc_blue_light),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.pc_gray),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                elements.append(topics_table)
                elements.append(Spacer(1, 0.2*inch))
        
        # Gráficos (si existen)
        if 'chart_path' in analysis:
            try:
                chart = Image(analysis['chart_path'], width=5*inch, height=3.5*inch)
                chart.hAlign = 'CENTER'
                elements.append(chart)
                elements.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        # Gaps y oportunidades
        if 'gaps' in analysis and analysis['gaps']:
            elements.append(Paragraph(
                "<b>Oportunidades de Contenido</b>",
                self.styles['CustomHeading2']
            ))
            
            for i, gap in enumerate(analysis['gaps'][:5], 1):
                gap_text = f"""
                <b>{i}. {gap.get('topic', 'N/A')}</b><br/>
                Volumen: {gap.get('volume', 0):,} búsquedas/mes<br/>
                Dificultad: {gap.get('difficulty', 'N/A').upper()}<br/>
                {gap.get('description', '')}
                """
                elements.append(Paragraph(gap_text, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_opportunities_chapter(
        self,
        analyses: Dict[str, Any],
        chapter_num: int
    ) -> List:
        """Crea el capítulo consolidado de oportunidades"""
        elements = []
        
        elements.append(Paragraph(
            f"Capítulo {chapter_num}: Consolidado de Oportunidades",
            self.styles['Chapter']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph(
            "Este capítulo consolida todas las oportunidades identificadas en los diferentes análisis, "
            "priorizadas por volumen de búsqueda y facilidad de implementación.",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Recopilar todas las oportunidades
        all_opportunities = []
        
        for key, analysis in analyses.items():
            if isinstance(analysis, dict) and 'gaps' in analysis:
                for gap in analysis['gaps']:
                    gap['source'] = key
                    all_opportunities.append(gap)
        
        # Ordenar por volumen
        all_opportunities.sort(key=lambda x: x.get('volume', 0), reverse=True)
        
        if all_opportunities:
            # Tabla de oportunidades
            table_data = [['#', 'Oportunidad', 'Volumen', 'Dificultad', 'Fuente']]
            
            analysis_names = {
                'thematic': 'Temático',
                'intent': 'Intención',
                'funnel': 'Funnel'
            }
            
            for i, opp in enumerate(all_opportunities[:20], 1):  # Top 20
                table_data.append([
                    str(i),
                    opp.get('topic', 'N/A')[:35] + '...' if len(opp.get('topic', '')) > 35 else opp.get('topic', 'N/A'),
                    f"{opp.get('volume', 0):,}",
                    opp.get('difficulty', 'N/A').upper(),
                    analysis_names.get(opp.get('source', ''), 'N/A')
                ])
            
            opp_table = Table(table_data, colWidths=[0.4*inch, 2.5*inch, 1.2*inch, 1*inch, 0.9*inch])
            opp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.pc_orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.pc_gray),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            elements.append(opp_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Detalles de top 5
            elements.append(Paragraph(
                "<b>Top 5 Oportunidades - Análisis Detallado</b>",
                self.styles['CustomHeading2']
            ))
            
            for i, opp in enumerate(all_opportunities[:5], 1):
                detail_text = f"""
                <b>{i}. {opp.get('topic', 'N/A')}</b><br/>
                Volumen estimado: {opp.get('volume', 0):,} búsquedas mensuales<br/>
                Nivel de dificultad: {opp.get('difficulty', 'N/A').upper()}<br/>
                Fuente: Análisis {analysis_names.get(opp.get('source', ''), 'N/A')}<br/><br/>
                {opp.get('description', 'Sin descripción disponible')}
                """
                elements.append(Paragraph(detail_text, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.2*inch))
        else:
            elements.append(Paragraph(
                "No se identificaron oportunidades específicas en los análisis realizados.",
                self.styles['CustomBody']
            ))
        
        return elements
    
    def _add_header_footer(self, canvas, doc):
        """Añade header y footer a cada página"""
        canvas.saveState()
        
        # Footer
        footer_text = f"Keyword Universe Analyzer - PC Componentes | Página {doc.page}"
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(self.pc_gray)
        canvas.drawCentredString(A4[0] / 2, 0.5 * inch, footer_text)
        
        # Línea decorativa
        canvas.setStrokeColor(self.pc_orange)
        canvas.setLineWidth(2)
        canvas.line(inch, A4[1] - 0.5*inch, A4[0] - inch, A4[1] - 0.5*inch)
        
        canvas.restoreState()
    
    def save_chart_as_image(self, fig, filename: str) -> str:
        """
        Guarda un gráfico de Plotly como imagen
        
        Args:
            fig: Figura de Plotly
            filename: Nombre del archivo
        
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear directorio temporal si no existe
            temp_dir = Path("outputs/temp_charts")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = temp_dir / filename
            
            # Guardar como imagen estática
            fig.write_image(str(filepath), format='png', width=800, height=600)
            
            return str(filepath)
        except Exception as e:
            print(f"Error guardando gráfico: {e}")
            return None
