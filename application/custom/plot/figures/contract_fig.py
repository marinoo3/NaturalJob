import plotly.express as px
import pandas as pd
from .base_fig import BaseFig


class ContractFig(BaseFig):

    def render(self, contracts:list[str]) -> str:
        contract_counts = (
            pd.Series(contracts)
            .value_counts()
        )

        fig = px.pie(
            values=contract_counts.values,
            names=contract_counts.index,
            title='Distribution par type de contrat',
            hole=0.3
        )

        fig.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.2%}",
            textinfo="percent",
        )

        fig.update_layout(
            margin=dict(t=50, b=50, l=0, r=0),
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#1e1e1e',
            font={'color': '#E5E5E5'},
            showlegend=False
        )

        return self._get_json(fig)
