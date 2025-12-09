from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from suggestion_engine import generate_ai_weather_guide
from city_fuzzy import get_city_suggestions   # ✅ NEW IMPORT

app = Flask(__name__)
CORS(app)

OPENWEATHER_KEY = "c16d8edd19f7604faf6b861d8daa3337"


@app.route("/")
def home():
    return {
        "status": "Weather API is running",
        "usage": "/weather?city=New York"
    }


# ✅ LIVE CITY SUGGESTIONS ENDPOINT
@app.route("/suggest")
def suggest_city():
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify([])

    suggestions = get_city_suggestions(query, limit=7)
    return jsonify(suggestions)


@app.route("/weather")
def get_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "City is required"}), 400

    # -------------------------------
    # 1) CURRENT WEATHER
    # -------------------------------
    current_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={OPENWEATHER_KEY}&units=metric"
    )

    current = requests.get(current_url).json()

    # ❗ Ensure JSON structure is valid
    if not isinstance(current, dict):
        return jsonify({"error": "upstream_api_failure"}), 500

    # ❗ On invalid city → send fuzzy suggestions
    if current.get("cod") != 200:
        suggestions = get_city_suggestions(city)
        return jsonify({"error": "city_not_found", "suggestions": suggestions}), 404

    # ❗ Safe description + category
    description = (current["weather"][0].get("description") or "").title()
    category = current["weather"][0].get("main", "")

    # ❗ Safe numeric values
    temp = current["main"].get("temp") or 0
    feels_like = current["main"].get("feels_like") or temp
    humidity = current["main"].get("humidity") or 0
    pressure = current["main"].get("pressure") or 0

    wind_speed = current["wind"].get("speed") or 0
    wind_speed_kmh = wind_speed * 3.6

    # ❗ Safe timezone offset
    timezone_offset = current.get("timezone", 0)

    local_time = datetime.utcfromtimestamp(
        current["dt"] + timezone_offset
    ).strftime("%Y-%m-%d %H:%M")

    lat = current["coord"]["lat"]
    lon = current["coord"]["lon"]

    # -------------------------------
    # 2) FORECAST (3 DAYS)
    # -------------------------------
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
    )

    forecast_raw = requests.get(forecast_url).json()

    # ❗ Ensure forecast_raw list exists
    if "list" not in forecast_raw:
        forecast_raw["list"] = []

    forecast_list = []
    days_seen = set()

    for entry in forecast_raw["list"]:
        dt = entry.get("dt_txt", "")

        if " " not in dt:
            continue

        date, time = dt.split(" ")

        if time == "12:00:00" and date not in days_seen:

            # ❗ Safe forecast description + temp
            f_desc = (entry["weather"][0].get("description") or "").title()
            f_temp = entry["main"].get("temp") or 0

            forecast_list.append({
                "day": date,
                "temp": f_temp,
                "description": f_desc
            })

            days_seen.add(date)

        if len(forecast_list) >= 3:
            break

    # ❗ Ensure forecast list is always returned
    if not forecast_list:
        forecast_list = []

    # -------------------------------
    # 3) AIR QUALITY (OpenWeather Air Pollution API)
    # -------------------------------
    aqi_value = None          # scaled (0–300 style)
    aqi_index = None          # raw 1–5 from OpenWeather
    aqi_label = None

    try:
        aqi_url = (
            f"https://api.openweathermap.org/data/2.5/air_pollution?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
        )
        aqi_raw = requests.get(aqi_url).json()
        if isinstance(aqi_raw, dict) and aqi_raw.get("list"):
            aqi_index = aqi_raw["list"][0]["main"].get("aqi")  # 1–5

            # Map 1–5 → approx AQI scale
            scale_map = {1: 50, 2: 100, 3: 150, 4: 200, 5: 300}
            aqi_value = scale_map.get(aqi_index)

            if aqi_value is not None:
                if aqi_value <= 50:
                    aqi_label = "Good"
                elif aqi_value <= 100:
                    aqi_label = "Moderate"
                elif aqi_value <= 150:
                    aqi_label = "Unhealthy for sensitive groups"
                elif aqi_value <= 200:
                    aqi_label = "Unhealthy"
                else:
                    aqi_label = "Very unhealthy"
    except Exception:
        aqi_value = None
        aqi_index = None
        aqi_label = None

    # -------------------------------
    # 4) AI SUGGESTION ENGINE
    # -------------------------------
    ai_guide = generate_ai_weather_guide(
        city=current["name"],
        country=current["sys"]["country"],
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        pressure=pressure,
        wind_speed_kmh=wind_speed_kmh,
        category=category,
        description=description,
        hourly=[],
        daily=[],
        timezone_offset=timezone_offset,
        aqi=aqi_value,   # ✅ NEW
    )

    # -------------------------------
    # 5) FINAL RESPONSE
    # -------------------------------
    result = {
        "city": current["name"],
        "country": current["sys"]["country"],
        "local_time": local_time,
        "temp": temp,
        "feels_like": feels_like,
        "description": description,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": round(wind_speed_kmh, 2),
        "wind_mood": "Windy" if wind_speed_kmh > 20 else "Calm",
        "air_quality": {            # ✅ Live AQI block
            "aqi": aqi_value,
            "index": aqi_index,
            "label": aqi_label,
            "source": "OpenWeather Air Pollution API"
        },
        "forecast": forecast_list,
        "ai_guide": ai_guide
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
