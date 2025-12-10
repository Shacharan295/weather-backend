from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from suggestion_engine import generate_ai_weather_guide

# 🔹 NEW fuzzy import
from city_fuzzy import get_city_suggestions

app = Flask(__name__)
CORS(app)

# 🔹 Your API key stays untouched
OPENWEATHER_KEY = "c16d8edd19f7604faf6b861d8daa3337"


@app.route("/")
def home():
    return {
        "status": "Weather API is running",
        "usage": "/weather?city=New York"
    }


# --------------------------------------------------------
#  ✅ IMPROVED /suggest ENDPOINT
# --------------------------------------------------------
@app.route("/suggest")
def suggest_city():
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify([])

    # use new fuzzy logic from city_fuzzy.py
    suggestions = get_city_suggestions(query, limit=5)

    return jsonify({
        "query": query,
        "suggestions": suggestions
    })


# --------------------------------------------------------
#  WEATHER ENDPOINT (your logic preserved)
# --------------------------------------------------------
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

    if not isinstance(current, dict):
        return jsonify({"error": "upstream_api_failure"}), 500

    if current.get("cod") != 200:
        suggestions = get_city_suggestions(city)
        return jsonify({"error": "city_not_found", "suggestions": suggestions}), 404

    description = (current["weather"][0].get("description") or "").title()
    category = current["weather"][0].get("main", "")

    temp = current["main"].get("temp") or 0
    feels_like = current["main"].get("feels_like") or temp
    humidity = current["main"].get("humidity") or 0
    pressure = current["main"].get("pressure") or 0

    wind_speed = current["wind"].get("speed") or 0
    wind_speed_kmh = wind_speed * 3.6

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

    # -------------------------------
    # 3) AIR QUALITY
    # -------------------------------
    aqi_url = (
        f"https://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
    )

    aqi_raw = requests.get(aqi_url).json()

    aqi_index = aqi_raw.get("list", [{}])[0].get("main", {}).get("aqi", None)

    aqi_label_map = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor",
    }

    aqi_label = aqi_label_map.get(aqi_index, "Unknown")

    # -------------------------------
    # 4) AI WEATHER GUIDE
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
        aqi=aqi_index,
    )

    # -------------------------------
    # 5) FINAL RESPONSE
    # -------------------------------
    return jsonify({
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
        "air_quality": {
            "aqi": aqi_index,
            "label": aqi_label
        },
        "forecast": forecast_list,
        "ai_guide": ai_guide
    })


if __name__ == "__main__":
    app.run(debug=True)
