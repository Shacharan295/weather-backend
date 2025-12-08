# suggestion_engine.py
import random

# -----------------------------
# City / Region Climate Profiles
# -----------------------------
CITY_CLIMATE = {
    "mumbai": "coastal-humid",
    "chennai": "coastal-hot",
    "kolkata": "humid-tropical",
    "delhi": "continental-dry",
    "new york": "continental-cold",
    "london": "cold-rainy",
    "tokyo": "temperate-mixed",
    "dubai": "desert-hot",
    "singapore": "tropical-wet",
    "sydney": "coastal-mild",
}

def _climate(city, country):
    city_key = (city or "").lower()
    if city_key in CITY_CLIMATE:
        return CITY_CLIMATE[city_key]

    country = (country or "").upper()
    if country in ["NO", "SE", "FI", "RU", "CA"]:
        return "cold-north"
    if country in ["IN", "TH", "MY", "ID"]:
        return "tropical-asia"
    if country in ["AE", "SA", "EG"]:
        return "desert-hot"
    if country in ["GB", "IE", "DE", "NL"]:
        return "cool-europe"

    return "generic"


# -----------------------------
# Temperature Feel
# -----------------------------
def _temp_feel(temp, feels_like):
    t = feels_like if feels_like is not None else temp
    if t is None:
        return "moderate"

    if t >= 38:
        return "extremely hot"
    if t >= 34:
        return "very hot"
    if t >= 30:
        return "hot"
    if t >= 24:
        return "warm"
    if t >= 18:
        return "mild"
    if t >= 10:
        return "cool"
    if t >= 0:
        return "cold"
    return "freezing"


# -----------------------------
# Helpers for insight
# -----------------------------
def _humidity_label(h):
    if h is None:
        return "moderate"
    if h >= 80:
        return "very humid"
    if h >= 60:
        return "humid"
    if h <= 30:
        return "dry"
    return "normal"


def _wind_label(w):
    if w is None:
        return "calm"
    if w >= 40:
        return "very windy"
    if w >= 20:
        return "breezy"
    return "light wind"


# -----------------------------
# SAFETY TEXT
# -----------------------------
def _build_safety_text(temp, humidity, wind_speed_kmh, category, climate):
    tips = []
    t = temp if temp is not None else 25
    h = humidity or 0
    w = wind_speed_kmh or 0
    cat = (category or "").lower()

    # heat / cold
    if t >= 36:
        tips.append("Avoid staying under direct sunlight for long and drink water often.")
    elif t <= 3:
        tips.append("Wear strong winter layers and limit long outdoor exposure.")

    # humidity
    if h >= 80 and t >= 28:
        tips.append("Heavy humidity can make the day feel tiring, so take short breaks in cool areas.")

    # wind
    if w >= 40:
        tips.append("Strong winds are expected, so be careful near open areas and while riding two-wheelers.")
    elif w >= 25:
        tips.append("It may feel quite breezy, so secure light objects on balconies or terraces.")

    # rain / storm / snow
    if cat in ["rain", "drizzle"]:
        tips.append("Roads and footpaths can be slippery, so walk carefully and keep an umbrella or raincoat handy.")
    if cat in ["thunderstorm", "storm"]:
        tips.append("Avoid open spaces and do not stand under isolated trees during lightning or thunder.")
    if cat in ["snow", "snowy"]:
        tips.append("Snow and ice can make surfaces risky, so move slowly and plan extra time for travel.")

    # climate specific
    if climate == "desert-hot" and t >= 32:
        tips.append("The dry desert-style heat can dehydrate you quickly, so carry enough water if you go out.")
    if climate.startswith("coastal") and cat in ["rain", "drizzle", "thunderstorm"]:
        tips.append("Coastal showers can start suddenly, so check the sky and forecast before longer trips.")

    if not tips:
        return "No major weather-related safety issues are expected for most people today."

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
        f"In {city}, {country}, the day feels {feel_word} with mainly {cat} conditions.",
        f"{city}, {country} is experiencing a {feel_word} day with {cat} skies.",
        f"Overall, {city} has a {feel_word} feel today with {cat} dominating the sky.",
    ]

    temp_part = f" Around {temp:.1f}°C, it feels close to {feels_like:.1f}°C."
    humidity_part = f" The air is {hum_label} with about {humidity}% humidity."
    wind_part = f" Winds stay {wind_label} near {wind_speed_kmh:.1f} km/h."

    climate_extra = ""
    if climate in ["coastal-humid", "tropical-wet", "humid-tropical"]:
        climate_extra = " Being a more humid region, the warmth can feel stronger than the number suggests."
    elif climate in ["desert-hot"]:
        climate_extra = " The dry style of heat makes shade and hydration very important."
    elif climate in ["cold-north", "continental-cold"]:
        climate_extra = " Cooler air is common here, so the temperature can drop further after sunset."
    elif climate in ["cold-rainy", "cool-europe"]:
        climate_extra = " Cloud cover and light rain can keep the day feeling cooler and softer."

    base_line = random.choice(base_templates)
    return base_line + temp_part + humidity_part + wind_part + climate_extra


