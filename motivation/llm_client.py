import os
import json
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from mistralai import Mistral


def _extract_text_content(chat_response) -> str:
    """
    La réponse Mistral peut renvoyer content en string OU en liste de chunks.
    On normalise en texte brut.
    """
    msg = chat_response.choices[0].message
    content = msg.content

    if isinstance(content, str):
        return content

    # content peut être une liste de chunks {type: "text", text: "..."} etc.
    if isinstance(content, list):
        parts = []
        for chunk in content:
            if isinstance(chunk, dict) and chunk.get("type") == "text":
                parts.append(chunk.get("text", ""))
            elif isinstance(chunk, str):
                parts.append(chunk)
        return "".join(parts).strip()

    return str(content).strip()


def parse_json_text(text: str) -> Dict[str, Any]:
    """
    Parse robuste d'un JSON renvoyé par un LLM:
    - supprime caractères de contrôle invalides
    - tente json.loads direct
    - sinon extrait le premier bloc {...} ou [...]
    """
    # Normalisation anti "Invalid control character"
    text = "".join(
        ch for ch in text
        if ch in ("\n", "\r", "\t") or ord(ch) >= 32
    ).strip()

    # Essai direct
    try:
        return json.loads(text)
    except Exception:
        pass

    # Extraction objet JSON
    start_obj = text.find("{")
    end_obj = text.rfind("}")
    if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
        candidate = text[start_obj:end_obj + 1]
        candidate = "".join(
            ch for ch in candidate
            if ch in ("\n", "\r", "\t") or ord(ch) >= 32
        )
        return json.loads(candidate)

    # Extraction tableau JSON
    start_arr = text.find("[")
    end_arr = text.rfind("]")
    if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
        candidate = text[start_arr:end_arr + 1]
        candidate = "".join(
            ch for ch in candidate
            if ch in ("\n", "\r", "\t") or ord(ch) >= 32
        )
        return json.loads(candidate)

    raise ValueError("Impossible de parser du JSON depuis la réponse du modèle.")


class MistralLLMClient:
    def __init__(self, model: str = "mistral-large-latest", api_key: Optional[str] = None):
        api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError(
                "MISTRAL_API_KEY introuvable. Mets-la dans ton .env puis charge-la avec python-dotenv."
            )
        self.client = Mistral(api_key=api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        """
        Retourne du texte (idéalement du JSON si ton prompt l'exige).
        """
        messages: List[Dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        chat_response = self.client.chat.complete(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return _extract_text_content(chat_response)

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> Dict[str, Any]:
        """
        Force une sortie JSON (parse robuste).
        """
        text = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return parse_json_text(text)
