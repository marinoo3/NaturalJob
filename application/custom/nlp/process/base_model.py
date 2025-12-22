import os
import joblib
from typing import Generic, TypeVar, ClassVar

from sklearn.base import BaseEstimator



EstimatorT = TypeVar("EstimatorT", bound=BaseEstimator)


class Model(Generic[EstimatorT]):

    model_name: ClassVar[str]  # must be supplied by subclasses

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "model_name", None):
            raise TypeError(
                f"{cls.__name__} must define class attribute 'model_name'"
            )

    def __init__(self):
        self.model_path = self._make_model_path()
        self.model = self._load_model()

    def _make_model_path(self) -> str:
        path = os.environ.get('DATA_PATH', 'data/')
        return os.path.join(path, 'model', self.model_name)

    def _load_model(self) -> EstimatorT|None:
        try:
            return joblib.load(self.model_path)
        except FileNotFoundError:
            return None
        
    def _save_model(self, model:EstimatorT) -> None:
        joblib.dump(model, self.model_path)
        self.model = model