from dotenv import load_dotenv
load_dotenv()
import json
import os
import requests
from events import get_events
from weather_api import fetch_weather_data
from historical_data import get_historical_data
from news import get_news
from similar_hotel_data import get_similar_hotel_prices

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ✅ Dynamic Ancillary Pricing Strategy
ANCILLARIES = {
    "breakfast": 500,
    "airport_transfer": 1000,
    "spa_access": 1200,
    "gym_access": 300
}

def groq_api(prompt):
    """ Sends structured prompt to Groq's API and returns the response. """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are an AI pricing strategist that determines optimal hotel pricing. Given historical trends, competitor pricing, weather, and demand, propose the best price while ensuring competitiveness and profitability."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])  # Parsing JSON response from Groq
    else:
        return {
            "optimized_price": None,
            "reason": f"Error: {response.status_code}, {response.text}"
        }

def predict_room_price(booking_date, room_type, city="Bangalore"):
    """
    Fetches all required data, provides everything to LLM, and lets it decide the best pricing strategy.
    """
    print(f"\n🚀 Predicting price for {room_type} on {booking_date} in {city}")

    # ✅ Fetch data from various sources
    events_data = get_events(booking_date)
    news_data = get_news(booking_date)
    weather_data = fetch_weather_data(booking_date)
    historical_data = get_historical_data()

    # ✅ Validate room type
    if room_type not in historical_data:
        return json.dumps({"error": f"Invalid room type '{room_type}'."}, indent=4)

    # ✅ Fetch competitor pricing
    competitors = get_similar_hotel_prices(city, booking_date, booking_date)

    # ✅ Compute average, min, and max competitor price
    competitor_prices = [
        int(hotel["price_per_night"].replace("₹", "").replace(",", "")) 
        for hotel in competitors 
        if hotel["price_per_night"] not in ["N/A", None]
    ]
    
    competitor_avg_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0
    competitor_min_price = min(competitor_prices) if competitor_prices else 0
    competitor_max_price = max(competitor_prices) if competitor_prices else 0

    # ✅ Get historical price
    month_index = int(booking_date.split('-')[1]) - 1
    current_price = historical_data[room_type][month_index]

    # ✅ Construct prompt for LLM
    prompt = f"""
    Based on the following details, determine an **optimized room price** for the given date.

    **Booking Details:**
    - **Date:** {booking_date}
    - **City:** {city}
    - **Room Type:** {room_type}

    **Pricing Data:**
    - **Historical Average Price (Same Month):** {current_price} INR
    - **Competitor Average Price:** {competitor_avg_price} INR
    - **Lowest Competitor Price:** {competitor_min_price} INR
    - **Highest Competitor Price:** {competitor_max_price} INR

    **Ancillaries (Optional Value-Adds, Add Only If Below Competitor Avg):**
    ```json
    {json.dumps(ANCILLARIES, indent=2)}
    ```

    **Additional Factors:**
    - **Weather Forecast:**  
    ```json
    {json.dumps(weather_data, indent=2)}
    ```
    - **Nearby Events Affecting Demand:**  
    ```json
    {json.dumps(events_data, indent=2)}
    ```
    - **Recent News Impacting Travel:**  
    ```json
    {json.dumps(news_data, indent=2)}
    ```

    ### **Instructions for Price Prediction**
    1. **Determine an optimized room price based on demand trends, competitor pricing, historical data, and external factors.**
    2. **Ensure the optimized price falls within the range of competitor pricing.**
    3. **If the model suggests a price above the competitor average, cap it at that level and do NOT include ancillaries.**
    4. **If the model suggests a price below the competitor average, offer additional ancillaries (free breakfast, spa access, etc.) to increase value.**
    5. **Explicitly outline the logic (math breakdown) for arriving at the final price.**
    6. **Output must follow this exact JSON structure:**
    
    ```json
    {{
        "optimized_price": "integer",
        "selected_ancillaries": ["string"],
        "short_description": "string",
        "description": "string",
        "logic": "string"
    }}
    ```
    """

    print("\n🔹 Sending prompt to Groq API...\n")

    # ✅ Send prompt to Groq API
    pricing_decision = groq_api(prompt)

    # ✅ Validate and adjust pricing based on rules
    final_price = pricing_decision.get("optimized_price", competitor_avg_price)

    if final_price > competitor_avg_price:
        final_price = competitor_avg_price
        selected_ancillaries = []
    elif final_price < competitor_min_price:
        selected_ancillaries = list(ANCILLARIES.keys())  # Add all ancillaries
    else:
        selected_ancillaries = pricing_decision.get("selected_ancillaries", [])

    # ✅ Format response
    response = {
        "room_type": room_type,
        "current_price": current_price,
        "optimized_price": final_price,
        "avgOfSimilarHotelsPricing": competitor_avg_price,
        "selected_ancillaries": selected_ancillaries,
        "short_description": pricing_decision.get("short_description"),
        "description": pricing_decision.get("description"),
        "logic": pricing_decision.get("logic")
    }

    print("✅ Pricing Decision Received!")
    return json.dumps(response, indent=4)

