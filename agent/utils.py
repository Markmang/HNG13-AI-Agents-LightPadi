import re
from .ai_engine import NIGERIAN_CITIES


def extract_message_text(telex_message: dict) -> str:
    """
    Extracts user-readable text from Telex messages,
    safely handling nested parts and data arrays.
    """
    parts = telex_message.get("parts", [])
    texts = []

    for part in parts:
        # Direct text
        if "text" in part and part["text"].strip():
            texts.append(part["text"].strip())

        # Nested 'data'
        if "data" in part:
            for data_part in part["data"]:
                if "text" in data_part and data_part["text"].strip():
                    texts.append(data_part["text"].strip())

    return texts[-1] if texts else ""


def extract_city_from_text(text: str):
    """
    Extract the first valid Nigerian city name from user input.
    """
    text = text.strip().title()

    # Try "in {city}" pattern first
    match = re.search(r"\b(?:in|at|from|location)\s+([A-Z][a-zA-Z\s]+)", text)
    if match:
        possible_city = match.group(1).strip()
        for city in NIGERIAN_CITIES:
            if city.lower() in possible_city.lower():
                return city

    # Fallback: direct name match
    for city in NIGERIAN_CITIES:
        if city.lower() in text.lower():
            return city

    return None
