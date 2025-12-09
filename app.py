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

    # ❗ FIX: Ensure JSON structure is valid
    if not isinstance(current, dict):
        return jsonify({"error": "upstream_api_failure"}), 500

    # ❗ FIX: On invalid city → send fuzzy suggestions
    if current.get("cod") != 200:
        suggestions = get_city_suggestions(city)
        return jsonify({"error": "city_not_found", "suggestions": suggestions}), 404

    # ❗ FIX: Safe description + category
    description = (current["weather"][0].get("description") or "").title()
    category = current["weather"][0].get("main", "")

    # ❗ FIX: Safe numeric values
    temp = current["main"].get("temp") or 0
    feels_like = current["main"].get("feels_like") or temp
    humidity = current["main"].get("humidity") or 0
    pressure = current["main"].get("pressure") or 0

    wind_speed = current["wind"].get("speed") or 0
    wind_speed_kmh = wind_speed * 3.6

    # ❗ FIX: Safe timezone offset
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

    # ❗ FIX: Ensure forecast_raw list exists
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

            # ❗ FIX: Safe forecast description + temp
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

    # ❗ FIX: Ensure forecast list is always returned
    if not forecast_list:
        forecast_list = []

    # -------------------------------
    # 3) AI SUGGESTION ENGINE
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
    )

    # -------------------------------
    # 4) FINAL RESPONSE
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
        "forecast": forecast_list,
        "ai_guide": ai_guide
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
