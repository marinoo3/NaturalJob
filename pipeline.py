import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

from cv.parser import load_all_cvs
from cv.preprocess import clean_text
from nlp.vectorizer import load_and_prepare_offers, build_tfidf_matrix
from nlp.lsa import build_lsa_space


def fit_models(offers_csv: Path, n_components: int = 200):
    """
    Fit sur les offres uniquement:
    - préparation + clean
    - TF-IDF
    - LSA (SVD)
    Retourne (df_offers, vectorizer, X_offers_tfidf, svd, X_offers_lsa)
    """
    df_offers = load_and_prepare_offers(offers_csv)
    vectorizer, X_offers_tfidf = build_tfidf_matrix(df_offers["clean_document"].tolist())
    svd, X_offers_lsa = build_lsa_space(X_offers_tfidf, n_components=n_components)
    return df_offers, vectorizer, X_offers_tfidf, svd, X_offers_lsa


def rank_offers_tfidf(cv_text: str, vectorizer, X_offers_tfidf, df_offers: pd.DataFrame, top_n: int = 10):
    cv_clean = clean_text(cv_text)
    X_cv = vectorizer.transform([cv_clean])
    scores = cosine_similarity(X_cv, X_offers_tfidf)[0]
    idx = np.argsort(scores)[::-1][:top_n]
    out = df_offers.iloc[idx].copy()
    out["score"] = scores[idx]
    out["method"] = "tfidf"
    return out


def rank_offers_lsa(cv_text: str, vectorizer, svd, X_offers_lsa, df_offers: pd.DataFrame, top_n: int = 10):
    cv_clean = clean_text(cv_text)
    X_cv_tfidf = vectorizer.transform([cv_clean])
    X_cv_lsa = svd.transform(X_cv_tfidf)
    scores = cosine_similarity(X_cv_lsa, X_offers_lsa)[0]
    idx = np.argsort(scores)[::-1][:top_n]
    out = df_offers.iloc[idx].copy()
    out["score"] = scores[idx]
    out["method"] = "lsa"
    return out


def run_for_one_cv(
    cv_name: str,
    cv_text: str,
    df_offers: pd.DataFrame,
    vectorizer,
    X_offers_tfidf,
    svd,
    X_offers_lsa,
    top_n: int = 10
):
    tfidf_top = rank_offers_tfidf(cv_text, vectorizer, X_offers_tfidf, df_offers, top_n=top_n)
    lsa_top = rank_offers_lsa(cv_text, vectorizer, svd, X_offers_lsa, df_offers, top_n=top_n)

    # overlap 
    overlap = len(set(tfidf_top.index).intersection(set(lsa_top.index)))
    overlap_pct = (overlap / top_n) * 100

    return tfidf_top, lsa_top, overlap, overlap_pct


def export_outputs(out_dir: Path, cv_name: str, tfidf_top: pd.DataFrame, lsa_top: pd.DataFrame, overlap: int, overlap_pct: float):
    out_dir.mkdir(parents=True, exist_ok=True)

    tfidf_file = out_dir / f"{cv_name}_top_tfidf.csv"
    lsa_file = out_dir / f"{cv_name}_top_lsa.csv"
    summary_file = out_dir / "summary.csv"

    tfidf_top.to_csv(tfidf_file, index=False, encoding="utf-8")
    lsa_top.to_csv(lsa_file, index=False, encoding="utf-8")

    row = pd.DataFrame([{
        "cv_name": cv_name,
        "top_n": len(tfidf_top),
        "overlap_count": overlap,
        "overlap_percent": round(overlap_pct, 1),
    }])

    if summary_file.exists():
        old = pd.read_csv(summary_file)
        pd.concat([old, row], ignore_index=True).to_csv(summary_file, index=False, encoding="utf-8")
    else:
        row.to_csv(summary_file, index=False, encoding="utf-8")

    return tfidf_file, lsa_file, summary_file


def run_pipeline(
    offers_csv: Path,
    cv_dir: Path,
    out_dir: Path,
    top_n: int = 10,
    n_components: int = 200
):
    df_offers, vectorizer, X_offers_tfidf, svd, X_offers_lsa = fit_models(offers_csv, n_components=n_components)

    cvs = load_all_cvs(cv_dir)
    if not cvs:
        raise ValueError(f"Aucun CV trouvé dans {cv_dir}")

    for cv_name, cv_text in cvs.items():
        tfidf_top, lsa_top, overlap, overlap_pct = run_for_one_cv(
            cv_name, cv_text, df_offers, vectorizer, X_offers_tfidf, svd, X_offers_lsa, top_n=top_n
        )
        tfidf_file, lsa_file, summary_file = export_outputs(out_dir, cv_name, tfidf_top, lsa_top, overlap, overlap_pct)

        print(f"\n===== {cv_name} =====")
        print(f"Overlap Top-{top_n} TF-IDF vs LSA : {overlap}/{top_n} ({overlap_pct:.1f}%)")
        print(f"Saved: {tfidf_file.name}, {lsa_file.name}")
        print(f"Summary: {summary_file.name}")
