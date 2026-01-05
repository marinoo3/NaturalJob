from abc import ABC, abstractmethod
from plotly.graph_objects import Figure
from plotly.utils import PlotlyJSONEncoder
import json




class BaseFig(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def render(self) -> str:
        ...
    
    @staticmethod
    def _get_json(fig) -> str:
        fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        return fig_json