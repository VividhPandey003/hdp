import requests

def fetch_weather_data(latitude="41.85003", longitude="-87.65005", date="2025-03-10", hour=12):
    """Fetch temperature, precipitation, and wind speed at a specific hour on a given date."""
    
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&start_date={date}&end_date={date}"
        f"&hourly=temperature_2m,precipitation,windspeed_10m"
        f"&timezone=auto"
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)  # Debugging

        hourly_data = data.get("hourly", {})

        # Extracting temperature, precipitation, and windspeed at the requested hour
        temperatures = hourly_data.get("temperature_2m", [])
        precipitation = hourly_data.get("precipitation", [])
        windspeed = hourly_data.get("windspeed_10m", [])

        if len(temperatures) > hour:
            return {
                "temperature": temperatures[hour],  # Temperature at requested hour
                "precipitation": precipitation[hour],
                "windspeed": windspeed[hour]
            }
        else:
            print("❌ ERROR: Data not available for requested hour")
            return {"temperature": 20, "precipitation": 0, "windspeed": 5}  # Default values
    else:
        print(f"❌ ERROR: Failed to fetch weather data (Status Code {response.status_code})")
        return {"temperature": 20, "precipitation": 0, "windspeed": 5}  # Default values

# Example usage: Get weather at 12:00 PM on March 10, 2025
print(fetch_weather_data())
