import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

from cv.parser import load_all_cvs
from cv.preprocess import clean_text
from nlp.vectorizer import load_and_prepare_offers, build_tfidf_matrix


def rank_offers_for_cv(
    cv_text: str,
    vectorizer,
    X_offers,
    df_offers,
    top_n: int = 10
):
    """
    Classe les offres par similarité avec le CV.
    """
    cv_clean = clean_text(cv_text)
    X_cv = vectorizer.transform([cv_clean])

    scores = cosine_similarity(X_cv, X_offers)[0]

    ranked_idx = np.argsort(scores)[::-1][:top_n]

    results = df_offers.iloc[ranked_idx].copy()
    results["similarity_score"] = scores[ranked_idx]

    return results


if __name__ == "__main__":
    # 1. Charger les offres
    offers_path = Path("data/offer.csv")
    df_offers = load_and_prepare_offers(offers_path)

    vectorizer, X_offers = build_tfidf_matrix(df_offers["clean_document"])

    # 2. Charger le CV
    cvs = load_all_cvs(Path("data/cv"))
    cv_name, cv_text = list(cvs.items())[0]  # premier CV

    # 3. Ranking
    results = rank_offers_for_cv(
        cv_text=cv_text,
        vectorizer=vectorizer,
        X_offers=X_offers,
        df_offers=df_offers,
        top_n=10
    )

    print(f"\n===== TOP 10 OFFRES POUR : {cv_name} =====\n")

    for i, row in results.iterrows():
        print(f"- Score: {row['similarity_score']:.3f}")
        if "title" in row:
            print(f"  Titre: {row['title']}")
        print()
