import requests

def fetch_weather_data(date, latitude="12.97194", longitude="77.59369",  hour=12):
    """Fetch temperature, precipitation, and wind speed at a specific hour on a given date."""
    
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,precipitation,windspeed_10m"
        f"&timezone=Asia/Kolkata"  # Explicit timezone
        f"&forecast_days=1"  # Only fetch data for the given date
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        hourly_data = data.get("hourly", {})

        # Extract timestamps and values
        timestamps = hourly_data.get("time", [])
        temperatures = hourly_data.get("temperature_2m", [])
        precipitation = hourly_data.get("precipitation", [])
        windspeed = hourly_data.get("windspeed_10m", [])

        # Find the index that matches the requested hour
        for i, timestamp in enumerate(timestamps):
            if timestamp.endswith(f"T{hour:02d}:00"):
                return {
                    "temperature": temperatures[i],
                    "precipitation": precipitation[i],
                    "windspeed": windspeed[i]
                }
        
        print("❌ ERROR: No data found for the requested hour.")
        return {"temperature": 20, "precipitation": 0, "windspeed": 5}  # Default values
    else:
        print(f"❌ ERROR: Failed to fetch weather data (Status Code {response.status_code})")
        return {"temperature": 20, "precipitation": 0, "windspeed": 5}  # Default values

