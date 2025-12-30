from flask import url_for

import os
import spacy
import numpy as np
from datetime import date
from scipy.sparse import csc_matrix, vstack, save_npz, load_npz
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from openTSNE import TSNE, TSNEEmbedding

from .base_model import Model







class _Norm(Model[Normalizer]):
    
    model_name = 'normalizer.joblib'

    def __init__(self):
        """Create a Normalizer instance, using Kmeans algorithm."""

        super().__init__()

    def fit_transform(self, X:np.ndarray) -> np.ndarray:
        model = Normalizer(copy=False)
        emb = model.fit_transform(X)
        self._save_model(model)
        return emb
    
    def transform(self, X:np.ndarray) -> np.ndarray:
        emb = self.model.transform(X)
        return emb



class _SVD(Model[TruncatedSVD]):

    model_name = 'svd.joblib'

    def __init__(self):
        """Create a SVD instance, using Kmeans algorithm."""
        super().__init__()
        self.normalizer = _Norm()

    def fit_transform(self, X:csc_matrix, n=50) -> np.ndarray:
        if X.shape[0] < n:
            raise Exception("X should contains more than n observations")
        
        model = TruncatedSVD(n_components=n)
        emb = self.normalizer.fit_transform(
            model.fit_transform(X)
        )
        self._save_model(model)

        return emb
    
    def transform(self, X) -> np.ndarray:
        emb = self.normalizer.transform(
            self.model.transform(X)
        )
        return emb
    

class _TSNE(Model[TSNEEmbedding]):

    model_name = 'tsne.joblib'

    def __init__(self):
        """Create a SVD instance, using Kmeans algorithm."""
        super().__init__()

    def fit_transform(self, X:np.ndarray, n=3, p=30) -> np.ndarray:
        p = min(p, X.shape[0]-1)
        model = TSNE(n_components=n, metric='cosine', perplexity=max(p, 0.5))
        emb = model.fit(X)
        self._save_model(emb)
        return np.asarray(emb, dtype=np.float32)
    
    def transform(self, X:np.ndarray) -> np.ndarray:
        emb = self.model.transform(X)
        return np.asarray(emb, dtype=np.float32)




class TFIDF(Model[TfidfVectorizer]):

    model_name = 'vectorizer.joblib'
    matrix_name = 'tfidf_matrix.npz'

    def __init__(self) -> None:
        """Create a TF-IDF instance, using TfidfVectorizer."""

        super().__init__()
        self.nlp = spacy.load("fr_core_news_sm", disable=["parser", "ner", "tagger"])
        self.englisg_stops = stopwords.words('english')
        self.svd = _SVD()
        self.tsne = _TSNE()

    def _spacy_tokenizer(self, _doc) -> list:
        """Tokenize with spaCy and keep only real tokens (no punctuation/space)."""

        doc = self.nlp(_doc)
        return [token.lemma_.lower()
                for token in doc
                if token.is_alpha and not token.is_punct and not token.is_space and not token.like_num and token.lemma_.lower() not in self.englisg_stops and len(token) > 1]
    
    def __generate_metadata(self, new_model=False, predict_size=0, X:csc_matrix=None):
        metadata = self.metadata

        if new_model:
            metadata['prefix'] = "Tf"
            metadata['version'] = (metadata.get('version') or 0) + 1
            metadata['date'] = date.today().isoformat()
            metadata['shape'] = X.shape[0]
            metadata['features'] = {
                '0_tokens': {
                    'label': 'Nombre de tokens',
                    'icon': url_for('static', filename='images/token.svg'),
                    'value': X.shape[1]
                },
                '1_fit': {
                    'label': "Taille de l'échantillon d'apprentissage",
                    'icon': url_for('static', filename='images/fit.svg'),
                    'value': X.shape[0]
                },
                '2_predict' : {
                    'label': "Nombre de prédictions",
                    'icon': url_for('static', filename='images/stack.svg'),
                    'value': 0
                },
                '3_min': {
                    'label': 'Occurrence minimale',
                    'icon': url_for('static', filename='images/min.svg'),
                    'value': self.model.min_df
                },
                '4_max': {
                    'label': 'Fréquence maximale',
                    'icon': url_for('static', filename='images/max.svg'),
                    'value': self.model.max_df
                }
            }

        metadata['features']['2_predict']['value'] += predict_size
        return metadata


    def _save_matrix(self, X:csc_matrix) -> None:
        path = os.path.join(self.model_path, self.matrix_name)
        save_npz(path, X)

    def _update_matrix(self, X:csc_matrix) -> None:
        X_prev, _ = self.load_matrix()
        X_all = vstack([X_prev, X], format='csc')
        self._save_matrix(X_all)


    def load_matrix(self) -> tuple[csc_matrix, np.ndarray]:
        """Load TD-IDF sparse matrix from files

        Returns:
            csc_matrix: TF-IDF sparse matrix
        """

        tokens = self.model.get_feature_names_out()
        path = os.path.join(self.model_path, self.matrix_name)
        X = load_npz(path)

        return X, tokens
    
    def fit_transform(self, corpus:list[str], min_df=3, max_df=0.5) -> tuple[np.ndarray, np.ndarray]:
        """Create a TF-IDF matrix from documents

        Args:
            corpus (list[str]): The list of documents to create a TF-IDF matrix on
            min_df (int): The minimum document occurence a term should have to be in the matrix. Default to 3
            max_df (float): The maximum document frequency a term can have to be in the matrix. Default to 0.5

        Returns:
            np.ndarray: 50 dimenssions reduction
            np.ndarray: 3 dimenssions reduction
        """

        model = TfidfVectorizer(
            tokenizer=self._spacy_tokenizer,    # use spaCy
            token_pattern=None,                 # disable default regex since we supply tokenizer
            min_df=min_df,                           # keep terms present in at least 3 docs
            max_df=max_df,                         # drop very common words
            dtype=np.float32
        )

        X = model.fit_transform(corpus)
        # Save sparse matrix and vectorizer model
        self._save_matrix(X)
        self._save_model(model)

        # Update and save metadata
        metadata = self.__generate_metadata(new_model=True, X=X)
        self._save_metadata(metadata)

        emb_50d = self.svd.fit_transform(X)
        emb_3d = self.tsne.fit_transform(emb_50d)

        
        return emb_50d, emb_3d
    
    def transform(self, corpus:list[str], save=False) -> tuple[np.ndarray, np.ndarray]:
        """Create a TF-IDF matrix from documents

        Args:
            corpus (list[str]): The list of documents to create a TF-IDF matrix on

        Returns:
            np.ndarray: 50 dimenssions reduction
            np.ndarray: 3 dimenssions reduction
        """

        if not self.model:
            raise Exception(f"Impossible to predict on {self.model_name} since the model doesn't exist yet. Use `fit_transform` method first to create the model")
        
        X = self.model.transform(corpus)
        
        if save:
            self._update_matrix(X)
            # Update and save metadata
            metadata = self.__generate_metadata(X=X)
            self._save_metadata(metadata)

        emb_50d = self.svd.transform(X)
        emb_3d = self.tsne.transform(emb_50d)

        return emb_50d, emb_3d