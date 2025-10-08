"""
Generador de PDF profesional para informes completos de análisis de keywords
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any
import io
import plotly.graph_objects as go
from PIL import Image as PILImage
import tempfile
import os

class PDFReportGenerator:
    """Generador de informes PDF profesionales con múltiples análisis"""
    
    # Colores corporativos PC Componentes
    PC_ORANGE = colors.HexColor('#FF6000')
    PC_BLUE_DARK = colors.HexColor('#090029')
    PC_BLUE_MEDIUM = colors.HexColor('#170453')
    PC_WHITE = colors.white
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crea estilos personalizados para el PDF"""
        
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
        
        # Capítulo
        self.styles.add(ParagraphStyle(
            name='Chapter',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=self.PC_BLUE_DARK,
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subcapítulo
        self.styles.add(ParagraphStyle(
            name='SubChapter',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.PC_BLUE_MEDIUM,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Resumen ejecutivo
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=12,
            backColor=colors.HexColor('#F5F5F5')
        ))
    
    def generate_complete_report(
        self,
        analyses: Dict[str, Dict],
        metadata: Dict[str, Any],
        output_path: str = None
    ) -> bytes:
        """
        Genera el informe PDF completo con todos los análisis
        
        Args:
            analyses: Dict con los análisis completados
                     {'Temática': {...}, 'Intención': {...}, 'Funnel': {...}}
            metadata: Información general del informe
            output_path: Ruta donde guardar (opcional)
        
        Returns:
            PDF como bytes
        """
        
        # Crear buffer o archivo
        if output_path:
            pdf_file = output_path
        else:
            pdf_file = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            pdf_file,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenido del PDF
        story = []
        
        # Portada
        story.extend(self._create_cover_page(metadata, analyses))
        story.append(PageBreak())
        
        # Índice
        story.extend(self._create_table_of_contents(analyses))
        story.append(PageBreak())
        
        # Resumen ejecutivo general
        story.extend(self._create_executive_summary(analyses, metadata))
        story.append(PageBreak())
        
        # Capítulos de análisis
        chapter_num = 1
        for analysis_type, analysis_data in analyses.items():
            if analysis_data:  # Solo incluir si existe el análisis
                story.extend(self._create_analysis_chapter(
                    chapter_num,
                    analysis_type,
                    analysis_data,
                    metadata
                ))
                story.append(PageBreak())
                chapter_num += 1
        
        # Capítulo de oportunidades consolidadas
        story.extend(self._create_opportunities_chapter(analyses))
        story.append(PageBreak())
        
        # Conclusiones y próximos pasos
        story.extend(self._create_conclusions(analyses, metadata))
        
        # Generar PDF
        doc.build(story, onFirstPage=self._add_header_footer, 
                  onLaterPages=self._add_header_footer)
        
        # Retornar bytes si es BytesIO
        if isinstance(pdf_file, io.BytesIO):
            pdf_file.seek(0)
            return pdf_file.getvalue()
        
        return None
    
    def _create_cover_page(self, metadata: Dict, analyses: Dict) -> List:
        """Crea la portada del informe"""
        
        elements = []
        
        # Espaciado inicial
        elements.append(Spacer(1, 3*cm))
        
        # Título principal
        title = Paragraph(
            "KEYWORD UNIVERSE ANALYZER",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Subtítulo
        subtitle = Paragraph(
            "Informe Completo de Análisis SEO",
            self.styles['Heading2']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 2*cm))
        
        # Información del proyecto
        project_info = f"""
        <b>Proyecto:</b> {metadata.get('project_name', 'Sin nombre')}<br/>
        <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Keywords analizadas:</b> {metadata.get('total_keywords', 0):,}<br/>
        <b>Volumen total:</b> {metadata.get('total_volume', 0):,}<br/>
        <b>Análisis realizados:</b> {len([a for a in analyses.values() if a])} de 3
        """
        
        info_para = Paragraph(project_info, self.styles['CustomBody'])
        elements.append(info_para)
        elements.append(Spacer(1, 2*cm))
        
        # Logo placeholder
        logo_text = Paragraph(
            "<b>Powered by PC Componentes</b>",
            self.styles['Heading3']
        )
        elements.append(logo_text)
        
        return elements
    
    def _create_table_of_contents(self, analyses: Dict) -> List:
        """Crea el índice del informe"""
        
        elements = []
        
        elements.append(Paragraph("Índice", self.styles['Chapter']))
        elements.append(Spacer(1, 0.5*cm))
        
        toc_data = [
            ['Capítulo', 'Título', 'Página']
        ]
        
        page_num = 1
        
        # Resumen ejecutivo
        toc_data.append(['', 'Resumen Ejecutivo', str(page_num)])
        page_num += 1
        
        # Capítulos de análisis
        chapter_num = 1
        for analysis_type, analysis_data in analyses.items():
            if analysis_data:
                toc_data.append([
                    str(chapter_num),
                    f'Análisis {analysis_type}',
                    str(page_num)
                ])
                page_num += 1
                chapter_num += 1
        
        # Oportunidades
        toc_data.append([
            str(chapter_num),
            'Oportunidades Consolidadas',
            str(page_num)
        ])
        page_num += 1
        chapter_num += 1
        
        # Conclusiones
        toc_data.append([
            str(chapter_num),
            'Conclusiones y Próximos Pasos',
            str(page_num)
        ])
        
        # Crear tabla
        toc_table = Table(toc_data, colWidths=[2*cm, 12*cm, 2*cm])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PC_BLUE_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
        ]))
        
        elements.append(toc_table)
        
        return elements
    
    def _create_executive_summary(self, analyses: Dict, metadata: Dict) -> List:
        """Crea el resumen ejecutivo general"""
        
        elements = []
        
        elements.append(Paragraph("Resumen Ejecutivo", self.styles['Chapter']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Estadísticas generales
        total_topics = sum([
            len(a.get('topics', [])) for a in analyses.values() if a
        ])
        
        summary_text = f"""
        Este informe presenta un análisis completo del universo de keywords con {len([a for a in analyses.values() if a])} 
        perspectivas diferentes: {', '.join([k for k, v in analyses.items() if v])}.
        <br/><br/>
        Se han analizado un total de <b>{metadata.get('total_keywords', 0):,} keywords</b> con un volumen 
        de búsqueda combinado de <b>{metadata.get('total_volume', 0):,} búsquedas mensuales</b>.
        <br/><br/>
        Se han identificado <b>{total_topics} topics</b> distribuidos en diferentes niveles de prioridad 
        estratégica, desde oportunidades de alto impacto hasta keywords de nicho específico.
        """
        
        elements.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        elements.append(Spacer(1, 1*cm))
        
        # Tabla resumen por análisis
        if len([a for a in analyses.values() if a]) > 0:
            elements.append(Paragraph("Resumen por Tipo de Análisis", self.styles['SubChapter']))
            
            summary_data = [['Análisis', 'Topics', 'Keywords', 'Volumen']]
            
            for analysis_type, analysis_data in analyses.items():
                if analysis_data:
                    topics_count = len(analysis_data.get('topics', []))
                    keywords_sum = sum([t.get('keyword_count', 0) for t in analysis_data.get('topics', [])])
                    volume_sum = sum([t.get('volume', 0) for t in analysis_data.get('topics', [])])
                    
                    summary_data.append([
                        analysis_type,
                        str(topics_count),
                        f"{keywords_sum:,}",
                        f"{volume_sum:,}"
                    ])
            
            summary_table = Table(summary_data, colWidths=[4*cm, 3*cm, 4*cm, 4*cm])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.PC_ORANGE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFD7BF')])
            ]))
            
            elements.append(summary_table)
        
        return elements
    
    def _create_analysis_chapter(
        self, 
        chapter_num: int,
        analysis_type: str, 
        analysis_data: Dict,
        metadata: Dict
    ) -> List:
        """Crea un capítulo completo para un análisis"""
        
        elements = []
        
        # Título del capítulo
        chapter_title = f"Capítulo {chapter_num}: Análisis {analysis_type}"
        elements.append(Paragraph(chapter_title, self.styles['Chapter']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Resumen del análisis
        if 'summary' in analysis_data:
            elements.append(Paragraph("Resumen", self.styles['SubChapter']))
            summary_text = analysis_data['summary'].replace('\n', '<br/>')
            elements.append(Paragraph(summary_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.5*cm))
        
        # Topics identificados
        if 'topics' in analysis_data and len(analysis_data['topics']) > 0:
            elements.append(Paragraph("Topics Identificados", self.styles['SubChapter']))
            
            topics_df = pd.DataFrame(analysis_data['topics'])
            
            # Tabla de topics por tier
            for tier in sorted(topics_df['tier'].unique()):
                tier_topics = topics_df[topics_df['tier'] == tier]
                
                elements.append(Paragraph(f"Tier {tier}", self.styles['Heading3']))
                
                # Crear tabla
                table_data = [['Topic', 'Keywords', 'Volumen', 'Prioridad']]
                
                for _, topic in tier_topics.iterrows():
                    table_data.append([
                        topic.get('topic', 'N/A')[:40],  # Limitar longitud
                        str(topic.get('keyword_count', 0)),
                        f"{topic.get('volume', 0):,}",
                        topic.get('priority', 'N/A')
                    ])
                
                topic_table = Table(table_data, colWidths=[7*cm, 2.5*cm, 3*cm, 2.5*cm])
                topic_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.PC_BLUE_MEDIUM),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
                ]))
                
                elements.append(topic_table)
                elements.append(Spacer(1, 0.3*cm))
        
        # Tendencias (si existen)
        if 'trends' in analysis_data and len(analysis_data['trends']) > 0:
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph("Tendencias Identificadas", self.styles['SubChapter']))
            
            for trend in analysis_data['trends'][:5]:  # Top 5
                trend_text = f"""
                <b>{trend.get('trend', 'N/A')}</b><br/>
                {trend.get('insight', 'Sin descripción')}
                """
                elements.append(Paragraph(trend_text, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.2*cm))
        
        return elements
    
    def _create_opportunities_chapter(self, analyses: Dict) -> List:
        """Crea el capítulo de oportunidades consolidadas"""
        
        elements = []
        
        elements.append(Paragraph("Oportunidades Consolidadas", self.styles['Chapter']))
        elements.append(Spacer(1, 0.5*cm))
        
        intro_text = """
        Este capítulo consolida todas las oportunidades de contenido identificadas 
        en los diferentes análisis, priorizadas por impacto potencial y volumen de búsqueda.
        """
        elements.append(Paragraph(intro_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Recopilar todas las oportunidades
        all_opportunities = []
        
        for analysis_type, analysis_data in analyses.items():
            if analysis_data and 'gaps' in analysis_data:
                for gap in analysis_data['gaps']:
                    opportunity = gap.copy()
                    opportunity['source_analysis'] = analysis_type
                    all_opportunities.append(opportunity)
        
        if len(all_opportunities) > 0:
            # Ordenar por volumen
            all_opportunities.sort(key=lambda x: x.get('volume', 0), reverse=True)
            
            # Crear tabla
            opp_data = [['#', 'Oportunidad', 'Volumen', 'Fuente', 'Dificultad']]
            
            for idx, opp in enumerate(all_opportunities[:20], 1):  # Top 20
                opp_data.append([
                    str(idx),
                    opp.get('topic', 'N/A')[:35],
                    f"{opp.get('volume', 0):,}",
                    opp.get('source_analysis', 'N/A'),
                    opp.get('difficulty', 'N/A')
                ])
            
            opp_table = Table(opp_data, colWidths=[1*cm, 7*cm, 3*cm, 3*cm, 2*cm])
            opp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.PC_ORANGE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF3E0')])
            ]))
            
            elements.append(opp_table)
        else:
            elements.append(Paragraph(
                "No se identificaron gaps de contenido en los análisis realizados.",
                self.styles['CustomBody']
            ))
        
        return elements
    
    def _create_conclusions(self, analyses: Dict, metadata: Dict) -> List:
        """Crea el capítulo de conclusiones"""
        
        elements = []
        
        elements.append(Paragraph("Conclusiones y Próximos Pasos", self.styles['Chapter']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Resumen de hallazgos
        total_topics = sum([len(a.get('topics', [])) for a in analyses.values() if a])
        
        conclusion_text = f"""
        El análisis completo ha revelado <b>{total_topics} topics estratégicos</b> distribuidos 
        en {len([a for a in analyses.values() if a])} perspectivas complementarias.
        <br/><br/>
        <b>Recomendaciones principales:</b><br/>
        1. Priorizar contenido para topics de Tier 1 identificados<br/>
        2. Desarrollar estrategia de contenido por intención de usuario<br/>
        3. Crear flujo de contenido según el funnel de conversión<br/>
        4. Capitalizar oportunidades identificadas en gaps de contenido<br/>
        5. Monitorear tendencias emergentes para ajustar estrategia
        """
        
        elements.append(Paragraph(conclusion_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 1*cm))
        
        # Información del informe
        footer_text = f"""
        <b>Informe generado el:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
        <b>Herramienta:</b> Keyword Universe Analyzer<br/>
        <b>Powered by:</b> PC Componentes
        """
        
        elements.append(Paragraph(footer_text, self.styles['CustomBody']))
        
        return elements
    
    def _add_header_footer(self, canvas, doc):
        """Añade header y footer a cada página"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(self.PC_BLUE_DARK)
        canvas.drawString(2*cm, A4[1] - 1.5*cm, "Keyword Universe Analyzer")
        
        # Línea decorativa
        canvas.setStrokeColor(self.PC_ORANGE)
        canvas.setLineWidth(2)
        canvas.line(2*cm, A4[1] - 1.7*cm, A4[0] - 2*cm, A4[1] - 1.7*cm)
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(
            2*cm, 
            1.5*cm, 
            f"Generado el {datetime.now().strftime('%d/%m/%Y')}"
        )
        
        # Número de página
        page_num = canvas.getPageNumber()
        canvas.drawRightString(
            A4[0] - 2*cm,
            1.5*cm,
            f"Página {page_num}"
        )
        
        canvas.restoreState()
