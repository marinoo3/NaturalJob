import spacy
import numpy as np
from scipy.sparse import csc_matrix
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer

from .base_model import Model





class Reduce:

    """Reduce dimensions using TruncatedSVD or t-SNE"""

    @staticmethod
    def svd(X:csc_matrix, n=50) -> np.ndarray:
        svd = TruncatedSVD(n_components=n)
        normalizer = Normalizer(copy=False)
        emb = normalizer.fit_transform(svd.fit_transform(X))
        return emb
    
    @staticmethod
    def tsne(X:np.ndarray, n=3, p=30) -> np.ndarray:
        tsne = TSNE(n_components=n, metric='cosine', init='pca', perplexity=min(p, len(X)))
        emb = tsne.fit_transform(X)
        return emb



class TFIDF(Model[TfidfVectorizer]):

    model_name = 'vectorizer.joblib'

    def __init__(self) -> None:
        """Create a TF-IDF instance, using TfidfVectorizer."""

        super().__init__()
        self.nlp = spacy.load("fr_core_news_sm", disable=["parser", "ner", "tagger"])
        self.englisg_stops = stopwords.words('english')

    def _spacy_tokenizer(self, _doc) -> list:
        """Tokenize with spaCy and keep only real tokens (no punctuation/space)."""

        doc = self.nlp(_doc)
        return [token.lemma_.lower()            # or token.lemma_.lower() if you prefer lemmas
                for token in doc
                if token.is_alpha and not token.is_punct and not token.is_space and not token.like_num and token.lemma_.lower() not in self.englisg_stops and len(token) > 1]
    
    def fit_transform(self, corpus:list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create a TF-IDF matrix from documents

        Args:
            corpus (list[str]): The list of documents to create a TF-IDF matrix on

        Returns:
            np.ndarray: 50 dimension TF-IDF reduction
            np.ndarray: 3 dimension TF-IDF reduction
            np.ndarray: List of TF-IDF tokens
        """

        model = TfidfVectorizer(
            tokenizer=self._spacy_tokenizer,   # use spaCy
            token_pattern=None,                 # disable default regex since we supply tokenizer
            min_df=3,                           # keep terms present in at least 3 docs
            max_df=0.5,                         # drop very common words
            dtype=np.float32
        )
        X = model.fit_transform(corpus)
        self._save_model(model)

        emb_50d = Reduce.svd(X)
        emb_3d = Reduce.tsne(emb_50d)
        tokens = np.array(self.model.get_feature_names_out())
        
        return emb_50d, emb_3d, tokens
    
    def transform(self, corpus:list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create a TF-IDF matrix from documents

        Args:
            corpus (list[str]): The list of documents to create a TF-IDF matrix on

        Returns:
            np.ndarray: 50 dimension TF-IDF reduction
            np.ndarray: 3 dimension TF-IDF reduction
            np.ndarray: List of TF-IDF tokens
        """

        if not self.model:
            raise Exception(f"Impossible to predict on {self.model_name} since the model doesn't exist yet. Use `fit_transform` method first to create the model")
        
        X = self.model.transform(corpus)
        emb_50d = Reduce.svd(X)
        emb_3d = Reduce.tsne(emb_50d)
        tokens = np.array(self.model.get_feature_names_out())

        return emb_50d, emb_3d, tokens