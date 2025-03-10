from dotenv import load_dotenv
load_dotenv()
import json
import os
import requests
from events import get_events
from weather_api import fetch_weather_data
from historical_data import get_historical_data
from news import get_news

GROQ_API_KEY =  os.getenv("GROQ_API_KEY")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def groq_api(prompt):
    """
    Sends the structured prompt to Groq's API and returns the response.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are an AI that predicts hotel room prices based on historical data, weather, and events."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "response_format":{"type":"json_object"}
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])  # Parsing JSON response from Groq
    else:
        return {
            "predicted_price": None,
            "reason": f"Error: {response.status_code}, {response.text}"
        }

def create_prompt(booking_date, events_data, weather_data, historical_data, news_data):
    """
    Formats the input data into a structured prompt to send to Groq API.
    """
    month = booking_date.split('-')[1]  # Extract month as a string (MM format)
    months_map = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    month_name = months_map.get(month, "Unknown")

    # Convert weather data into a readable JSON format
    weather_info = json.dumps(weather_data, indent=2)

    prompt = f"""
    You are an AI that predicts hotel room prices based on historical pricing trends, weather conditions, and major events.

    **Booking Details:**
    - Booking Date: {booking_date}
    - Month: {month_name}

    **Weather Information:**  - {weather_info}

    **Major Events Nearby:** - {events_data}

    **News - ** - {news_data}

    **Historical Monthly Prices:**
    {json.dumps(historical_data["historical_prices"], indent=2)}

    Based on this data, predict the room price for the given booking date.

    ### **Expected Output in the below JSON Format:**
    - `"predicted_price"`: The estimated price based on demand factors.
    - `"reason"`: A short explanation for the prediction in maximum 250 characters with only necessary information.
    """

    return prompt

def predict_room_price(booking_date):
    """
    Fetches all required data and predicts the room price by sending a structured prompt to Groq API.
    """
    # Collect data from various sources
    events_data = get_events(booking_date)
    news_data = get_news(booking_date)
    weather_data = fetch_weather_data()
    historical_data = get_historical_data()

    # Generate the prompt
    prompt = create_prompt(booking_date, events_data, weather_data, historical_data, news_data)
    print("\n\n",prompt,"\n\n")
    # Send prompt to Groq API
    prediction = groq_api(prompt)

    # Format the response
    response = {
        "current_price": historical_data["historical_prices"][int(booking_date.split('-')[1])-1],
        "predicted_price": prediction.get("predicted_price"),
        "reason": prediction.get("reason")
    }

    return json.dumps(response, indent=4)

# Example usage
booking_date = "2025-03-10"  # Format YYYY-MM-DD
print(predict_room_price(booking_date))
