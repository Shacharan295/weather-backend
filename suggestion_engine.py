# suggestion_engine.py
import random

# -----------------------------
# City / Region Climate Profiles (NO HYPHENS)
# -----------------------------
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


# -----------------------------
# Temperature Feel
# -----------------------------
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


# -----------------------------
# Helpers
# -----------------------------
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


# -----------------------------
# SAFETY TEXT
def _build_safety_text(temp, humidity, wind_speed_kmh, category, climate):
    tips = []
    t = temp or 25
    h = humidity or 0
    w = wind_speed_kmh or 0
    cat = (category or "").lower()

    # Temperature safety
    if t >= 36:
        tips.append("Avoid direct sunlight for long periods, stay hydrated, and take breaks in shaded areas.")
    elif t <= 3:
        tips.append("Wear strong winter layers and limit outdoor exposure, especially during windy hours.")

    # Humidity safety
    if h >= 80 and t >= 28:
        tips.append("High humidity can increase fatigue, so rest often and avoid strenuous outdoor activity.")

    # Wind safety
    if w >= 40:
        tips.append("Strong winds may cause reduced visibility and balance issues, so be extra careful in open areas.")
    elif w >= 25:
        tips.append("Breezy conditions can disturb light objects, so secure anything placed outdoors.")

    # Rain / Storm / Snow
    if cat in ["rain", "drizzle"]:
        tips.append("Roads and footpaths may be slippery, so walk slowly and keep rain protection handy.")
    if cat in ["thunderstorm", "storm"]:
        tips.append("Stay indoors during lightning, avoid open grounds, and keep away from tall isolated trees.")
    if cat in ["snow", "snowy"]:
        tips.append("Snow and ice can make travel unsafe, so move carefully and allow extra time for your trips.")

    # Climate-specific
    if climate == "desert hot" and t >= 32:
        tips.append("Dry desert heat can dehydrate quickly, so carry sufficient water if you step out.")
    if climate.startswith("coastal") and cat in ["rain", "drizzle", "thunderstorm"]:
        tips.append("Coastal rains may start suddenly, so plan outdoor activities with caution.")

    if not tips:
        return "No major weather related safety concerns are expected today, but staying aware of local conditions is always helpful."

    return " ".join(tips)



# -----------------------------
# SUMMARY TEXT (CAST TODAY)
# -----------------------------
def _build_summary_text(city, country, temp, feels_like, humidity, wind_speed_kmh, category, description, climate):
    feel_word = _temp_feel(temp, feels_like)
    hum_label = _humidity_label(humidity)
    wind_label = _wind_label(wind_speed_kmh)
    cat = (category or description or "the weather").lower()

    base_templates = [
        f"In {city}, {country}, the day feels {feel_word} with mostly {cat} conditions.",
        f"{city}, {country} is seeing a {feel_word} kind of day with {cat} skies.",
        f"Overall, {city} has a {feel_word} feel today with {cat} being the main pattern.",
    ]

    temp_part = f" Around {temp:.1f}°C, it feels close to {feels_like:.1f}°C."
    humidity_part = f" The air is {hum_label}, with about {humidity}% humidity."
    wind_part = f" Winds stay {wind_label}, around {wind_speed_kmh:.1f} km/h."

    # Climate-friendly extra wording
 climate_extra_map = {
    "coastal humid": " Coastal humidity can make the warmth feel stronger than usual.",
    "tropical wet": " Moist tropical air can add heaviness to the day.",
    "humid tropical": " The humidity in this region often enhances the warmth.",
    "desert hot": " Dry desert heat increases the need for shade and regular hydration.",
    "continental cold": " Cold continental areas often feel sharper during the day.",
    "cold northern": " Northern air patterns tend to keep daytime temperatures on the cooler side.",
    "cold rainy": " Cloudy or rainy conditions can soften the daytime temperature.",
    "cool european": " Cloud-covered European climates often reduce daytime warmth slightly.",
}

    climate_extra = climate_extra_map.get(climate, "")

    return random.choice(base_templates) + temp_part + humidity_part + wind_part + climate_extra


# -----------------------------
# INSIGHT TEXT (CLIMATE INSIGHT)
# -----------------------------
def _build_insight_text(city, country, temp, feels_like, humidity, pressure, wind_speed_kmh, category, climate):
    pieces = []
    t = temp or 25
    fl = feels_like or t
    diff = fl - t
    h = humidity or 0
    w = wind_speed_kmh or 0
    p = pressure or 1013
    cat = (category or "").lower()

    # Feels-like difference
    if diff >= 2:
        pieces.append("It feels warmer than the actual temperature, mostly due to humidity and surrounding conditions.")
    elif diff <= -2:
        pieces.append("It feels cooler than the reading, likely helped by wind or lower humidity.")
    else:
        pieces.append("The feels like temperature is almost the same as the real one, so conditions should feel predictable.")

    # Humidity
    if h >= 80:
        pieces.append("High humidity can trap heat around the body, making the day feel heavier.")
    elif h <= 30:
        pieces.append("Low humidity keeps the air dry, which can feel sharp on the skin.")

    # Pressure notes
    if p >= 1020:
        pieces.append("Higher pressure usually brings calmer and more settled weather.")
    elif p <= 1005:
        pieces.append("Lower pressure can hint at clouds, changes, or possible rain later.")

    # Wind + sky
    if w >= 35:
        pieces.append("Strong winds can make temperatures feel lower, especially in open spaces.")
    if cat in ["rain", "drizzle"]:
        pieces.append("Passing showers may cool the surface slightly.")
    if cat in ["clear", "sunny"]:
        pieces.append("Clear skies allow stronger sunlight, especially around mid-day.")

    # Climate natural-language notes
    climate_map = {
        "coastal humid": f"{city} often mixes sea breeze with moisture, making even mild days feel heavier.",
        "desert hot": f"{city} usually has sharp daytime heat and quick cooling at night, a common desert pattern.",
        "tropical wet": f"{city} often sees quick shifts between sun and clouds due to tropical moisture.",
        "humid tropical": f"{city} is influenced by warm humid air, making warmth feel stronger.",
        "tropical asian": f"{city} fits a tropical pattern where weather shifts happen quickly.",
        "continental cold": f"{city} experiences sharp cold swings, especially after sunset or during clear nights.",
        "cold northern": f"{city} belongs to colder northern zones where temperatures drop quickly at night.",
        "cold rainy": f"{city}'s cool and rainy style often keeps temperatures on the softer side.",
        "cool european": f"{city} usually sees cloudier skies that reduce daytime heating.",
    }

    pieces.append(climate_map.get(climate, f"Today behaves normally for {city}'s usual climate."))

    return " ".join(pieces)


# -----------------------------
# MAIN PUBLIC FUNCTION
# -----------------------------
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
    climate = _climate(city, country)

    summary_text = _build_summary_text(
        city, country, temp, feels_like, humidity, wind_speed_kmh,
        category, description, climate
    )

    safety_text = _build_safety_text(
        temp, humidity, wind_speed_kmh, category, climate
    )

    insight_text = _build_insight_text(
        city, country, temp, feels_like, humidity, pressure,
        wind_speed_kmh, category, climate
    )

    return {
        "summary": summary_text,
        "safety": safety_text,
        "insight": insight_text,
    }


