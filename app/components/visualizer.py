import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List

class KeywordVisualizer:
    """Componente para crear visualizaciones del Keyword Universe"""
    
    def __init__(self):
        # Esquema de colores PC Componentes
        self.color_scheme = {
            1: '#FF6000',  # Naranja principal - Tier 1 (máxima prioridad)
            2: '#170453',  # Azul medio - Tier 2
            3: '#51437E',  # Azul medio claro - Tier 3
            4: '#8B81A9',  # Azul claro - Tier 4
            5: '#C5C0D4'   # Azul muy claro - Tier 5
        }
        
        # Colores adicionales para variaciones
        self.pc_colors = {
            'orange': '#FF6000',
            'orange_light': '#FF8640',
            'orange_lighter': '#FFD7BF',
            'blue_dark': '#090029',
            'blue_medium': '#170453',
            'blue_light': '#51437E',
            'blue_lighter': '#8B81A9',
            'blue_lightest': '#C5C0D4',
            'gray_dark': '#999999',
            'gray_medium': '#CCCCCC',
            'white': '#FFFFFF'
        }
    
    def create_bubble_chart(self, topics_df: pd.DataFrame) -> go.Figure:
        """Crea un gráfico de burbujas interactivo del keyword universe"""
        
        # Preparar datos
        topics_df['color'] = topics_df['tier'].map(self.color_scheme)
        
        # Crear figura
        fig = px.scatter(
            topics_df,
            x='keyword_count',
            y='volume',
            size='traffic',
            color='tier',
            hover_name='topic',
            hover_data={
                'keyword_count': ':,',
                'volume': ':,',
                'traffic': ':,',
                'tier': True,
                'priority': True
            },
            text='topic',
            color_discrete_map={i: self.color_scheme[i] for i in range(1, 6)},
            title='Keyword Universe - Mapa de Topics'
        )
        
        # Personalizar diseño
        fig.update_traces(
            textposition='top center',
            textfont=dict(size=10),
            marker=dict(
                line=dict(width=2, color='white'),
                opacity=0.7
            )
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="Número de Keywords",
            yaxis_title="Volumen Total de Búsqueda",
            legend_title="Tier",
            hovermode='closest',
            plot_bgcolor='rgba(240,240,240,0.5)',
            font=dict(size=12)
        )
        
        return fig
    
    def create_treemap(self, topics_df: pd.DataFrame) -> go.Figure:
        """Crea un treemap jerárquico por volumen"""
        
        # Preparar datos
        topics_df['tier_label'] = topics_df['tier'].apply(lambda x: f"Tier {x}")
        
        fig = px.treemap(
            topics_df,
            path=['tier_label', 'topic'],
            values='volume',
            color='tier',
            hover_data={'keyword_count': ':,', 'volume': ':,'},
            color_discrete_map={i: self.color_scheme[i] for i in range(1, 6)},
            title='Distribución de Volumen por Topic'
        )
        
        fig.update_layout(height=500)
        
        return fig
    
    def create_sunburst(self, topics_df: pd.DataFrame) -> go.Figure:
        """Crea un gráfico sunburst para mostrar la distribución jerárquica"""
        
        topics_df['tier_label'] = topics_df['tier'].apply(lambda x: f"Tier {x}")
        
        fig = px.sunburst(
            topics_df,
            path=['tier_label', 'topic'],
            values='volume',
            color='tier',
            hover_data={'keyword_count': ':,'},
            color_discrete_map={i: self.color_scheme[i] for i in range(1, 6)},
            title='Vista Jerárquica del Keyword Universe'
        )
        
        fig.update_layout(height=500)
        
        return fig
    
    def create_bar_chart(self, topics_df: pd.DataFrame, top_n: int = 20) -> go.Figure:
        """Crea un gráfico de barras con los top topics"""
        
        # Obtener top N topics
        top_topics = topics_df.nlargest(top_n, 'volume')
        
        fig = go.Figure(data=[
            go.Bar(
                x=top_topics['volume'],
                y=top_topics['topic'],
                orientation='h',
                marker=dict(
                    color=top_topics['tier'].map(self.color_scheme),
                    line=dict(color='white', width=2)
                ),
                text=top_topics['volume'].apply(lambda x: f'{x:,.0f}'),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Volumen: %{x:,.0f}<br><extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f'Top {top_n} Topics por Volumen',
            xaxis_title='Volumen de Búsqueda',
            yaxis_title='',
            height=max(400, top_n * 25),
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_priority_matrix(self, topics_df: pd.DataFrame) -> go.Figure:
        """Crea una matriz de prioridad (volumen vs dificultad)"""
        
        # Simular dificultad basada en keywords count (más keywords = más competencia)
        topics_df['difficulty_score'] = (topics_df['keyword_count'] / topics_df['keyword_count'].max()) * 100
        
        fig = px.scatter(
            topics_df,
            x='difficulty_score',
            y='volume',
            size='traffic',
            color='tier',
            hover_name='topic',
            color_discrete_map={i: self.color_scheme[i] for i in range(1, 6)},
            title='Matriz de Prioridad: Volumen vs Dificultad',
            labels={'difficulty_score': 'Nivel de Competencia', 'volume': 'Volumen'}
        )
        
        # Añadir líneas de referencia
        fig.add_hline(y=topics_df['volume'].median(), line_dash="dash", 
                     line_color="gray", annotation_text="Volumen medio")
        fig.add_vline(x=50, line_dash="dash", 
                     line_color="gray", annotation_text="Competencia media")
        
        # Añadir cuadrantes
        fig.add_annotation(x=25, y=topics_df['volume'].max() * 0.9,
                          text="🎯 Quick Wins", showarrow=False,
                          font=dict(size=14, color="green"))
        fig.add_annotation(x=75, y=topics_df['volume'].max() * 0.9,
                          text="⭐ Alta Prioridad", showarrow=False,
                          font=dict(size=14, color="blue"))
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_keyword_funnel(self, topics_df: pd.DataFrame) -> go.Figure:
        """Crea un embudo de keywords por tier"""
        
        # Agrupar por tier
        tier_summary = topics_df.groupby('tier').agg({
            'keyword_count': 'sum',
            'volume': 'sum',
            'topic': 'count'
        }).reset_index()
        
        tier_summary['tier_label'] = tier_summary['tier'].apply(lambda x: f"Tier {x}")
        
        fig = go.Figure(go.Funnel(
            y=tier_summary['tier_label'],
            x=tier_summary['volume'],
            textinfo="value+percent initial",
            marker=dict(
                color=[self.color_scheme.get(t, '#999') for t in tier_summary['tier']]
            ),
            hovertemplate='<b>%{y}</b><br>Volumen: %{x:,.0f}<br><extra></extra>'
        ))
        
        fig.update_layout(
            title='Embudo de Volumen por Tier',
            height=400
        )
        
        return fig
    
    def create_comparison_chart(self, topics_df: pd.DataFrame, metric: str = 'volume') -> go.Figure:
        """Crea un gráfico comparativo entre tiers"""
        
        tier_comparison = topics_df.groupby('tier').agg({
            'keyword_count': 'sum',
            'volume': 'sum',
            'traffic': 'sum',
            'topic': 'count'
        }).reset_index()
        
        fig = go.Figure()
        
        if metric == 'volume':
            fig.add_trace(go.Bar(
                x=[f"Tier {t}" for t in tier_comparison['tier']],
                y=tier_comparison['volume'],
                name='Volumen',
                marker_color=[self.color_scheme.get(t, '#999') for t in tier_comparison['tier']]
            ))
            title = 'Volumen Total por Tier'
            yaxis_title = 'Volumen de Búsqueda'
        elif metric == 'keywords':
            fig.add_trace(go.Bar(
                x=[f"Tier {t}" for t in tier_comparison['tier']],
                y=tier_comparison['keyword_count'],
                name='Keywords',
                marker_color=[self.color_scheme.get(t, '#999') for t in tier_comparison['tier']]
            ))
            title = 'Keywords Totales por Tier'
            yaxis_title = 'Número de Keywords'
        else:  # topics
            fig.add_trace(go.Bar(
                x=[f"Tier {t}" for t in tier_comparison['tier']],
                y=tier_comparison['topic'],
                name='Topics',
                marker_color=[self.color_scheme.get(t, '#999') for t in tier_comparison['tier']]
            ))
            title = 'Número de Topics por Tier'
            yaxis_title = 'Número de Topics'
        
        fig.update_layout(
            title=title,
            xaxis_title='Tier',
            yaxis_title=yaxis_title,
            height=400,
            showlegend=False
        )
        
        return fig
