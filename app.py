from flask import Flask, request, jsonify, render_template
import requests
from suggestion_engine import generate_ai_weather_guide
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# OpenWeather API Key
API_KEY = "c16d8edd19f7604faf6b861d8daa3337"


@app.route("/")
def home():
    return {
        "status": "Weather API is running",
        "usage": "/weather?city=New York"
    }


# ----------------------------
# NORMALIZE CONDITIONS
# ----------------------------
def normalize_weather(main, description):
    m = (main or "").lower()
    d = (description or "").lower()

    if m == "clear":
        return "Sunny"

    if m == "clouds":
        if "few" in d or "scattered" in d or "broken" in d:
            return "Partly Cloudy"
        if "overcast" in d:
            return "Cloudy"
        return "Cloudy"

    if m in ["rain", "drizzle"]:
        return "Rainy"

    if m == "thunderstorm":
        return "Stormy"

    if m == "snow":
        return "Snowy"

    if m in ["mist", "fog", "haze", "smoke", "dust"]:
        return "Foggy"

    return "Cloudy"


# ============================================================
# 1️⃣ NEW ENDPOINT FOR NEXT.JS — GET /weather
# ============================================================
@app.route("/weather", methods=["GET"])
def get_weather_new():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": True, "message": "City is required"}), 400

    # --- Fetch Current Weather ---
    current_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    cur = requests.get(current_url, params=params).json()

    if cur.get("cod") != 200:
        return jsonify({
            "error": True,
            "message": cur.get("message", "Invalid city name")
        }), 400

    city_name = cur["name"]
    country = cur["sys"]["country"]
    lat = cur["coord"]["lat"]
    lon = cur["coord"]["lon"]

    temp = cur["main"]["temp"]
    feels_like = cur["main"]["feels_like"]
    humidity = cur["main"]["humidity"]
    pressure = cur["main"]["pressure"]
    wind_speed = cur["wind"]["speed"] * 3.6   # m/s → km/h
    description_raw = cur["weather"][0]["description"]
    description = description_raw.title()
    category = normalize_weather(cur["weather"][0]["main"], description_raw)

    dt = cur.get("dt", 0)
    timezone_offset = cur.get("timezone", 0)

    # --- Fetch Forecast ---
    one_url = "https://api.openweathermap.org/data/2.5/onecall"
    one_params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "exclude": "minutely,alerts"
    }

    fc = requests.get(one_url, params=one_params).json()
    daily = fc.get("daily", [])
    hourly = fc.get("hourly", [])[:12]

    # 3-day forecast
    forecast = []
    for i in range(1, min(4, len(daily))):
        day_item = daily[i]
        day_ts = day_item["dt"] + timezone_offset
        day_name = datetime.utcfromtimestamp(day_ts).strftime("%a")

        w_main = day_item["weather"][0]["main"]
        w_desc = day_item["weather"][0]["description"]

        forecast.append({
            "day": day_name,
            "temp": day_item["temp"]["day"],
            "desc": normalize_weather(w_main, w_desc),
            "emoji": "☀️" if "sun" in w_main.lower() else "☁️"
        })

    # AI guide (your rule-based model)
    ai_guide = generate_ai_weather_guide(
        city=city_name,
        country=country,
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        pressure=pressure,
        wind_speed_kmh=wind_speed,
        category=category,
        description=description,
        hourly=hourly,
        daily=daily[:4],
        timezone_offset=timezone_offset,
    )

    # FINAL RESPONSE — MATCHES YOUR FRONTEND'S WeatherData
    return jsonify({
        "city": city_name,
        "country": country,
        "temp": temp,
        "feels_like": feels_like,
        "description": description,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "wind_mood": category,
        "local_time": datetime.utcfromtimestamp(dt + timezone_offset).strftime("%Y-%m-%d %H:%M"),
        "forecast": forecast,
        "ai_guide": ai_guide
    })


# ============================================================
# 2️⃣ OLD /get_weather POST ENDPOINT (Keep if needed)
# ============================================================
@app.route("/get_weather", methods=["POST"])
def get_weather_old():
    # your existing code remains untouched
    return jsonify({"message": "Still works, but use /weather"})


# ============================================================
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)

