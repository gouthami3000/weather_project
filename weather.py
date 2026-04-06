import streamlit as st
import requests

st.set_page_config(page_title="Weather App")

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Slight rain",
    61: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def get_wmo(code):
    return WMO_CODES.get(code, "Unknown weather condition")

def wind_direction(degree):
    directions = ["N","NE","E","SE","S","SW","W","NW"]
    idx = int((degree / 45) % 8)
    return directions[idx]

def geocode(city):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 5, "language": "en", "format": "json"},
        timeout=8
    )
    r.raise_for_status()
    return r.json().get("results", [])

def fetch_weather(lat, lon):
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,weathercode,uv_index",
            "hourly": "temperature_2m,precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "forecast_days": 7
        },
        timeout=8
    )
    r.raise_for_status()
    return r.json()

# UI
st.title("☀️ Weather App Dashboard")
st.caption("Get the current weather and 7-day forecast for any city in the world.")

city_input = st.text_input("Enter a city name", placeholder="e.g. London, Paris, New York")
unit = st.radio("Select temperature unit", ("Celsius", "Fahrenheit"), horizontal=True)

if not city_input:
    st.info("Please enter a city name to get the weather information.")
    st.stop()

with st.spinner("Fetching location..."):
    try:
        locations = geocode(city_input)
    except Exception as e:
        st.error(f"Error fetching geocoding data: {e}")
        st.stop()

if not locations:
    st.error("No location found. Try another city.")
    st.stop()

options = [f"{loc['name']}, {loc.get('admin1', '')}, {loc.get('country', '')}" for loc in locations]

selected_index = st.selectbox(
    "Select a location",
    range(len(options)),
    format_func=lambda x: options[x]
)

with st.spinner("Fetching weather data..."):
    try:
        weather_data = fetch_weather(
            locations[selected_index]["latitude"],
            locations[selected_index]["longitude"]
        )
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        st.stop()

cur = weather_data["current"]

def fmt(c):
    return f"{c}°C" if unit == "Celsius" else f"{c * 9/5 + 32:.1f}°F"

# Current Weather
st.divider()
desc = get_wmo(cur["weathercode"])

st.subheader("Current Weather")
st.metric("Temperature", fmt(cur["temperature_2m"]), desc)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Feels Like", fmt(cur["apparent_temperature"]))
col2.metric("Wind Speed", f"{cur['wind_speed_10m']} km/h")
col3.metric("Humidity", f"{cur['relative_humidity_2m']}%")
col4.metric("UV Index", f"{cur['uv_index']}")

st.caption(f"Condition: {desc}")