import plotly.express as px
import numpy as np

from .base_fig import BaseFig
from ...db.offer.models import Cluster




class ClusterFig(BaseFig):

    def render(self, emb_3d:list[np.ndarray], clusters:list[Cluster], titles:list[str]) -> dict:
        emb_3d = np.stack(emb_3d)
        names = [str(c.name) for c in clusters]
        fig = px.scatter_3d(
            x=emb_3d[:, 0],
            y=emb_3d[:, 1],
            z=emb_3d[:, 2],
            color=names,
            hover_name=titles,
            labels={'x': 't-SNE 1', 'y': 't-SNE 2', 'z': 't-SNE 3'},
            opacity=0.8
        )
        fig.update_traces(
            marker=dict(size=4),
            hovertext=titles,
            hovertemplate='<b>%{hovertext}</b><br>'
                          't-SNE 1: %{x:.2f}<br>'
                          't-SNE 2: %{y:.2f}<br>'
                          't-SNE 3: %{z:.2f}<extra></extra>'
        )
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, b=0, t=0, pad=0),
            legend_title_text='Cluster',
            legend=dict(
                y=0.5,              # middle of plotting area
                yanchor='middle',   # anchor legend to its middle
            )
        )

        return self._get_json_2(fig)