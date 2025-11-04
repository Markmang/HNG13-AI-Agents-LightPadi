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
    Extracts the most recent one or two user message texts from Telex message payload.
    Handles both 'parts' and nested 'data' messages.
    """
    try:
        parts = message_data.get("parts", [])
        if not parts:
            return ""

        texts = []

        for part in parts:
            # Handle normal text messages
            if part.get("kind") == "text" and part.get("text"):
                texts.append(part["text"].strip())

            # Handle nested 'data' text blocks (Telex format)
            if part.get("kind") == "data":
                for d in part.get("data", []):
                    if d.get("kind") == "text" and d.get("text"):
                        texts.append(d["text"].strip())

        if not texts:
            return ""

        # Combine the last two messages (Telex sometimes splits messages)
        latest_texts = texts[-2:] if len(texts) > 1 else texts[-1:]
        combined_text = " ".join(latest_texts)

        # Remove HTML tags like <p></p>
        combined_text = re.sub(r"<.*?>", "", combined_text)

        # Clean whitespace and lowercase for consistency
        clean_text = combined_text.strip().lower()

        print(f"🧠 Extracted latest user text: {clean_text}")  # for debugging
        return clean_text

    except Exception as e:
        print(f"⚠️ Error extracting text: {e}")
        return ""


def extract_city_from_text(text):
    """
    Identifies a Nigerian city name from the text.
    Returns None if no known city is found.
    """
    if not text:
        return None

    # Remove punctuation to catch cities followed by commas, etc.
    text_clean = re.sub(r"[^\w\s]", "", text)

    for city in NIGERIAN_CITIES:
        pattern = rf"\b{re.escape(city.lower())}\b"
        if re.search(pattern, text_clean.lower()):
            print(f"🏙️ City detected: {city}")
            return city
    return None


def extract_power_status_from_text(text):
    """
    Extracts a user's report of 'light on' or 'light off' from text.
    Returns 'on', 'off', or None.
    """
    text = text.lower()

    # 'No light' scenarios
    if any(word in text for word in [
        "no light", "light off", "nepa take light", "power outage", "blackout",
        "no electricity", "power gone", "light don go"
    ]):
        print("💡 Power status detected: OFF")
        return "off"

    # 'Light on' scenarios
    elif any(word in text for word in [
        "light is on", "light on", "there is light", "nepa bring light",
        "power restored", "light dey", "power don come"
    ]):
        print("💡 Power status detected: ON")
        return "on"

    return None
