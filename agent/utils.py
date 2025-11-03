import re

# Full list of Nigerian state capitals + major cities
NIGERIAN_CITIES = [
    "Abakaliki", "Abeokuta", "Abuja", "Ado Ekiti", "Akure", "Asaba", "Awka", "Bauchi", "Benin City",
    "Birnin Kebbi", "Calabar", "Damaturu", "Lagos", "Enugu", "Gombe", "Gusau", "Ibadan", "Ilorin",
    "Jalingo", "Jos", "Kaduna", "Kano", "Katsina", "Lafia", "Lokoja", "Maiduguri", "Makurdi",
    "Minna", "Oshogbo", "Ondo", "Owerri", "Port Harcourt", "Sokoto", "Umuahia", "Uyo", "Yenagoa",
    "Yola", "Aba", "Onitsha", "Warri"
]


def extract_latest_message_text(message_data):
    """
    Extracts the most recent relevant text from a Telex-style message.
    Focuses only on the last 2–3 parts to avoid confusion from older chat history.
    """
    try:
        parts = message_data.get("parts", [])
        if not parts:
            return ""

        # Consider only the last few parts (latest messages)
        recent_parts = parts[-3:]

        texts = []
        for part in recent_parts:
            if part.get("kind") == "text":
                texts.append(part.get("text", ""))
            elif part.get("kind") == "data":
                for sub in part.get("data", []):
                    if sub.get("kind") == "text":
                        texts.append(sub.get("text", ""))

        combined = " ".join(texts).strip()
        return combined
    except Exception:
        return ""


def extract_city_from_text(text):
    """
    Identifies a Nigerian city name from the text.
    Returns None if no known city is found.
    """
    if not text:
        return None

    for city in NIGERIAN_CITIES:
        pattern = rf"\b{re.escape(city)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            return city
    return None


def extract_power_status_from_text(text):
    """
    Extracts a user's report of 'light on' or 'light off' from text.
    """
    text = text.lower()
    if any(word in text for word in ["no light", "light off", "nepa take light", "power outage", "blackout"]):
        return "off"
    elif any(word in text for word in ["light is on", "light on", "there is light", "nepa bring light", "power restored"]):
        return "on"
    return None
