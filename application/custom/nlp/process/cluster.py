import numpy as np

from sklearn.cluster import KMeans

from .base_model import Model
from ...db.offer.models import Cluster


    

class Kmeans(Model[KMeans]):

    model_name = 'kmeans.joblib'

    def __init__(self):
        """Create a Cluster instance, using Kmeans algorithm."""

        super().__init__()

    def __top_tokens(self, terms, n_terms=8):
        main_tokens = []
        for center in self.model.cluster_centers_:
            top_idx = center.argsort()[::-1][:n_terms]
            main_tokens.append(terms[top_idx])
        return main_tokens


    def fit_predict(self, emb_50d:np.ndarray, tokens:np.ndarray, K=10) -> list[Cluster]:
        """fit_predict Kmeans model then

        Args:
            emb_50d (np.ndarray): The 50 dimensions embeddings of the TF-IDF matrix
            tokens (np.ndarray): The list of TF-IDF tokens
            K (int): Number of clusters

        Returns:
            list[CLuster]: The list of clusters
        """

        model = KMeans(n_clusters=K)
        labels = model.fit_predict(emb_50d)
        self._save_model(model)

        clusters = []
        main_tokens = self.__top_tokens(tokens)
        for cluster_id in labels:
            c = Cluster(
                id = int(cluster_id),
                main_tokens = ', '.join(main_tokens[cluster_id])
            )
            clusters.append(c)

        return clusters
    
    def predict(self, emb_50d:np.ndarray, tokens:np.ndarray) -> list[Cluster]:
        """Reduce to 50 dimensions using TruncatedSVD, predict on saved Kmeans model then reduce to 3 dimensions with t-SNE

        Args:
            X (csc_matrix): The TF-IDF matrix

        Returns:
            np.ndarray: Cluster labels
            np.ndarray: 50d reduction
            np.ndarray: 3d reduction
        """

        if not self.model:
            raise Exception(f"Impossible to predict on {self.model_name} since the model doesn't exist yet. Use `fit_predict` method first to create the model")
        
        labels = self.model.predict(emb_50d)

        clusters = []
        main_tokens = self.__top_tokens(tokens)
        for cluster_id in labels:
            c = Cluster(
                id = int(cluster_id),
                main_tokens = ', '.join(main_tokens[cluster_id])
            )
            clusters.append(c)

        return clusters
