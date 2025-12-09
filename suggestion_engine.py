import random

# ----------------------------------------
# City / Region Climate Profiles
# ----------------------------------------
CITY_CLIMATE = {
    "mumbai": "coastal humid",
    "chennai": "coastal hot",
    "kolkata": "humid tropical",
    "delhi": "continental dry",
    "new york": "continental cold",
    "london": "cold rainy",
    "tokyo": "temperate mixed",
    "dubai": "desert hot",
    "singapore": "tropical wet",
    "sydney": "coastal mild",
}


def _climate(city, country):
    city_key = (city or "").lower()
    if city_key in CITY_CLIMATE:
        return CITY_CLIMATE[city_key]

    country = (country or "").upper()

    if country in ["NO", "SE", "FI", "RU", "CA"]:
        return "cold northern"
    if country in ["IN", "TH", "MY", "ID"]:
        return "tropical asian"
    if country in ["AE", "SA", "EG"]:
        return "desert hot"
    if country in ["GB", "IE", "DE", "NL"]:
        return "cool european"

    return "generic climate"


# ----------------------------------------
# Temperature Feel
# ----------------------------------------
def _temp_feel(temp, feels_like):
    t = feels_like if feels_like is not None else temp
    if t is None:
        return "moderate"

    if t >= 38: return "extremely hot"
    if t >= 34: return "very hot"
    if t >= 30: return "hot"
    if t >= 24: return "warm"
    if t >= 18: return "mild"
    if t >= 10: return "cool"
    if t >= 0:  return "cold"
    return "freezing"


# ----------------------------------------
# Labels (Humidity / Wind)
# ----------------------------------------
def _humidity_label(h):
    if h is None: return "moderate"
    if h >= 80: return "very humid"
    if h >= 60: return "humid"
    if h <= 30: return "dry"
    return "normal"


def _wind_label(w):
    if w is None: return "calm"
    if w >= 40: return "very windy"
    if w >= 20: return "breezy"
    return "light wind"


# ----------------------------------------
# SAFETY CONCERN (Includes AQI Now)
# ----------------------------------------
def _build_safety_text(temp, humidity, wind_speed_kmh, category, climate, aqi):
    tips = []
    t = temp or 25
    h = humidity or 0
    w = wind_speed_kmh or 0
    cat = (category or "").lower()

    # Temperature Risks
    if t >= 36:
        tips.append("Avoid long exposure to direct sunlight and keep yourself hydrated throughout the day.")
    elif t <= 3:
        tips.append("Wear strong winter layers and reduce outdoor exposure, especially when the wind picks up.")

    # Humidity Risks
    if h >= 80 and t >= 28:
        tips.append("High humidity can add extra strain, so take short breaks in cooler or shaded spots.")

    # Wind Risks
    if w >= 40:
        tips.append("Strong winds may reduce visibility and balance, so stay cautious in open areas.")
    elif w >= 25:
        tips.append("Breezy conditions may disturb lighter objects outdoors, so secure anything on balconies or terraces.")

    # Rain / Storm / Snow
    if cat in ["rain", "drizzle"]:
        tips.append("Roads and paths can be slippery, so walk slowly and keep rain protection handy.")
    if cat in ["thunderstorm", "storm"]:
        tips.append("Stay indoors during lightning and avoid open grounds or isolated tall trees.")
    if cat in ["snow", "snowy"]:
        tips.append("Snow or ice can reduce grip, so move carefully and allow extra time for travel.")

    # Climate-specific notes
    if climate == "desert hot" and t >= 32:
        tips.append("Dry desert heat can cause dehydration quickly, so carry water if you step outside.")
    if climate.startswith("coastal") and cat in ["rain", "drizzle", "thunderstorm"]:
        tips.append("Coastal showers can begin suddenly, so plan longer activities with caution.")

    # ----------------------------------------
    # ⭐ NEW — AIR QUALITY RISKS
    # ----------------------------------------
    if aqi is not None:
        if aqi == 5:
            tips.append("Air quality is very poor — avoid outdoor activity and consider using a mask if you step outside.")
        elif aqi == 4:
            tips.append("Air quality is poor today, so limit heavy outdoor activity and keep windows closed if possible.")
        elif aqi == 3:
            tips.append("Air quality is moderate — sensitive groups may feel slight irritation or discomfort.")

    if not tips:
        return "No major weather-related concerns today, but staying aware of changing conditions is always helpful."

    return " ".join(tips)


