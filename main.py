from pathlib import Path
from pipeline import run_pipeline

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    offers_csv = BASE_DIR / "data" / "offer.csv"
    cv_dir = BASE_DIR / "data" / "cv"
    out_dir = BASE_DIR / "data" / "outputs"

    run_pipeline(
        offers_csv=offers_csv,
        cv_dir=cv_dir,
        out_dir=out_dir,
        top_n=10,
        n_components=200
    )
