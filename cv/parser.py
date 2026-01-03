import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extrait le texte brut d'un fichier PDF.
    """
    doc = fitz.open(pdf_path)
    pages_text = []

    for page in doc:
        text = page.get_text()
        if text:
            pages_text.append(text)

    doc.close()
    return "\n".join(pages_text)


def load_all_cvs(cv_dir: Path) -> dict:
    """
    Charge tous les CV PDF d'un dossier.
    Retourne un dictionnaire :
    { nom_cv: texte }
    """
    cvs = {}

    for pdf_file in cv_dir.glob("*.pdf"):
        cvs[pdf_file.stem] = extract_text_from_pdf(pdf_file)

    return cvs


if __name__ == "__main__":
    cv_directory = Path("data/cv")
    cvs = load_all_cvs(cv_directory)

    for name, text in cvs.items():
        print(f"\n===== CV : {name} =====")
        print(text[:1000])  # aperçu
