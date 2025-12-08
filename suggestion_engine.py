# suggestion_engine.py

def _temp_feel(temp, feels_like):
    t = feels_like if feels_like is not None else temp
    if t is None:
        return "moderate"

    if t >= 35:
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


def _clothing_advice(temp, category, wind_speed, humidity):
    t = temp if temp is not None else 25
    cat = (category or "").lower()

    if t >= 35:
        return (
            "Wear very light, breathable clothing. Avoid dark colours and stay in the shade when possible."
        )
    if t >= 28:
        return "Light cotton clothes and sunglasses are a good choice. A cap or hat can help in the afternoon."
    if t >= 22:
        if cat in ["rainy", "stormy"]:
            return "Light clothing with a thin waterproof layer or umbrella will work well."
        return "A T-shirt and jeans or similar light outfit should feel comfortable for most of the day."
    if t >= 15:
        return "A light jacket or hoodie over regular clothes should be enough, especially for the evening."
    if t >= 5:
        return "Wear warm layers, including a sweater or light coat, to stay comfortable outdoors."
    return "Use a proper winter jacket, warm layers and closed shoes to protect yourself from the cold."


def _activity_advice(category, temp, wind_speed, humidity):
    cat = (category or "").lower()
    w = wind_speed or 0
    h = humidity or 0
    t = temp if temp is not None else 25

    if cat == "stormy":
        return "It is better to stay indoors or choose indoor activities while storms are active."
    if cat == "rainy":
        return "Short outdoor trips are fine with an umbrella. Indoor plans may feel more comfortable today."
    if cat == "snowy":
        return "You can enjoy short walks in the snow if paths are safe. Plan extra time for travel."
    if t >= 35:
        return "Avoid long activities under direct sun. Prefer shaded areas or shorter walks during cooler hours."
    if w >= 35:
        return "Outdoor plans are still possible, but strong wind can be tiring. Choose sheltered places if you can."
    if h >= 80 and t >= 28:
        return "High humidity can make it feel heavier. Light activity and frequent water breaks are best."

    return "Weather is suitable for normal outdoor plans such as walking, shopping or meeting friends."


def _safety_advice(temp, humidity, wind_speed, category):
    tips = []
    t = temp if temp is not None else 25
    h = humidity or 0
    w = wind_speed or 0
    cat = (category or "").lower()

    if t >= 35:
        tips.append("Drink water regularly and avoid staying under direct sunlight for long periods.")
    if t <= 5:
        tips.append("Wear enough warm layers to avoid getting too cold, especially at night.")
    if h >= 80:
        tips.append("High humidity can make the air feel heavy. Take breaks in cooler or ventilated spaces.")
    if w >= 40:
        tips.append("Strong winds are expected. Secure light objects and be careful near open areas.")
    if cat in ["rainy", "stormy"]:
        tips.append("Roads and paths may be slippery. Walk carefully and allow extra time for travel.")

    if not tips:
        return "No major weather-related safety concerns are expected for most people today."

    return " ".join(tips)


def _time_block_text(name, base_feel, category, part):
    """
    name: "morning"/"afternoon"/"evening"
    base_feel: very hot / hot / warm / mild / cool / cold / freezing
    category: Sunny / Cloudy / Rainy / etc.
    part: which block this is (for slight variation)
    """
    cat = (category or "").lower()
    f = base_feel

    # Simple patterns to keep text natural but varied.
    if name == "morning":
        if f in ["very hot", "hot"]:
            return "Morning starts warm and bright, but still more comfortable than the mid-day hours."
        if f in ["warm", "mild"]:
            return "Morning feels gentle and easy to step outside, with a calm start to the day."
        if f in ["cool", "cold", "freezing"]:
            return "Morning begins on the cooler side, so an extra layer can make early trips more pleasant."
    if name == "afternoon":
        if f in ["very hot", "hot"]:
            return "Afternoon is the warmest part of the day, so shade and lighter activity are ideal."
        if f in ["warm", "mild"]:
            return "Afternoon stays comfortable for most outdoor plans, with steady temperatures."
        if f in ["cool", "cold", "freezing"]:
            return "Afternoon remains on the cooler side, but a bit milder than the early morning."
    if name == "evening":
        if f in ["very hot", "hot"]:
            return "Evening slowly cools down, making it a better time for a relaxed walk outside."
        if f in ["warm", "mild"]:
            return "Evening feels pleasant and slightly cooler, good for short outings or fresh air."
        if f in ["cool", "cold", "freezing"]:
            return "Evening can feel quite chilly, so a jacket or warm layer is helpful if you go out."

    # Fallback, if something unexpected:
    return f"The {name} period follows similar conditions to the rest of the day, with no major changes expected."


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
    Main FREE 'AI' guide.
    Uses only rules, no paid API calls.
    Returns a dict with these keys:
        summary, morning, afternoon, evening, clothing, activities, safety
    """
    feel_word = _temp_feel(temp, feels_like)
    cat = category or description or "the current weather"

    # Summary
    summary = (
        f"Weather in {city}, {country} feels {feel_word} with mainly {cat.lower()} conditions. "
        f"The temperature is around {temp:.1f}°C, feeling like {feels_like:.1f}°C, "
        f"with about {humidity}% humidity and wind near {wind_speed_kmh:.1f} km/h."
    )

    # Time blocks
    morning_text = _time_block_text("morning", feel_word, category, "morning")
    afternoon_text = _time_block_text("afternoon", feel_word, category, "afternoon")
    evening_text = _time_block_text("evening", feel_word, category, "evening")

    # Clothing / activities / safety
    clothing_text = _clothing_advice(temp, category, wind_speed_kmh, humidity)
    activity_text = _activity_advice(category, temp, wind_speed_kmh, humidity)
    safety_text = _safety_advice(temp, humidity, wind_speed_kmh, category)

    return {
        "summary": summary,
        "activities": activity_text,
        "safety": safety_text,
    }

