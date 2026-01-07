import re
from typing import Dict, Any, List


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def _truncate_to_words(text: str, max_words: int) -> str:
    words = re.findall(r"\b\w+\b|\S", text, flags=re.UNICODE)
    # On reconstruit de façon simple (on ne garde pas ponctuation parfaite mais ça reste correct)
    out = []
    count = 0
    for tok in words:
        # compter seulement les mots
        if re.match(r"\b\w+\b", tok, flags=re.UNICODE):
            count += 1
        out.append(tok)
        if count >= max_words:
            break
    s = " ".join(out)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return s.strip()


def make_variants(letter_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: JSON issu de letter_llm.py
    Output: même JSON + variantes calculées.
    """
    base_letter = (letter_json.get("letter") or "").strip()
    if not base_letter:
        raise ValueError("letter est vide.")

    variants = {}

    # 1) Classique = inchangé
    variants["classique"] = base_letter

    # 2) Très concise ~150 mots
    variants["concise_150"] = _truncate_to_words(base_letter, 150)

    # 3) Orientée résultats:
    # simple règle: mettre les bullets (si existantes) en début du corps
    bullets: List[str] = letter_json.get("bullets_strengths") or []
    bullets_clean = [b.strip("-• \t") for b in bullets if isinstance(b, str) and b.strip()]
    if bullets_clean:
        bullet_block = "\n".join([f"- {b}" for b in bullets_clean[:3]])
        variants["resultats"] = bullet_block + "\n\n" + base_letter
    else:
        variants["resultats"] = base_letter  # fallback

    return {
        **letter_json,
        "variants": variants,
        "word_count": _count_words(base_letter),
    }


def make_ats_friendly(letter_text: str, keywords: List[str], max_keywords: int = 18) -> str:
    """
    Version ATS-friendly: ajoute un bloc "Mots-clés" en fin de lettre,
    basé sur keywords_used (déjà validés côté letter_llm).
    """
    clean = (letter_text or "").strip()
    kws = []
    seen = set()
    for k in keywords or []:
        k = str(k).strip()
        if not k:
            continue
        low = k.lower()
        if low not in seen:
            seen.add(low)
            kws.append(k)
        if len(kws) >= max_keywords:
            break

    if not kws:
        return clean

    block = "Mots-clés : " + ", ".join(kws)
    return clean + "\n\n" + block


def quick_sanity_check(letter_text: str) -> None:
    """
    Vérifs rapides (règles simples) : pas de lettre vide, pas trop courte.
    """
    t = (letter_text or "").strip()
    if len(t) < 50:
        raise ValueError("Lettre trop courte ou vide.")
