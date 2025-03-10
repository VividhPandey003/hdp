import requests

def fetch_weather_data(latitude="41.85003", longitude="-87.65005",start_date="2025-03-10",end_date="2025-03-10"):
    """Fetch current weather data using Open-Meteo API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}"

    response = requests.get(url)
    data = response.json()
    print(data)
    if response.status_code == 200:
        weather_data = data.get("current_weather", {})
        return {
            "temperature": weather_data.get("temperature", 20),  # Default 20°C
            "precipitation": weather_data.get("precipitation", 0),  # Default 0mm
            "windspeed": weather_data.get("windspeed", 5)  # Default 5 m/s
        }
    else:
        print(f"❌ ERROR: Failed to fetch weather data (Status Code {response.status_code})")
        return {"temperature": 20, "precipitation": 0, "windspeed": 5}  # Default values

print(fetch_weather_data())
