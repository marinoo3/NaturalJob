from abc import ABC, abstractmethod
from plotly.graph_objects import Figure
from plotly.utils import PlotlyJSONEncoder
import json




class BaseFig(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def render(self) -> dict:
        ...

    @staticmethod
    def _get_json(fig:Figure) -> str:
        return fig.to_plotly_json()
    
    @staticmethod
    def _get_json_2(fig) -> str:
        fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        return fig_json