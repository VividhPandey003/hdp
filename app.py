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

# ✅ Dynamic Ancillary Pricing Strategy (LLM decides usage)
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
            {"role": "system", "content": "You are an AI hotel pricing strategist. Given historical trends, competitor pricing, weather, and demand, propose the best price while ensuring competitiveness and profitability."},
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

    # ✅ Get historical price
    month_index = int(booking_date.split('-')[1]) - 1
    current_price = historical_data[room_type][month_index]

    # ✅ Validate room type
    if room_type not in historical_data:
        return json.dumps({"error": f"Invalid room type '{room_type}'."}, indent=4)

    # ✅ Fetch competitor pricing
    competitors = get_similar_hotel_prices(city, booking_date, booking_date, current_price)

    # ✅ Compute average, min, and max competitor price
    competitor_prices = [
        int(hotel["price_per_night"].replace("₹", "").replace(",", "")) 
        for hotel in competitors 
        if hotel["price_per_night"] not in ["N/A", None]
    ]
    
    competitor_avg_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0
    competitor_min_price = min(competitor_prices) if competitor_prices else 0
    competitor_max_price = max(competitor_prices) if competitor_prices else 0


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

    **Ancillaries (Optional Value-Adds, To Be Used ONLY If Needed for Competitiveness):**
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
    1. **Set an optimal room price based on real-time demand, competitor pricing, historical trends, and external factors like events and weather conditions.**
    2. **Ensure the price falls within the range of competitor pricing.**
    3. **If the predicted price is above the competitor average, cap it at that level and DO NOT include ancillaries.**
    4. **If the predicted price is below the competitor average, round it up to the competitor average price and add suitable ancillaries.**
    5. **If the predicted price is between the competitor average and the highest competitor price, keep it as is without adding ancillaries.**
    6. **If the predicted price is lower than the lowest competitor, adjust it to just below the lowest competitor price and add high-value ancillaries.**
    7. **Provide a detailed explanation (description) for the hotel owner explaining why this price is justified.**
    8. **Explicitly outline the logic (math breakdown) for arriving at the final price.**
    9. **Output must follow this exact JSON structure:**
    
    ```json
    {{
        "booking_date": "{booking_date}",
        "room_type": "{room_type}",
        "current_price": {current_price},
        "optimized_price": "integer",
        "avgOfSimilarHotelsPricing": {competitor_avg_price},
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

    # ✅ Format response
    response = {
        "booking_date": booking_date,
        "room_type": room_type,
        "current_price": current_price,
        "optimized_price": pricing_decision.get("optimized_price"),
        "avgOfSimilarHotelsPricing": competitor_avg_price,
        "selected_ancillaries": pricing_decision.get("selected_ancillaries", []),
        "short_description": pricing_decision.get("short_description"),
        "description": pricing_decision.get("description"),
        "logic": pricing_decision.get("logic")
    }

    print("✅ Pricing Decision Received!")
    return json.dumps(response, indent=4)
