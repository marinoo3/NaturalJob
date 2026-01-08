import plotly.express as px
import pandas as pd
from .base_fig import BaseFig


class ExperienceFig(BaseFig):

    def render(self, experiences:list[int], salary:list[float]) -> str:

        df = pd.DataFrame({
            'experience': experiences,
            'salary': salary
        }, dtype=float)

        df = (
            df.dropna()
            .groupby('experience', as_index=False)
            .agg(salary=('salary', 'mean'))
            .sort_values('experience')
        )

        fig = px.line(
            df,
            x='experience',
            y='salary',
            title='Salaire moyen vs Expérience minimale',
            labels={
                'experience': 'Expérience minimale (années)',
                'salary': 'Salaire moyen (€ par an)'
            },
            markers=True
        )

        fig.update_traces(
            hovertemplate=
            'Expérience: %{x} ans<br>'
            'Salaire moyen: %{y} €<extra></extra>',
            line=dict(color='#73ef88')
        )

        fig.update_layout(
            autosize=True,
            showlegend=False,
            margin=dict(t=50, b=50, r=0),
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#1e1e1e',
            font={'color': '#E5E5E5'},
            yaxis=dict(
                gridcolor="#7e7e7e",
                tickfont=dict(color="#7e7e7e"),
                zeroline=False
            ),
            xaxis=dict(
                gridcolor="#7e7e7e",
                tickfont=dict(color="#7e7e7e"),
            )
        )

        return self._get_json(fig)