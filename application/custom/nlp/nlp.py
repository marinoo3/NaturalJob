from .process.cluster import Kmeans
from .process.tfidf import TFIDF
from .process.llm import LLM


class NLP:

    def __init__(self) -> None:
        self.tfidf = TFIDF()
        self.kmeans = Kmeans()
        self.llm = LLM()