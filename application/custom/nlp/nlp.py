from .process.cluster import Kmeans
from .process.tfidf import TFIDF


class NLP:

    def __init__(self) -> None:
        self.tfidf = TFIDF()
        self.kmeans = Kmeans()