# ----------------------------------------
# Summary Text
# ----------------------------------------
def _build_summary_text(city, country, temp, feels_like, humidity, wind_speed_kmh, category, description, climate):

    feel_word = _temp_feel(temp, feels_like)
    hum_label = _humidity_label(humidity)
    wind_label = _wind_label(wind_speed_kmh)
    cat = (category or description or "the weather").lower()

    base_templates = [
        f"In {city}, {country}, the day feels {feel_word} with mostly {cat} conditions.",
        f"{city}, {country} is experiencing a {feel_word} day with {cat} skies.",
        f"Overall, {city} has a {feel_word} feel today with {cat} being the main pattern.",
    ]

    temp_part = f" Around {temp:.1f}°C, it feels close to {feels_like:.1f}°C."
    humidity_part = f" The air is {hum_label}, with about {humidity}% humidity."
    wind_part = f" Winds stay {wind_label}, around {wind_speed_kmh:.1f} km/h."

    climate_extra_map = {
        "coastal humid": " Coastal humidity can make the warmth feel slightly stronger.",
        "tropical wet": " Tropical moisture can add a bit of heaviness to the day.",
        "humid tropical": " The humid air enhances the warmth through the afternoon.",
        "desert hot": " Dry desert warmth often feels sharper during the daytime.",
        "continental cold": " Daytime cold in continental regions can feel crisp and sharp.",
        "cold northern": " Northern daytime temperatures often stay on the cooler side.",
        "cold rainy": " Cloudy or rainy conditions can make the day feel softer and cooler.",
        "cool european": " Cloud cover in such regions usually reduces daytime heating.",
    }

    climate_extra = climate_extra_map.get(climate, "")

    return random.choice(base_templates) + temp_part + humidity_part + wind_part + climate_extra


# ----------------------------------------
# Climate Insight (Max 3 lines)
# ----------------------------------------
def _build_insight_text(city, country, temp, feels_like, humidity, pressure, wind_speed_kmh, category, climate):

    pieces = []
    t = temp or 25
    fl = feels_like or t
    diff = fl - t
    h = humidity or 0
    w = wind_speed_kmh or 0
    p = pressure or 1013
    cat = (category or "").lower()

    # Feels-like
    if diff >= 2:
        pieces.append("It feels a little warmer than the actual temperature, mostly due to local humidity.")
    elif diff <= -2:
        pieces.append("It feels slightly cooler than the reading, helped by wind or lower moisture.")
    else:
        pieces.append("The feels like temperature is almost identical to the actual reading today.")

    # Humidity
    if h >= 80:
        pieces.append("High humidity can make the air feel heavier than usual.")
    elif h <= 30:
        pieces.append("Dry air adds a sharper feel to the temperature.")

    # Pressure
    if p >= 1020:
        pieces.append("Higher pressure usually brings calm and settled weather.")
    elif p <= 1005:
        pieces.append("Lower pressure hints at changing skies or possible light rain.")

    # Wind & Condition Behavior
    if w >= 35:
        pieces.append("Strong winds can lower how the temperature feels, especially in open spaces.")
    if cat in ["rain", "drizzle"]:
        pieces.append("Passing showers may cool the surroundings briefly.")
    if cat in ["clear", "sunny"]:
        pieces.append("Clear skies allow mid-day sunlight to feel stronger.")

    # Climate Insight
    climate_map = {
        "coastal humid": f"{city} often feels heavier in the evenings due to coastal moisture.",
        "desert hot": f"{city} cools down quickly at night despite warm daytime heat.",
        "tropical wet": f"{city} commonly sees quick shifts between sunshine and cloud cover.",
        "humid tropical": f"{city} often alternates between warm and humid spells throughout the day.",
        "tropical asian": f"{city} frequently experiences fast-changing weather patterns.",
        "continental cold": f"{city} cools noticeably after sunset, especially on clearer evenings.",
        "cold northern": f"{city} often develops colder gusts during the night hours.",
        "cold rainy": f"{city} tends to soften in the evening as moisture builds through the day.",
        "cool european": f"{city} loses daytime warmth steadily due to regular cloud cover.",
    }

    pieces.append(climate_map.get(climate, f"Conditions today follow a usual pattern for {city}."))

    text = ". ".join(" ".join(pieces).split(". ")[:3]) + "."
    return text


# ----------------------------------------
# Main Public Function
# ----------------------------------------
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
    aqi=None,   # ⭐ NEW
):
    climate = _climate(city, country)

    return {
        "summary": _build_summary_text(city, country, temp, feels_like, humidity, wind_speed_kmh, category, description, climate),
        "safety": _build_safety_text(temp, humidity, wind_speed_kmh, category, climate, aqi),  # ⭐ UPDATED
        "insight": _build_insight_text(city, country, temp, feels_like, humidity, pressure, wind_speed_kmh, category, climate),
    }
