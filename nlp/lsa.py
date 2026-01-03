import numpy as np
from pathlib import Path
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

from cv.parser import load_all_cvs
from cv.preprocess import clean_text
from nlp.vectorizer import load_and_prepare_offers, build_tfidf_matrix


def build_lsa_space(X_tfidf, n_components: int = 200, random_state: int = 42):
    """
    Construit l'espace LSA via TruncatedSVD.
    Retourne (svd, X_offers_lsa)
    """
    # n_components doit être < nb_features
    n_components = min(n_components, X_tfidf.shape[1] - 1)
    if n_components < 2:
        raise ValueError("n_components trop petit : vocabulaire insuffisant.")

    svd = TruncatedSVD(n_components=n_components, random_state=random_state)
    X_lsa = svd.fit_transform(X_tfidf)
    return svd, X_lsa


def rank_with_tfidf(cv_text: str, vectorizer, X_offers, df_offers, top_n: int = 10):
    """
    Ranking TF-IDF + cosine similarity.
    """
    cv_clean = clean_text(cv_text)
    X_cv = vectorizer.transform([cv_clean])
    scores = cosine_similarity(X_cv, X_offers)[0]

    idx = np.argsort(scores)[::-1][:top_n]
    out = df_offers.iloc[idx].copy()
    out["score_tfidf"] = scores[idx]
    return out, scores


def rank_with_lsa(cv_text: str, vectorizer, svd, X_offers_lsa, df_offers, top_n: int = 10):
    """
    Ranking LSA (TF-IDF -> SVD) + cosine similarity dans l'espace réduit.
    """
    cv_clean = clean_text(cv_text)
    X_cv_tfidf = vectorizer.transform([cv_clean])
    X_cv_lsa = svd.transform(X_cv_tfidf)

    scores = cosine_similarity(X_cv_lsa, X_offers_lsa)[0]

    idx = np.argsort(scores)[::-1][:top_n]
    out = df_offers.iloc[idx].copy()
    out["score_lsa"] = scores[idx]
    return out, scores


def compare_rankings(tfidf_top, lsa_top, id_col: str | None = None, k: int = 10):
    """
    Compare les Top-k:
    - overlap en nombre et en pourcentage
    - liste des titres communs / différents (si title existe)
    """
    # Si un ID unique existe, utilise-le; sinon utilise l'index pandas
    if id_col and id_col in tfidf_top.columns and id_col in lsa_top.columns:
        tfidf_set = set(tfidf_top[id_col].head(k).tolist())
        lsa_set = set(lsa_top[id_col].head(k).tolist())
    else:
        tfidf_set = set(tfidf_top.index[:k].tolist())
        lsa_set = set(lsa_top.index[:k].tolist())

    inter = tfidf_set.intersection(lsa_set)
    overlap = len(inter)
    pct = overlap / k * 100

    return overlap, pct, inter


if __name__ == "__main__":
    # Chemins robustes
    BASE_DIR = Path(__file__).resolve().parents[1]
    offers_path = BASE_DIR / "data" / "offer.csv"  # <-- ajuste si ton fichier s'appelle autrement
    cv_dir = BASE_DIR / "data" / "cv"

    # 1) Offres
    df_offers = load_and_prepare_offers(offers_path)

    # 2) TF-IDF
    vectorizer, X_offers_tfidf = build_tfidf_matrix(df_offers["clean_document"].tolist())

    # 3) LSA/SVD
    svd, X_offers_lsa = build_lsa_space(X_offers_tfidf, n_components=200)

    # 4) CV (premier CV du dossier)
    cvs = load_all_cvs(cv_dir)
    cv_name, cv_text = list(cvs.items())[0]

    # 5) Ranking comparatif
    top_n = 10
    tfidf_top, _ = rank_with_tfidf(cv_text, vectorizer, X_offers_tfidf, df_offers, top_n=top_n)
    lsa_top, _ = rank_with_lsa(cv_text, vectorizer, svd, X_offers_lsa, df_offers, top_n=top_n)

    # 6) Affichage
    print(f"\n===== TOP {top_n} TF-IDF pour : {cv_name} =====\n")
    for _, row in tfidf_top.iterrows():
        title = row["title"] if "title" in row else "(no title)"
        print(f"- {row['score_tfidf']:.3f} | {title}")

    print(f"\n===== TOP {top_n} LSA (SVD) pour : {cv_name} =====\n")
    for _, row in lsa_top.iterrows():
        title = row["title"] if "title" in row else "(no title)"
        print(f"- {row['score_lsa']:.3f} | {title}")

    # 7) Comparaison overlap
    overlap, pct, _ = compare_rankings(tfidf_top, lsa_top, id_col=None, k=top_n)
    print(f"\nOverlap Top-{top_n} TF-IDF vs LSA : {overlap}/{top_n} ({pct:.1f}%)")

    # 8) Qualité SVD (info utile)
    explained = svd.explained_variance_ratio_.sum()
    print(f"Variance expliquée cumulée (SVD) : {explained:.3f}")
