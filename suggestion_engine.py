# suggestion_engine.py

import random

# ------------------------------
# Temperature feel classification
# ------------------------------
def _temp_feel(temp, feels_like):
    t = feels_like if feels_like is not None else temp

    if t >= 38:
        return "extremely hot"
    if t >= 32:
        return "very hot"
    if t >= 27:
        return "warm"
    if t >= 20:
        return "mild"
    if t >= 12:
        return "cool"
    if t >= 5:
        return "cold"
    return "freezing"


# ------------------------------
# AI — CAST TODAY (SUMMARY)
# Highly varied and city-specific
# ------------------------------
def build_summary(city, country, desc, temp, feels, humidity, wind):
    feel_word = _temp_feel(temp, feels)

    templates = [
        f"In {city}, {country}, the day feels {feel_word} with {desc.lower()} conditions dominating.",
        f"{city} is experiencing {desc.lower()} weather today, with the atmosphere feeling {feel_word}.",
        f"Across {city}, the climate leans toward {feel_word} conditions with periods of {desc.lower()}.",
        f"The weather in {city} feels {feel_word}, paired with {desc.lower()} skies.",
        f"{city} today shows a mix of {desc.lower()} weather, and temperatures feel {feel_word} for most people.",
    ]

    humidity_line = (
        "Humidity is noticeably high" if humidity > 75
        else "Humidity levels remain comfortable" if humidity < 50
        else "Humidity sits at a moderate level"
    )

    wind_line = (
        "winds are quite strong, adding some chill"
        if wind > 35
        else "there is a light breeze throughout the day"
        if wind > 12
        else "winds stay calm and gentle"
    )

    return f"{random.choice(templates)}. {humidity_line}, and {wind_line}."


# ------------------------------
# SAFETY TODAY — dynamic & varied
# ------------------------------
def build_safety(temp, humidity, wind, desc):
    tips = []

    # Temperature safety
    if temp >= 35:
        tips.append("Limit long outdoor exposure and stay hydrated.")
    elif temp <= 5:
        tips.append("Cold conditions may require protective layering.")

    # Humidity safety
    if humidity >= 85:
        tips.append("High humidity may reduce visibility and cause discomfort.")
    elif humidity <= 35:
        tips.append("Dry air may irritate skin or throat.")

    # Wind safety
    if wind >= 40:
        tips.append("Strong winds may disrupt outdoor plans; proceed with caution.")
    elif wind >= 20:
        tips.append("Moderate winds may affect comfort, especially in open areas.")

    # Description-based safety
    d = desc.lower()
    if "rain" in d:
        tips.append("Roads and surfaces may be slippery; watch your step.")
    if "storm" in d or "thunder" in d:
        tips.append("Avoid open spaces due to storm risk.")
    if "snow" in d:
        tips.append("Snow may cause reduced traction; move carefully.")
    if "fog" in d or "mist" in d:
        tips.append("Fog may reduce visibility—drive or walk carefully.")

    if not tips:
        return "No significant safety concerns today for most people."

    return " ".join(tips)


# ------------------------------
# CLIMATE INSIGHT — unique & smart
# ------------------------------
def build_insight(temp, feels, humidity, wind, desc):
    feel_word = _temp_feel(temp, feels)
    d = desc.lower()

    temp_insights = {
        "extremely hot": [
            "Heat levels may feel intense during peak hours.",
            "The warmth may cause quick fatigue outdoors.",
        ],
        "very hot": [
            "The day may feel heavier in the sun.",
            "Shade will feel noticeably more comfortable.",
        ],
        "warm": [
            "The warmth provides an inviting outdoor feel.",
            "Most people find this temperature range pleasant.",
        ],
        "mild": [
            "Mild conditions support comfortable outdoor plans.",
            "A balanced temperature makes the day feel steady.",
        ],
        "cool": [
            "Cool air may add freshness, especially in the evening.",
            "You may feel a slight chill in shaded areas.",
        ],
        "cold": [
            "Cold air may impact comfort without layering.",
            "Winds can enhance the cold sensation.",
        ],
        "freezing": [
            "Freezing air may limit outdoor exposure.",
            "Extra layers are essential for comfort today.",
        ],
    }

    humidity_insights = (
        "Expect the air to feel heavy due to humidity."
        if humidity > 80 else
        "Dryness may make conditions feel sharper."
        if humidity < 40 else
        "Humidity remains moderate with no major discomfort expected."
    )

    wind_insights = (
        "Winds may feel harsh at times." if wind > 40 else
        "A steady breeze may be noticeable throughout the day." if wind > 20 else
        "Winds stay soft and calm today."
    )

    # pick random temperature insight for higher variation
    temp_line = random.choice(temp_insights[feel_word])

    # description insight
    if "rain" in d:
        desc_line = "Rain may influence mood and outdoor convenience."
    elif "snow" in d:
        desc_line = "Snow adds a crisp feel to the environment."
    elif "storm" in d:
        desc_line = "Storm conditions may cause sudden atmospheric shifts."
    elif "fog" in d or "mist" in d:
        desc_line = "Mist can soften the atmosphere and reduce clarity."
    elif "cloud" in d:
        desc_line = "Cloud cover may create a muted daylight tone."
    else:
        desc_line = "Clear skies keep the atmosphere simple and bright."

    return f"{temp_line} {humidity_insights} {wind_insights} {desc_line}"


# ------------------------------
#  MAIN ENGINE
# ------------------------------
def generate_ai_weather_guide(
    city,
    country,
    temp,
    feels_like,
    humidity,
    pressure,
    wind_speed_kmh,
    category,
    description,
    hourly,
    daily,
    timezone_offset,
):
    summary = build_summary(city, country, description, temp, feels_like, humidity, wind_speed_kmh)
    safety = build_safety(temp, humidity, wind_speed_kmh, description)
    insight = build_insight(temp, feels_like, humidity, wind_speed_kmh, description)

    return {
        "summary": summary,
        "safety": safety,
        "insight": insight
    }
