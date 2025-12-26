import os
import spacy
import numpy as np
from scipy.sparse import csc_matrix, save_npz, load_npz
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer

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
    

class _TSNE(Model[])




class TFIDF(Model[TfidfVectorizer]):

    model_name = 'vectorizer.joblib'
    matrix_name = 'tfidf_matrix.npz'

    def __init__(self) -> None:
        """Create a TF-IDF instance, using TfidfVectorizer."""

        super().__init__()
        self.nlp = spacy.load("fr_core_news_sm", disable=["parser", "ner", "tagger"])
        self.englisg_stops = stopwords.words('english')
        self.svd = _SVD()

    def _spacy_tokenizer(self, _doc) -> list:
        """Tokenize with spaCy and keep only real tokens (no punctuation/space)."""

        doc = self.nlp(_doc)
        return [token.lemma_.lower()            # or token.lemma_.lower() if you prefer lemmas
                for token in doc
                if token.is_alpha and not token.is_punct and not token.is_space and not token.like_num and token.lemma_.lower() not in self.englisg_stops and len(token) > 1]
    
    def _save_matrix(self, X:csc_matrix) -> None:
        path = os.path.join(self.model_path, self.matrix_name)
        save_npz(path, X)

    def load_matrix(self) -> tuple[csc_matrix, np.ndarray]:
        """Load TD-IDF sparse matrix from files

        Returns:
            csc_matrix: TF-IDF sparse matrix
        """

        tokens = self.model.get_feature_names_out()
        path = os.path.join(self.model_path, self.matrix_name)
        X = load_npz(path)

        return X, tokens
    
    def fit_transform(self, corpus:list[str]) -> tuple[np.ndarray, np.ndarray]:
        """Create a TF-IDF matrix from documents

        Args:
            corpus (list[str]): The list of documents to create a TF-IDF matrix on

        Returns:
            np.ndarray: 50 dimenssions reduction
            np.ndarray: 3 dimenssions reduction
        """

        model = TfidfVectorizer(
            tokenizer=self._spacy_tokenizer,   # use spaCy
            token_pattern=None,                 # disable default regex since we supply tokenizer
            min_df=3,                           # keep terms present in at least 3 docs
            max_df=0.5,                         # drop very common words
            dtype=np.float32
        )

        X = model.fit_transform(corpus)

        # Save sparse matrix and vectorizer model
        self._save_matrix(X)
        self._save_model(model)

        p = min(30, X.shape[0]-1)
        tsne = TSNE(n_components=3, metric='cosine', init='pca', perplexity=max(1, p))
        emb_50d = self.svd.fit_transform(X)
        emb_3d = tsne.fit_transform(emb_50d)
        
        return emb_50d, emb_3d
    
    def transform(self, corpus:list[str]) -> tuple[np.ndarray, np.ndarray]:
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
        print('DTYPE:', X.dtype, flush=True)
        p = min(30, X.shape[0]-1)
        tsne = TSNE(n_components=3, metric='cosine', init='pca', perplexity=max(.5, p))
        emb_50d = self.svd.transform(X)
        print(emb_50d.dtype, flush=True)
        emb_3d = tsne.fit_transform(emb_50d)

        return emb_50d, emb_3d