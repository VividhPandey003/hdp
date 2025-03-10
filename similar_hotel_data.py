import requests
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
SERPAPI_KEY = os.getenv("SERP_API_KEY")

def get_similar_hotel_prices(city, check_in_date, check_out_date, currency="INR", min_price=16000, max_price=20000, radius=5):
    """
    Fetches hotel prices from Google Hotels using SerpAPI within a given radius.
    """

    # SerpAPI Endpoint
    url = "https://serpapi.com/search"

    # Request Parameters
    params = {
        "engine": "google_hotels",
        "q": f"hotels in {city}",
        "hl": "en",
        "gl": "in",
        "currency": currency,
        "check_in_date": check_in_date,  
        "check_out_date": check_out_date,  
        "min_price": min_price,       
        "max_price": max_price,       
        "sort_by": 8,                 # Sort by lowest price
        "radius": radius,             # 5km radius
        "api_key": SERPAPI_KEY
    }

    # API Request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        # Extract hotel data from `properties`
        hotels = []
        if "properties" in data:
            for hotel in data["properties"]:
                hotel_info = {
                    "name": hotel.get("name", "N/A"),
                    "price_per_night": hotel.get("rate_per_night", {}).get("before_taxes_fees", "N/A"),
                    "rating": hotel.get("overall_rating", "N/A"),
                    "reviews": hotel.get("reviews", "N/A"),
                    "location": hotel.get("description", "N/A"),
                    "link": hotel.get("link", "N/A")
                }
                hotels.append(hotel_info)

        return hotels

    else:
        return {"error": f"Failed to fetch data: {response.status_code}, {response.text}"}

# Example usage
city = "Bangalore"
check_in = "2025-06-10"
check_out = "2025-06-11"

hotels = get_similar_hotel_prices(city, check_in, check_out)
