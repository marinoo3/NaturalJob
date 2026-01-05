import plotly.express as px
import pandas as pd
from .base_fig import BaseFig




class JobFig(BaseFig):

    def render(self, job_names:list[str]) -> str:
        top_jobs = (
            pd.Series(job_names)
            .value_counts()
            .head(10)
            .reset_index()
        )
        top_jobs.columns = ['job_name', 'count']

        fig = px.bar(
            top_jobs,
            x="count",
            y="job_name",
            orientation="h",
            title="Top 10 des intitulés d'offres",
            labels={"count": "Total", "job_name": "Intitulé"},
            text="count"
        )

        fig.update_traces(
            textposition="outside",
            hovertemplate="%{y}<br>Nombre: %{x}<extra></extra>",
            marker=dict(
                color="#73ef88",                 # fill color
                line=dict(width=0)  # outline color/width
            )
        )

        fig.update_layout(
            autosize=True,
            showlegend=False,
            margin=dict(t=50, b=50, r=0),
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#1e1e1e',
            font={'color': '#E5E5E5'},
            yaxis=dict(
                categoryorder="total ascending"
            ),
            xaxis=dict(
                gridcolor="#7e7e7e",
                tickfont=dict(color="#7e7e7e")
            )
        )

        return self._get_json(fig)