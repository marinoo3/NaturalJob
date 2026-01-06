import pandas as pd
from pathlib import Path

from cv.parser import load_all_cvs
from nlp.vectorizer import load_and_prepare_offers, build_tfidf_matrix
from nlp.lsa import build_lsa_space, rank_with_tfidf, rank_with_lsa, compare_rankings


def export_results(cv_name, tfidf_top, lsa_top, overlap, pct, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarde Top TF-IDF
    tfidf_out = out_dir / f"{cv_name}_top_tfidf.csv"
    tfidf_top.to_csv(tfidf_out, index=False, encoding="utf-8")

    # Sauvegarde Top LSA
    lsa_out = out_dir / f"{cv_name}_top_lsa.csv"
    lsa_top.to_csv(lsa_out, index=False, encoding="utf-8")

    # Petit résumé (1 ligne)
    summary_out = out_dir / "summary.csv"
    row = pd.DataFrame([{
        "cv_name": cv_name,
        "top_n": len(tfidf_top),
        "overlap_count": overlap,
        "overlap_percent": round(pct, 1),
    }])

    if summary_out.exists():
        old = pd.read_csv(summary_out)
        new = pd.concat([old, row], ignore_index=True)
        new.to_csv(summary_out, index=False, encoding="utf-8")
    else:
        row.to_csv(summary_out, index=False, encoding="utf-8")

    return tfidf_out, lsa_out, summary_out


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[1]
    offers_path = BASE_DIR / "data" / "offer.csv"   # <-- ton nom de fichier
    cv_dir = BASE_DIR / "data" / "cv"
    out_dir = BASE_DIR / "data" / "outputs"

    # 1) Préparer offres
    df_offers = load_and_prepare_offers(offers_path)

    # 2) Fit TF-IDF sur offres
    vectorizer, X_offers_tfidf = build_tfidf_matrix(df_offers["clean_document"].tolist())

    # 3) Fit LSA sur TF-IDF offres
    svd, X_offers_lsa = build_lsa_space(X_offers_tfidf, n_components=200)

    # 4) Charger tous les CV
    cvs = load_all_cvs(cv_dir)

    top_n = 10

    for cv_name, cv_text in cvs.items():
        tfidf_top, _ = rank_with_tfidf(cv_text, vectorizer, X_offers_tfidf, df_offers, top_n=top_n)
        lsa_top, _ = rank_with_lsa(cv_text, vectorizer, svd, X_offers_lsa, df_offers, top_n=top_n)

        overlap, pct, _ = compare_rankings(tfidf_top, lsa_top, id_col=None, k=top_n)

        print(f"\n===== {cv_name} =====")
        print(f"Overlap Top-{top_n} TF-IDF vs LSA : {overlap}/{top_n} ({pct:.1f}%)")

        tfidf_file, lsa_file, summary_file = export_results(
            cv_name=cv_name,
            tfidf_top=tfidf_top,
            lsa_top=lsa_top,
            overlap=overlap,
            pct=pct,
            out_dir=out_dir
        )

        print(f"Saved: {tfidf_file.name}, {lsa_file.name}")
        print(f"Summary: {summary_file.name}")
