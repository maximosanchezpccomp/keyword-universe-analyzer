"""
Generador de informes PDF completos con múltiples análisis de keywords

Este módulo crea informes profesionales en PDF con branding PC Componentes,
incluyendo análisis temático, de intención y de funnel.

Instalación requerida:
    pip install reportlab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import io
from typing import Dict, List, Any
import pandas as pd


class PDFReportGenerator:
    """Generador de informes PDF con branding PC Componentes"""
    
    # Colores corporativos PC Componentes
    PC_ORANGE = colors.HexColor('#FF6000')
    PC_ORANGE_LIGHT = colors.HexColor('#FF8640')
    PC_BLUE_DARK = colors.HexColor('#090029')
    PC_BLUE_MEDIUM = colors.HexColor('#170453')
    PC_BLUE_LIGHT = colors.HexColor('#51437E')
    PC_GRAY = colors.HexColor('#999999')
    
    def __init__(self):
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.PC_ORANGE,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.PC_BLUE_DARK,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulos secundarios
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.PC_BLUE_MEDIUM,
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.PC_BLUE_DARK,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Texto destacado
        self.styles.add(ParagraphStyle(
            name='CustomHighlight',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.PC_ORANGE,
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
    
    def _create_header_footer(self, canvas, doc):
        """Crea header y footer en cada página"""
        canvas.saveState()
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.PC_GRAY)
        canvas.drawString(
            inch, 0.5 * inch,
            f"Keyword Universe Analyzer - Powered by PC Componentes"
        )
        canvas.drawRightString(
            letter[0] - inch, 0.5 * inch,
            f"Página {doc.page}"
        )
        
        # Línea decorativa en el footer
        canvas.setStrokeColor(self.PC_ORANGE_LIGHT)
        canvas.setLineWidth(2)
        canvas.line(inch, 0.75 * inch, letter[0] - inch, 0.75 * inch)
        
        canvas.restoreState()
    
    def generate_report(
        self,
        analyses: Dict[str, Any],
        total_keywords: int,
        total_volume: int
    ) -> bytes:
        """
        Genera el informe PDF completo
        
        Args:
            analyses: Diccionario con los análisis disponibles
                {
                    'thematic': {...},
                    'intent': {...},
                    'funnel': {...}
                }
            total_keywords: Total de keywords analizadas
            total_volume: Volumen total de búsqueda
        
        Returns:
            bytes del PDF generado
        """
        
        # Crear documento
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        # Contenedor de elementos
        story = []
        
        # === PORTADA ===
        story.extend(self._create_cover_page(analyses, total_keywords, total_volume))
        story.append(PageBreak())
        
        # === RESUMEN EJECUTIVO ===
        story.extend(self._create_executive_summary(analyses))
        story.append(PageBreak())
        
        # === ANÁLISIS TEMÁTICO ===
        if 'thematic' in analyses:
            story.extend(self._create_thematic_section(analyses['thematic']))
            story.append(PageBreak())
        
        # === ANÁLISIS DE INTENCIÓN ===
        if 'intent' in analyses:
            story.extend(self._create_intent_section(analyses['intent']))
            story.append(PageBreak())
        
        # === ANÁLISIS DE FUNNEL ===
        if 'funnel' in analyses:
            story.extend(self._create_funnel_section(analyses['funnel']))
            story.append(PageBreak())
        
        # === OPORTUNIDADES ===
        gaps = []
        for analysis_type, data in analyses.items():
            if 'gaps' in data:
                gaps.extend(data['gaps'])
        
        if gaps:
            story.extend(self._create_opportunities_section(gaps))
            story.append(PageBreak())
        
        # === RECOMENDACIONES FINALES ===
        story.extend(self._create_recommendations(analyses))
        
        # Construir PDF
        doc.build(story, onFirstPage=self._create_header_footer, 
                  onLaterPages=self._create_header_footer)
        
        # Retornar bytes
        pdf_bytes = self.buffer.getvalue()
        self.buffer.close()
        return pdf_bytes
    
    def _create_cover_page(
        self,
        analyses: Dict[str, Any],
        total_keywords: int,
        total_volume: int
    ) -> List:
        """Crea la portada del informe"""
        
        elements = []
        
        # Espaciado inicial
        elements.append(Spacer(1, 2 * inch))
        
        # Título principal
        title = Paragraph(
            "🌌 Keyword Universe Analyzer",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Subtítulo
        subtitle = Paragraph(
            "Informe Completo de Análisis SEO",
            self.styles['CustomHeading']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.5 * inch))
        
        # Info del informe
        info_data = [
            ['Fecha del Informe:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Total Keywords Analizadas:', f"{total_keywords:,}"],
            ['Volumen Total de Búsqueda:', f"{total_volume:,}"],
            ['', ''],
            ['Análisis Incluidos:', ''],
        ]
        
        # Añadir análisis incluidos
        analysis_names = {
            'thematic': '✓ Análisis Temático (Topics)',
            'intent': '✓ Análisis de Intención de Búsqueda',
            'funnel': '✓ Análisis de Funnel de Conversión'
        }
        
        for key, name in analysis_names.items():
            if key in analyses:
                info_data.append(['', name])
        
        # Tabla de información
        info_table = Table(info_data, colWidths=[2.5 * inch, 3.5 * inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), self.PC_BLUE_DARK),
            ('TEXTCOLOR', (1, 0), (1, -1), self.PC_BLUE_MEDIUM),
            ('TEXTCOLOR', (1, 4), (1, 4), self.PC_ORANGE),
            ('TEXTCOLOR', (1, 5), (1, -1), self.PC_ORANGE),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 1 * inch))
        
        # Footer de portada
        footer_text = Paragraph(
            "<b>Powered by PC Componentes</b><br/>Análisis generado con IA (Claude Sonnet 4.5)",
            self.styles['CustomBody']
        )
        elements.append(footer_text)
        
        return elements
    
    def _create_executive_summary(self, analyses: Dict[str, Any]) -> List:
        """Crea el resumen ejecutivo"""
        
        elements = []
        
        # Título
        elements.append(Paragraph("📊 Resumen Ejecutivo", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Combinar resúmenes de todos los análisis
        for analysis_type, data in analyses.items():
            if 'summary' in data:
                # Título del análisis
                analysis_titles = {
                    'thematic': 'Análisis Temático',
                    'intent': 'Análisis de Intención',
                    'funnel': 'Análisis de Funnel'
                }
                
                elements.append(Paragraph(
                    analysis_titles.get(analysis_type, 'Análisis'),
                    self.styles['CustomHeading']
                ))
                
                # Resumen
                summary_text = data['summary'].replace('\n', '<br/>')
                elements.append(Paragraph(summary_text, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _create_thematic_section(self, analysis: Dict[str, Any]) -> List:
        """Crea la sección de análisis temático"""
        
        elements = []
        
        # Título
        elements.append(Paragraph(
            "🎯 Análisis Temático - Topics Identificados",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Convertir topics a DataFrame
        topics_df = pd.DataFrame(analysis['topics'])
        
        # Agrupar por tier
        for tier in sorted(topics_df['tier'].unique()):
            tier_topics = topics_df[topics_df['tier'] == tier].sort_values(
                'volume', ascending=False
            )
            
            # Título del tier
            tier_colors = {
                1: self.PC_ORANGE,
                2: self.PC_BLUE_DARK,
                3: self.PC_BLUE_MEDIUM,
                4: self.PC_BLUE_LIGHT,
                5: self.PC_GRAY
            }
            
            elements.append(Paragraph(
                f"<font color='{tier_colors.get(tier, self.PC_BLUE_DARK).hexval()}'>Tier {tier} - Prioridad {'Alta' if tier == 1 else 'Media' if tier <= 3 else 'Baja'}</font>",
                self.styles['CustomHeading']
            ))
            elements.append(Spacer(1, 0.1 * inch))
            
            # Tabla de topics
            table_data = [['Topic', 'Keywords', 'Volumen', 'Tráfico', 'Prioridad']]
            
            for _, topic in tier_topics.head(10).iterrows():
                table_data.append([
                    topic['topic'][:40] + '...' if len(topic['topic']) > 40 else topic['topic'],
                    f"{int(topic['keyword_count']):,}",
                    f"{int(topic['volume']):,}",
                    f"{int(topic['traffic']):,}",
                    topic['priority'].upper()
                ])
            
            # Crear tabla
            col_widths = [2.5 * inch, 0.8 * inch, 1 * inch, 1 * inch, 0.7 * inch]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), tier_colors.get(tier, self.PC_ORANGE)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Body
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.PC_BLUE_DARK),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 0.5, self.PC_GRAY),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _create_intent_section(self, analysis: Dict[str, Any]) -> List:
        """Crea la sección de análisis de intención"""
        
        elements = []
        
        # Título
        elements.append(Paragraph(
            "🎯 Análisis de Intención de Búsqueda",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Convertir topics a DataFrame
        topics_df = pd.DataFrame(analysis['topics'])
        
        # Agrupar por intención
        intent_names = {
            'informational': '📚 Informacional - Usuario busca aprender',
            'navigational': '🧭 Navegacional - Usuario busca un sitio',
            'commercial': '🔍 Comercial - Usuario investiga opciones',
            'transactional': '💳 Transaccional - Usuario listo para comprar'
        }
        
        if 'intent' in topics_df.columns:
            for intent, title in intent_names.items():
                intent_topics = topics_df[topics_df['intent'] == intent].sort_values(
                    'volume', ascending=False
                )
                
                if len(intent_topics) == 0:
                    continue
                
                # Título de la intención
                elements.append(Paragraph(title, self.styles['CustomHeading']))
                elements.append(Spacer(1, 0.1 * inch))
                
                # Estadísticas
                total_volume = intent_topics['volume'].sum()
                total_keywords = intent_topics['keyword_count'].sum()
                
                stats_text = f"Volumen Total: <b>{total_volume:,}</b> | Keywords: <b>{int(total_keywords):,}</b>"
                elements.append(Paragraph(stats_text, self.styles['CustomHighlight']))
                elements.append(Spacer(1, 0.1 * inch))
                
                # Top 5 topics
                table_data = [['Topic', 'Keywords', 'Volumen', 'Tier']]
                
                for _, topic in intent_topics.head(5).iterrows():
                    table_data.append([
                        topic['topic'][:45] + '...' if len(topic['topic']) > 45 else topic['topic'],
                        f"{int(topic['keyword_count']):,}",
                        f"{int(topic['volume']):,}",
                        f"Tier {topic['tier']}"
                    ])
                
                # Crear tabla
                col_widths = [3 * inch, 1 * inch, 1.2 * inch, 0.8 * inch]
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.PC_ORANGE),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.PC_BLUE_DARK),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.PC_GRAY),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.25 * inch))
        
        return elements
    
    def _create_funnel_section(self, analysis: Dict[str, Any]) -> List:
        """Crea la sección de análisis de funnel"""
        
        elements = []
        
        # Título
        elements.append(Paragraph(
            "📊 Análisis de Funnel de Conversión",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Convertir topics a DataFrame
        topics_df = pd.DataFrame(analysis['topics'])
        
        # Agrupar por etapa del funnel
        funnel_stages = {
            'TOFU': '🔝 Top of Funnel (TOFU) - Awareness',
            'MOFU': '⚡ Middle of Funnel (MOFU) - Consideration',
            'BOFU': '🎯 Bottom of Funnel (BOFU) - Decision'
        }
        
        if 'funnel_stage' in topics_df.columns:
            for stage, title in funnel_stages.items():
                stage_topics = topics_df[topics_df['funnel_stage'] == stage].sort_values(
                    'volume', ascending=False
                )
                
                if len(stage_topics) == 0:
                    continue
                
                # Título de la etapa
                elements.append(Paragraph(title, self.styles['CustomHeading']))
                elements.append(Spacer(1, 0.1 * inch))
                
                # Estadísticas
                total_volume = stage_topics['volume'].sum()
                total_keywords = stage_topics['keyword_count'].sum()
                
                stats_text = f"Volumen Total: <b>{total_volume:,}</b> | Keywords: <b>{int(total_keywords):,}</b>"
                elements.append(Paragraph(stats_text, self.styles['CustomHighlight']))
                elements.append(Spacer(1, 0.1 * inch))
                
                # Top topics
                table_data = [['Topic', 'Keywords', 'Volumen', 'Tipo Contenido']]
                
                for _, topic in stage_topics.head(8).iterrows():
                    table_data.append([
                        topic['topic'][:40] + '...' if len(topic['topic']) > 40 else topic['topic'],
                        f"{int(topic['keyword_count']):,}",
                        f"{int(topic['volume']):,}",
                        topic.get('content_type', 'N/A')[:20]
                    ])
                
                # Crear tabla
                col_widths = [2.5 * inch, 0.9 * inch, 1.1 * inch, 1.5 * inch]
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.PC_ORANGE),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.PC_BLUE_DARK),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.PC_GRAY),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.25 * inch))
        
        return elements
    
    def _create_opportunities_section(self, gaps: List[Dict]) -> List:
        """Crea la sección de oportunidades"""
        
        elements = []
        
        # Título
        elements.append(Paragraph(
            "💡 Oportunidades de Contenido Detectadas",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Ordenar por volumen
        gaps_sorted = sorted(gaps, key=lambda x: x.get('volume', 0), reverse=True)
        
        for i, gap in enumerate(gaps_sorted[:10], 1):
            # Título de la oportunidad
            elements.append(Paragraph(
                f"<b>Oportunidad {i}: {gap['topic']}</b>",
                self.styles['CustomSubheading']
            ))
            
            # Descripción
            elements.append(Paragraph(
                gap.get('description', 'N/A'),
                self.styles['CustomBody']
            ))
            
            # Métricas
            metrics = [
                ['Volumen Potencial:', f"{gap.get('volume', 0):,}"],
                ['Dificultad:', gap.get('difficulty', 'N/A').upper()],
                ['Keywords relacionadas:', str(gap.get('keyword_count', 'N/A'))]
            ]
            
            metrics_table = Table(metrics, colWidths=[1.5 * inch, 2 * inch])
            metrics_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.PC_BLUE_DARK),
            ]))
            
            elements.append(Spacer(1, 0.05 * inch))
            elements.append(metrics_table)
            elements.append(Spacer(1, 0.15 * inch))
        
        return elements
    
    def _create_recommendations(self, analyses: Dict[str, Any]) -> List:
        """Crea la sección de recomendaciones"""
        
        elements = []
        
        # Título
        elements.append(Paragraph(
            "✅ Recomendaciones Estratégicas",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        recommendations = [
            {
                'title': '1. Priorizar Contenido Tier 1',
                'text': 'Enfócate primero en los topics de Tier 1 identificados en el análisis temático. Estos tienen el mayor potencial de impacto inmediato.'
            },
            {
                'title': '2. Estrategia de Intención',
                'text': 'Crea contenido específico para cada tipo de intención. El contenido transaccional debe optimizarse para conversión, mientras que el informacional debe enfocarse en SEO y autoridad.'
            },
            {
                'title': '3. Desarrollo del Funnel',
                'text': 'Desarrolla contenido para todas las etapas del funnel. No te enfoques solo en BOFU; el contenido TOFU y MOFU es crucial para atraer y educar a tu audiencia.'
            },
            {
                'title': '4. Capitalizar Oportunidades',
                'text': 'Las oportunidades detectadas representan gaps donde la competencia es menor. Prioriza estas áreas para conseguir quick wins.'
            },
            {
                'title': '5. Calendario de Contenido',
                'text': 'Crea un calendario basado en los tiers identificados. Distribuye la producción de contenido a lo largo de 3-6 meses para mantener consistencia.'
            }
        ]
        
        for rec in recommendations:
            elements.append(Paragraph(
                f"<b>{rec['title']}</b>",
                self.styles['CustomSubheading']
            ))
            elements.append(Paragraph(
                rec['text'],
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Nota final
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(
            "<b>Nota:</b> Este informe es una guía estratégica basada en análisis de IA. Recomendamos validar las oportunidades con investigación adicional y adaptarlas a tu contexto específico de negocio.",
            self.styles['CustomBody']
        ))
        
        return elements


# ============================================
# FUNCIÓN AUXILIAR PARA USAR EN MAIN.PY
# ============================================

def generate_comprehensive_pdf(
    analyses: Dict[str, Any],
    total_keywords: int,
    total_volume: int
) -> bytes:
    """
    Genera un PDF completo con todos los análisis disponibles
    
    Args:
        analyses: Dict con los análisis {'thematic': {...}, 'intent': {...}, 'funnel': {...}}
        total_keywords: Total de keywords analizadas
        total_volume: Volumen total
    
    Returns:
        bytes del PDF
    """
    generator = PDFReportGenerator()
    return generator.generate_report(analyses, total_keywords, total_volume)


# ============================================
# EJEMPLO DE USO
# ============================================

def example_usage():
    """Ejemplo de cómo generar un PDF"""
    
    # Datos de ejemplo
    analyses = {
        'thematic': {
            'summary': 'Resumen del análisis temático...',
            'topics': [
                {
                    'topic': 'SEO Tools',
                    'tier': 1,
                    'keyword_count': 150,
                    'volume': 500000,
                    'traffic': 150000,
                    'priority': 'high'
                },
                {
                    'topic': 'Keyword Research',
                    'tier': 1,
                    'keyword_count': 120,
                    'volume': 350000,
                    'traffic': 105000,
                    'priority': 'high'
                }
            ],
            'gaps': [
                {
                    'topic': 'API Integration',
                    'volume': 50000,
                    'description': 'Oportunidad de contenido técnico',
                    'difficulty': 'medium',
                    'keyword_count': 25
                }
            ]
        }
    }
    
    # Generar PDF
    pdf_bytes = generate_comprehensive_pdf(
        analyses=analyses,
        total_keywords=10000,
        total_volume=5000000
    )
    
    # Guardar
    with open('ejemplo_informe.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print("✅ PDF generado: ejemplo_informe.pdf")


if __name__ == "__main__":
    example_usage()
