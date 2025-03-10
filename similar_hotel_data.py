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
    if current_price <= 20000:
        price_variation = current_price * 0.10  # ±10%
    elif 20000 < current_price <= 50000:
        price_variation = current_price * 0.15  # ±15%
    else:
        price_variation = current_price * 0.20  # ±20%

    min_price = max(1000, int(current_price - price_variation))  # Ensure min price is reasonable
    max_price = int(current_price + price_variation)

    return min_price, max_price

def get_similar_hotel_prices(city, check_in_date, check_out_date, current_price, currency="INR", radius=5):
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

# Example usage
if __name__ == "__main__":
    city = "Bangalore"
    check_in = "2025-06-10"
    check_out = "2025-06-11"
    currency = "INR"
    current_price = 18000  # Example: Assume hotel's base price is 18k INR

    # ✅ Fetch similar hotel prices
    hotels = get_similar_hotel_prices(city, check_in, check_out, current_price, currency)

    # ✅ Print results
    print(f"\n🔹 Searching for hotels in price range: ₹{get_dynamic_price_range(current_price)}")

    if isinstance(hotels, list):
        if hotels:
            print("\nAvailable Hotels:")
            print("=" * 50)
            for hotel in hotels:
                print(f"Name: {hotel['name']}")
                print(f"Price per night: {hotel['price_per_night']} {currency}")
                print(f"Rating: {hotel['rating']}")
                print(f"Reviews: {hotel['reviews']}")
                print(f"Location: {hotel['location']}")
                print(f"Link: {hotel['link']}")
                print("-" * 50)
        else:
            print("No hotels found within the specified criteria.")
    else:
        print(hotels)  # Print error if any
