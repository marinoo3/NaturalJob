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
        return os.path.join(path, 'model')

    def _load_model(self) -> EstimatorT|None:
        try:
            path = os.path.join(self.model_path, self.model_name)
            return joblib.load(path)
        except FileNotFoundError:
            return None
        
    def _save_model(self, model:EstimatorT) -> None:
        path = os.path.join(self.model_path, self.model_name)
        joblib.dump(model, path)
        self.model = model