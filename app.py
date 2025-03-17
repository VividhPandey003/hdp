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

# ✅ Ancillary Pricing Strategy
ANCILLARIES = {
    "gym_access": 100,
    "breakfast": 500,
    "airport_transfer": 1000,
    "spa_access": 1200,
    "late_checkout": 700,
    "early_checkin": 800,
    "city_tour": 1500,
    "laundry_service": 600,
    "private_dining": 2000,
    "wifi_premium": 400,
    "business_center_access": 900,
    "valet_parking": 500,
    "mini_bar_credit": 700,
    "room_upgrades": 2500,
    "personal_concierge_service": 1800,
    "pet_friendly_services": 1000,
    "romantic_package": 2200,
    "babysitting_service": 1500,
    "kids_play_area_access": 600,
    "bike_rental": 750,
    "shuttle_service": 900,
    "poolside_cabana": 1300,
    "live_entertainment": 1200,
    "beach_club_access": 1600,
    "cooking_classes": 1400,
    "wine_tasting_experience": 1700,
    "yoga_session": 800,
    "private_fitness_training": 1100,
    "car_rental_discount": 2500,
    "personal_shopper_service": 2000,
    "premium_lounge_access": 1800
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

    # ✅ Validate room type
    if room_type not in historical_data:
        return json.dumps({"error": f"Invalid room type '{room_type}'."}, indent=4)

    # ✅ Get historical price
    month_index = int(booking_date.split('-')[1]) - 1
    current_price = historical_data[room_type][month_index]

    # ✅ Fetch competitor pricing
    competitors = get_similar_hotel_prices(city, booking_date, booking_date, current_price)
    print("🔴 COMPETITORS =", competitors)  # Debugging step

    competitor_prices = [
        int(hotel["price_per_night"].replace("₹", "").replace(",", "")) 
        for hotel in competitors 
        if hotel["price_per_night"] not in ["N/A", None]
    ]

    if not competitor_prices:
        return json.dumps({"error": "No valid competitor prices found."}, indent=4)

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
    1. **Set an optimal room price** based on real-time demand, competitor pricing, historical trends, and external factors like events, weather conditions, and news.
    2. **Ensure the price falls within the competitor pricing range** to maintain competitiveness while maximizing revenue.
    3. **If the predicted price is above the competitor average**, cap it at that level and **DO NOT include ancillaries** to avoid overpricing.
    4. **If the predicted price is below the competitor average**, round it up to the competitor average price and **ADD suitable ancillaries** to enhance value.
    5. **If the predicted price is between the competitor average and the highest competitor price**, keep it as is **without adding ancillaries** to maintain competitiveness.
    6. **If the predicted price is lower than the lowest competitor**, adjust it to just below the **average** competitor price and **add high-value ancillaries** to attract more bookings.
    7. **Provide a structured `description` in bullet points**, ranking the factors influencing the final price in order of importance, but **without headings**:
    - Mention any major events affecting demand with expected attendance and impact.
    - Summarize the competitor pricing trend and where the optimized price is set.
    - Briefly note weather conditions if they have any impact on travel plans.
    - Include historical booking trends and how the price aligns with past demand.
    - If ancillaries are added, mention them with a short justification.
    - If any news or external factors influence the price, summarize their effect.
    8. **Explicitly outline the `logic` used** for arriving at the final price, ensuring calculations and justifications are clearly explained in maximum 150 tokens.
    9. **Strictly follow the JSON response format below:**
    ```json
    {{
        "booking_date": "{booking_date}",
        "room_type": "{room_type}",
        "current_price": {current_price},
        "optimized_price": "integer",
        "avgOfSimilarHotelsPricing": {competitor_avg_price},
        "selected_ancillaries": ["string"],
        "short_description": "string",
        "description": ["string"], 
        "logic": "string"
    }}
    ```
    """

    print("\n🔹 Sending prompt to Groq API...\n")

    # ✅ Send prompt to Groq API
    pricing_decision = groq_api(prompt)

    print(f"\n\n🔹 LLM Prompt Sent:\n{prompt}")

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
