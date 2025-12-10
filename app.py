from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from suggestion_engine import generate_ai_weather_guide
from city_fuzzy import get_city_suggestions

app = Flask(__name__)
CORS(app)

OPENWEATHER_KEY = "c16d8edd19f7604faf6b861d8daa3337"


@app.route("/")
def home():
    return {"status": "Weather API running"}


# -------------------------------
# CITY SUGGESTIONS
# -------------------------------
@app.route("/suggest")
def suggest_city():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"query": "", "suggestions": []})

    suggestions = get_city_suggestions(query, limit=5)
    return jsonify({"query": query, "suggestions": suggestions})


# -------------------------------
# WEATHER ENDPOINT
# -------------------------------
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

    if current.get("cod") != 200:
        return jsonify({
            "error": "city_not_found",
            "suggestions": get_city_suggestions(city)
        })

    description = current["weather"][0]["description"].title()
    category = current["weather"][0]["main"]

    temp = current["main"]["temp"]
    feels_like = current["main"]["feels_like"]
    humidity = current["main"]["humidity"]
    pressure = current["main"]["pressure"]

    wind_speed = current["wind"]["speed"] * 3.6  # convert m/s → km/h
    timezone_offset = current["timezone"]

    local_time = datetime.utcfromtimestamp(
        current["dt"] + timezone_offset
    ).strftime("%Y-%m-%d %H:%M")

    lat = current["coord"]["lat"]
    lon = current["coord"]["lon"]

    # -------------------------------
    # 2) FORECAST FETCH
    # -------------------------------
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
    )
    forecast_raw = requests.get(forecast_url).json()

    # -------------------------------
    # ⭐ PERFECT 24-HOUR HOURLY DATA
    # -------------------------------
    hourly_temps = []

    # First point = current temperature
    now_time = datetime.utcfromtimestamp(
        current["dt"] + timezone_offset
    ).strftime("%H:00")

    hourly_temps.append({
        "time": now_time,
        "temp": temp
    })

    # Add next 7 forecast hours (3-hour intervals)
    count = 1
    for entry in forecast_raw.get("list", []):
        if count > 7:
            break

        dt = entry.get("dt_txt", "")
        hour_label = dt.split(" ")[1][:5]
        temp_val = entry["main"]["temp"]

        hourly_temps.append({
            "time": hour_label,
            "temp": temp_val
        })

        count += 1

    # -------------------------------
    # 3) 3-DAY FORECAST
    # -------------------------------
    forecast_list = []
    days_seen = set()

    for entry in forecast_raw.get("list", []):
        dt = entry["dt_txt"]
        date, time = dt.split(" ")

        if time == "12:00:00" and date not in days_seen:
            forecast_list.append({
                "day": date,
                "temp": entry["main"]["temp"],
                "description": entry["weather"][0]["description"].title()
            })
            days_seen.add(date)

        if len(forecast_list) >= 3:
            break

    # -------------------------------
    # 4) AIR QUALITY
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
        5: "Very Poor"
    }
    aqi_label = aqi_label_map.get(aqi_index, "Unknown")

    # -------------------------------
    # 5) AI WEATHER GUIDE
    # -------------------------------
    ai_guide = generate_ai_weather_guide(
        city=current["name"],
        country=current["sys"]["country"],
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        pressure=pressure,
        wind_speed_kmh=wind_speed,
        category=category,
        description=description,
        hourly=hourly_temps,
        daily=forecast_list,
        timezone_offset=timezone_offset,
        aqi=aqi_index,
    )

    # -------------------------------
    # FINAL RESPONSE
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
        "wind_speed": round(wind_speed, 1),
        "wind_mood": "Windy" if wind_speed > 20 else "Calm",
        "air_quality": {"aqi": aqi_index, "label": aqi_label},
        "forecast": forecast_list,
        "hourly": hourly_temps,
        "ai_guide": ai_guide
    })


if __name__ == "__main__":
    app.run(debug=True)
