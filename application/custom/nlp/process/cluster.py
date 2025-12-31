from flask import url_for

import numpy as np
from scipy.sparse import csc_matrix
from datetime import date

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
    
    def __compute_score(self, X:np.ndarray) -> float:
        global_center = np.mean(X, axis=0)
        total_inertia = np.sum(np.sum((X - global_center)**2, axis=1))
        explained_inertia = 1 - self.model.inertia_ / total_inertia
        return round(float(explained_inertia) * 100, 2)
    
    def __generate_metadata(self, new_model=False, X:np.ndarray=None) -> dict:
        metadata = self.metadata

        if new_model:
            metadata['prefix'] = "K"
            metadata['version'] = (metadata.get('version') or 0) + 1
            metadata['date'] = date.today().isoformat()
            metadata['shape'] = self.model.labels_.shape[0]
            metadata['features'] = {
                '0_score': {
                    'label': "Pourcentage d'inertie expliquée",
                    'icon': url_for('static', filename='images/smart.svg'),
                    'value': str(self.__compute_score(X)) + '%'
                },
                '1_fit': {
                    'label': "Taille de l'échantillon d'apprentissage",
                    'icon': url_for('static', filename='images/fit.svg'),
                    'value': self.model.labels_.shape[0]
                },
                '2_predict' : {
                    'label': "Nombre de prédictions",
                    'icon': url_for('static', filename='images/stack.svg'),
                    'value': 0
                },
                '3_dimensions': {
                    'label': 'Nombre de dimensions',
                    'icon': url_for('static', filename='images/dimension.svg'),
                    'value': 50
                },
                '4_clusters': {
                    'label': "Nombre de cluster",
                    'icon': url_for('static', filename='images/shapes.svg'),
                    'value': self.model.n_clusters
                }
            }
        else:
            metadata['features']['2_predict']['value'] += X.shape[0]
            
        return metadata


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

        # Update and save model metadata
        metadata = self.__generate_metadata(new_model=True, X=emb_50d)
        self._save_metadata(metadata)

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

        # Update metadata
        metadata = self.__generate_metadata(X=emb_50d)
        self._save_metadata(metadata)

        clusters = [Cluster(id = int(cluster_id)) for cluster_id in np.unique(labels)]

        return labels.tolist(), clusters
