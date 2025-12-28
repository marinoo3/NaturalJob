import numpy as np
from scipy.sparse import csc_matrix

from sklearn.cluster import KMeans

from .base_model import Model
from ...db.offer.models import Cluster


    

class Kmeans(Model[KMeans]):

    model_name = 'kmeans.joblib'

    def __init__(self):
        """Create a Cluster instance, using Kmeans algorithm."""

        super().__init__()


    def __top_tokens(self, X:csc_matrix, labels:np.ndarray, terms:np.ndarray, n_terms=8):
        X_csr = X.tocsr()      # convenient row slicing
        main_tokens = []
        for cluster_id in range(self.model.n_clusters):
            mask = (labels == cluster_id)
            cluster_docs = X_csr[mask]

            if cluster_docs.shape[0] == 0:    # no docs assigned
                continue

            mean_vec = np.asarray(cluster_docs.mean(axis=0)).ravel()
            top_idx = mean_vec.argsort()[::-1][:n_terms]
            main_tokens.append(terms[top_idx])

        return main_tokens


    def fit_predict(self, X:csc_matrix, emb_50d:np.ndarray, tokens:np.ndarray, K=5) -> tuple[list[int], list[Cluster]]:
        """fit_predict Kmeans model

        Args:
            X (csc_matrix): TF-IDF matrix
            emb_50d (np.ndarray): The 50 dimensions embeddings of the TF-IDF matrix
            tokens (np.ndarray): The list of TF-IDF tokens
            K (int): Number of clusters. Default to 5

        Returns:
            list[int]: The list of cluster assignments
            list[Clusters]: List of unique clusters
        """

        model = KMeans(n_clusters=K)
        labels = model.fit_predict(emb_50d)
        self._save_model(model)

        clusters = []
        main_tokens = self.__top_tokens(X, labels, tokens)
        for cluster_id in np.unique(labels):
            c = Cluster(
                id = int(cluster_id),
                main_tokens = ', '.join(main_tokens[cluster_id])
            )
            clusters.append(c)

        return labels.tolist(), clusters
    
    def predict(self, emb_50d:np.ndarray) -> tuple[list[int], list[Cluster]]:
        """Predict cluster assignments on saved Kmeans model

        Args:
            emb_50d (np.ndarray): 50 dimensions reduction

        Returns:
            list[int]: The list of cluster assignments
            list[Cluster]: List of unique clusters (only cluster id)
        """

        if not self.model:
            raise Exception(f"Impossible to predict on {self.model_name} since the model doesn't exist yet. Use `fit_predict` method first to create the model")
        
        emb_50d = np.asarray(emb_50d, dtype=np.float32)
        labels = self.model.predict(emb_50d)
        clusters = [Cluster(id = int(cluster_id)) for cluster_id in np.unique(labels)]

        return labels.tolist(), clusters
