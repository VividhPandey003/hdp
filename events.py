from dotenv import load_dotenv
load_dotenv()
import requests
import os

API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_events(date, hotel_location="Whitefield, Bangalore"):
    """
    Fetches major upcoming events near the hotel location that could impact hotel pricing.
    The response includes event details, expected attendance, event location, and its impact on hotel pricing.
    """

    prompt_content = f"""
    You are an AI assistant that provides structured data on major events in {hotel_location} affecting hotel pricing.
    
    Your response **must strictly follow the provided JSON schema**.

    **Task:**  
    List major upcoming events near {hotel_location} that could impact hotel pricing on {date}.  

    **Considerations:**  
    - Only include events with **large attendance (above 1000 attendees)** or those that could significantly impact hotel demand.  
    - Provide the **expected attendee count** for each event.  
    - Specify the **event location (venue & city)**.  
    - Analyze whether the event **actually affects hotel demand** in {hotel_location}.  
      - If yes, explain why (e.g., high demand, close to hotel, multi-day event).  
      - If no, provide a reason (e.g., niche audience, far from hotel).  

    **JSON Response Structure:**  
    ```json
    {{
      "events": [
        {{
          "eventName": "string",
          "eventCapacityLevel": "High | Medium | Low",
          "expectedAttendees": "integer",
          "eventLocation": {{
            "venue": "string",
            "city": "string"
          }},
          "startDate": "YYYY-MM-DD",
          "endDate": "YYYY-MM-DD",
          "affectsHotel": "Yes | No",
          "reason": "string"
        }}
      ]
    }}
    ```
    
    **Rules for the Response:**  
    - `eventCapacityLevel`:  
      - "High" → **More than 10,000 attendees**  
      - "Medium" → **Between 2,000 - 10,000 attendees**  
      - "Low" → **Between 1,000 - 2,000 attendees**  
    - `affectsHotel`:  
      - "Yes" → If high demand is expected in {hotel_location}  
      - "No" → If the event is far away or has a niche audience  
    - Ensure that all fields are provided in valid JSON format. **No extra text or markdown.**
    """

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are an AI assistant that provides structured data on major events affecting hotel pricing."},
            {"role": "user", "content": prompt_content}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "name": "fetch_Bangalore_events",
                    "description": "Retrieve major upcoming events that could impact hotel pricing.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "events": {
                                "type": "array",
                                "description": "A list of major events that may affect hotel pricing.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "eventName": {"type": "string"},
                                        "eventCapacityLevel": {"type": "string", "enum": ["High", "Medium", "Low"]},
                                        "expectedAttendees": {"type": "integer"},
                                        "eventLocation": {
                                            "type": "object",
                                            "properties": {
                                                "venue": {"type": "string"},
                                                "city": {"type": "string"}
                                            },
                                            "required": ["venue", "city"]
                                        },
                                        "startDate": {"type": "string", "format": "date"},
                                        "endDate": {"type": "string", "format": "date"},
                                        "affectsHotel": {"type": "string", "enum": ["Yes", "No"]},
                                        "reason": {"type": "string"}
                                    },
                                    "required": ["eventName", "eventCapacityLevel", "expectedAttendees", "eventLocation", "startDate", "endDate", "affectsHotel", "reason"]
                                }
                            }
                        },
                        "required": ["events"]
                    }
                }
            }
        }
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"