# -----------------------------
# INSIGHT TEXT (CLIMATE INSIGHT)
# -----------------------------
def _build_insight_text(city, country, temp, feels_like, humidity, pressure, wind_speed_kmh, category, climate):
    pieces = []
    t = temp if temp is not None else 25
    fl = feels_like if feels_like is not None else t
    diff = fl - t
    h = humidity or 0
    w = wind_speed_kmh or 0
    p = pressure or 1013
    cat = (category or "").lower()

    # feels-like vs actual
    if diff >= 2:
        pieces.append("It feels warmer than the actual temperature, mainly due to humidity and local conditions.")
    elif diff <= -2:
        pieces.append("It actually feels cooler than the measured temperature, likely helped by wind or lower humidity.")
    else:
        pieces.append("The feels-like temperature is close to the actual reading, so the day should match expectations.")

    # humidity note
    if h >= 80:
        pieces.append("High humidity can trap heat near the body, which is why the weather may feel heavy or sticky.")
    elif h <= 30:
        pieces.append("Low humidity keeps the air dry, which can feel sharper on the skin and lips.")

    # pressure insight
    if p >= 1020:
        pieces.append("Pressure is on the higher side, often linked with more stable and calmer conditions.")
    elif p <= 1005:
        pieces.append("Pressure is slightly lower, which sometimes hints at more clouds, rain, or changing conditions.")

    # wind and category
    if w >= 35:
        pieces.append("Stronger winds can make temperatures feel lower, especially in open areas.")
    if cat in ["rain", "drizzle"]:
        pieces.append("Passing showers can cool the surface a bit, especially later in the day.")
    if cat in ["clear", "sunny"]:
        pieces.append("Clear skies allow more direct sunlight, so mid-day can feel noticeably stronger than morning or evening.")

    # climate-style context
    climate_note = ""
    if climate == "coastal-humid":
        climate_note = f"{city} often mixes sea breeze with humidity, so even moderate temperatures can feel heavier."
    elif climate == "desert-hot":
        climate_note = f"{city} tends to have sharp daytime heat and faster cooling at night, which is typical for desert-style climates."
    elif climate in ["tropical-wet", "humid-tropical", "tropical-asia"]:
        climate_note = f"{city} sits in a more tropical pattern, so quick shifts between sun and clouds are normal."
    elif climate in ["cold-north", "continental-cold"]:
        climate_note = f"{city} is used to colder swings, so temperatures can drop quickly after sunset or during clear nights."
    else:
        climate_note = f"Overall, today fits within a normal pattern for {city} and its usual climate."

    pieces.append(climate_note)

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
    """
    Returns EXACTLY:
        {
          "summary": "...",  # Cast Today
          "safety": "...",   # Safety Today
          "insight": "..."   # Climate Insight
        }
    """

    climate = _climate(city, country)

    summary_text = _build_summary_text(
        city=city,
        country=country,
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        wind_speed_kmh=wind_speed_kmh,
        category=category,
        description=description,
        climate=climate,
    )

    safety_text = _build_safety_text(
        temp=temp,
        humidity=humidity,
        wind_speed_kmh=wind_speed_kmh,
        category=category,
        climate=climate,
    )

    insight_text = _build_insight_text(
        city=city,
        country=country,
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        pressure=pressure,
        wind_speed_kmh=wind_speed_kmh,
        category=category,
        climate=climate,
    )

    return {
        "summary": summary_text,
        "safety": safety_text,
        "insight": insight_text,
    }
