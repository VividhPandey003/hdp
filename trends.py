import requests
import os
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
SERPAPI_KEY = os.getenv("SERP_API_KEY")

def get_hotel_demand_trends():
    """
    Fetches Google Trends data to analyze peak hotel demand periods in Bangalore.
    """

    # Define SerpAPI Endpoint
    url = "https://serpapi.com/search"

    # Google Trends Query Parameters
    params = {
        "engine": "google_trends",
        "q": "Bangalore hotels, best time to visit Bangalore, Bangalore travel trends",
        "geo": "IN",
        "hl": "en",
        "date": "today 12-m",  # Past 12 months
        "data_type": "TIMESERIES",  # Interest over time
        "api_key": SERPAPI_KEY
    }

    # API Request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "interest_over_time" in data:
            trends = data["interest_over_time"]
            print("\n🔹 **Bangalore Hotel Demand Trends Over the Past Year:**")
            for entry in trends:
                print(f"📅 {entry['date']}: Interest Level = {entry['value']}")

            return trends
        else:
            print("❌ No valid trend data found.")
            return None
    else:
        print(f"❌ Error fetching trends: {response.text}")
        return None


# Run the function
if __name__ == "__main__":
    get_hotel_demand_trends()
