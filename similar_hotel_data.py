import requests
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
SERPAPI_KEY = os.getenv("SERP_API_KEY")

def get_dynamic_price_range(current_price):
    """
    Determines min and max price using a percentage-based approach.
    """

    min_price = max(14000, (current_price - 2000))  
    max_price = max((current_price+5000),25000)

    return min_price, max_price

def get_similar_hotel_prices(city, check_in_date, check_out_date, current_price, currency="INR", radius=10):
    """
    Fetches hotel prices from Google Hotels using SerpAPI within a dynamically determined price range.
    """
    # ✅ Determine min/max price range
    min_price, max_price = get_dynamic_price_range(current_price)

    # ✅ SerpAPI Endpoint
    url = "https://serpapi.com/search"

    # ✅ Request Parameters
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
        "sort_by": "3",          # Sort by lowest price
        "radius": radius,        
        "api_key": SERPAPI_KEY
    }

    # ✅ API Request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        # ✅ Extract hotel data from `properties`
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
