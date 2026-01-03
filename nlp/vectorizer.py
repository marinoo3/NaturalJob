import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path

from cv.preprocess import clean_text


def load_and_prepare_offers(csv_path: Path) -> pd.DataFrame:
    """
    Charge les offres et construit le document texte (ligne par ligne).
    """
    df = pd.read_csv(csv_path)

    text_cols = []

    if "title" in df.columns:
        text_cols.append("title")
    if "description" in df.columns:
        text_cols.append("description")
    if "skills" in df.columns:
        text_cols.append("skills")

    if not text_cols:
        raise ValueError("Aucune colonne texte trouvée dans offers.csv")

    # Remplacer NaN par chaînes vides
    df[text_cols] = df[text_cols].fillna("")

    # Concaténation ligne par ligne
    df["document"] = df[text_cols].agg(" ".join, axis=1)

    # Nettoyage NLP
    df["clean_document"] = df["document"].apply(clean_text)

    return df



def build_tfidf_matrix(documents: list[str]):
    """
    Entraîne TF-IDF sur les documents annonces.
    """
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_df=0.85,
        min_df=2
    )

    X = vectorizer.fit_transform(documents)
    return vectorizer, X


if __name__ == "__main__":
    offers_path = Path("data/offer.csv")
    df_offers = load_and_prepare_offers(offers_path)

    vectorizer, X_offers = build_tfidf_matrix(df_offers["clean_document"])

    print("TF-IDF matrix shape:", X_offers.shape)
    print("Nombre de termes:", len(vectorizer.get_feature_names_out()))
