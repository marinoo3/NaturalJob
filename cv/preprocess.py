import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# À lancer UNE SEULE FOIS
nltk.download("stopwords")
nltk.download("wordnet")


STOPWORDS_FR = set(stopwords.words("french"))
lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Nettoie et normalise un texte (CV ou annonce).
    Retourne une chaîne prête pour la vectorisation.
    """

    # minuscules
    text = text.lower()

    # suppression emails / téléphones
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\b\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b", " ", text)

    # suppression caractères spéciaux
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", " ", text)

    # tokenisation simple
    tokens = text.split()

    # suppression stopwords + lemmatisation
    tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token not in STOPWORDS_FR and len(token) > 2
    ]

    return " ".join(tokens)


if __name__ == "__main__":
    from parser import load_all_cvs
    from pathlib import Path

    cvs = load_all_cvs(Path("data/cv"))

    for name, raw_text in cvs.items():
        clean = clean_text(raw_text)
        print(f"\n===== CV NETTOYÉ : {name} =====")
        print(clean[:800])
