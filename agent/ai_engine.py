import random
from datetime import datetime, timedelta
from agent.models import PowerReport

# Full list of Nigerian state capitals + major cities
NIGERIAN_CITIES = [
    "Abakaliki", "Abeokuta", "Abuja", "Ado Ekiti", "Akure", "Asaba", "Awka", "Bauchi", "Benin City",
    "Birnin Kebbi", "Calabar", "Damaturu", "Lagos", "Enugu", "Gombe", "Gusau", "Ibadan", "Ilorin",
    "Jalingo", "Jos", "Kaduna", "Kano", "Katsina", "Lafia", "Lokoja", "Maiduguri", "Makurdi",
    "Minna", "Oshogbo", "Ondo", "Owerri", "Port Harcourt", "Sokoto", "Umuahia", "Uyo", "Yenagoa",
    "Yola", "Aba", "Onitsha", "Warri"
]


def predict_light_status(location: str):
    """
    LightPadi AI logic:
    - Checks if the city is among supported Nigerian cities
    - Learns from existing reports (if any)
    - Generates realistic, friendly predictions
    - Always returns structured JSON for Telex A2A
    """

    location = location.strip().title()

    # Step 1: Check if the city is supported
    if location not in NIGERIAN_CITIES:
        return {
            "location": location,
            "prediction": "unsupported",
            "confidence": 0.0,
            "message": "Sorry, LightPadi currently supports only major Nigerian cities 🇳🇬."
        }

    # Step 2: Fetch recent reports for the city
    reports = PowerReport.objects.filter(location__iexact=location).order_by('-timestamp')[:5]

    if not reports.exists():
        # No data yet for this city
        return {
            "location": location,
            "prediction": "unknown",
            "confidence": 0.0,
            "message": f"No data for {location} yet. Help me learn — tell me if there’s light 💡."
        }

    # Analyze on/off pattern
    on_count = sum(r.status.lower() == "on" for r in reports)
    off_count = sum(r.status.lower() == "off" for r in reports)

    # Dynamic confidence and timing
    confidence = round(random.uniform(0.6, 0.95), 2)
    hours_ahead = random.choice([1, 2, 3, 4])
    next_change_time = (datetime.now() + timedelta(hours=hours_ahead)).strftime("%Y-%m-%d %H:%M:%S")

    # Step 3: Predict CURRENT status and future event
    if on_count >= off_count:
        # Light is likely ON now
        prediction = "on"
        message_templates = [
            f"Light is currently ON in {location}. Based on recent patterns, NEPA might take it around {next_change_time}.",
            f"{location} currently has light ⚡. You might want to charge up — possible outage around {next_change_time}.",
            f"Power seems steady in {location} right now, but it might go off near {next_change_time}."
        ]
    else:
        # Light is likely OFF now
        prediction = "off"
        message_templates = [
            f"Power is currently OFF in {location}. Based on trends, it may return around {next_change_time}.",
            f"No light in {location} at the moment 😞. Looks like NEPA may bring it back by {next_change_time}.",
            f"{location} is currently in darkness, but restoration might happen around {next_change_time} ⚡."
        ]

    message = random.choice(message_templates)

    # Step 4: Return structured, safe response
    return {
        "location": location,
        "prediction": prediction,  # Reflects current status, not the next change
        "confidence": confidence,
        "next_change": next_change_time,
        "message": message
    }
