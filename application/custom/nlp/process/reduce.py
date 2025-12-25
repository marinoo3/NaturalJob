import numpy as np
from scipy.sparse import csc_matrix

from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer

from .base_model import Model





class Norm(Model[Normalizer]):
    
    model_name = 'normalizer.joblib'

    def __init__(self):
        """Create a Normalizer instance, using Kmeans algorithm."""

        super().__init__()

    def fit_transform(self, X:np.ndarray) -> np.ndarray:
        emb = self.model.fit_transform(X)
        self._save_model(self.model)
        return emb
    
    def transform(self, X:np.ndarray) -> np.ndarray:
        emb = self.model.transform(X)
        return emb



class SVD(Model[TruncatedSVD]):

    model_name = 'svd.joblib'

    def __init__(self):
        """Create a SVD instance, using Kmeans algorithm."""

        super().__init__()
        self.normalizer = Norm()

    def fit_transform(self, X:csc_matrix, n=50) -> np.ndarray:
        if X.shape[0] < n:
            raise Exception("X should contains more than n observations")
        
        model = TruncatedSVD(n_components=n)
        emb = self.normalizer.fit_transform(model.fit_transform(X))
        self._save_model(model)

        return emb
    
    def transform(self, X) -> np.ndarray:
        emb = self.model.transform(X)
        emb = self.normalizer.transform()

        return emb


class Reduce:

    """Reduce dimensions using TruncatedSVD or t-SNE"""

    def __init__(self):
        self.svd_model = SVD()

    def svd(self, X:csc_matrix) -> np.ndarray:
        return self.svd_model.transform(X)
    
    def tsne(self, X:np.ndarray, n=3, p=30) -> np.ndarray:
        tsne = TSNE(n_components=n, metric='cosine', init='pca', perplexity=min(p, len(X)-1))
        return tsne.fit_transform(X)