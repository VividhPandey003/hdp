import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

# ✅ Load API key from .env file
load_dotenv()
SERPAPI_KEY = os.getenv("SERP_API_KEY")

def filter_relevant_events(events, target_date):
    """
    Filters events to include only those occurring within ±2 days of the target_date.
    """
    target_date = datetime.strptime(target_date, "%Y-%m-%d")
    filtered_events = []

    for event in events:
        start_date_str = event.get("date", {}).get("start_date", "")
        end_date_str = event.get("date", {}).get("end_date", start_date_str)  # Default to same day if missing

        try:
            # ✅ Convert event dates to datetime objects
            start_date = datetime.strptime(start_date_str, "%b %d")
            end_date = datetime.strptime(end_date_str, "%b %d")

            # ✅ Set the year to match the target date (API does not provide year)
            start_date = start_date.replace(year=target_date.year)
            end_date = end_date.replace(year=target_date.year)

            # ✅ Keep events within ±2 days of the target_date
            if (start_date - timedelta(days=2) <= target_date <= end_date + timedelta(days=2)):
                filtered_events.append(event)
        except ValueError:
            continue  # Skip events with invalid date formats

    return filtered_events


def get_events(date, location="Bangalore"):
    """
    Fetches major upcoming events near the specified location using Google Events API (SerpAPI).
    Filters out past events and only keeps relevant events that may affect hotel pricing.
    """

    # ✅ Define API Endpoint
    url = "https://serpapi.com/search"

    # ✅ Request Parameters
    params = {
        "engine": "google_events",
        "q": f"Events in {location}",  # ✅ Use city-level location
        "hl": "en",
        "gl": "in",
        "location": location,  # ✅ Use only city name
        "htichips": "date:week",  # ✅ Fetch events for the whole week
        "api_key": SERPAPI_KEY
    }

    # ✅ API Request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            print(json.dumps(data, indent=2))  # ✅ Debugging: Print full API response

            if "events_results" not in data:
                return {"error": "No events found"}

            # ✅ Extract and filter event details
            event_list = []
            for event in filter_relevant_events(data["events_results"], date):
                event_name = event.get("title", "N/A")
                venue = event.get("venue", {}).get("name", "Unknown Venue")
                city = event.get("venue", {}).get("address", {}).get("city", location)

                event_start_date = event.get("date", {}).get("start_date", "N/A")
                event_end_date = event.get("date", {}).get("end_date", event_start_date)  # Default to same day
                event_link = event.get("link", "N/A")

                # ✅ Fix: Extract ticket information properly
                ticket_info = event.get("ticket_info", [])
                if isinstance(ticket_info, list) and ticket_info:
                    event_attendance = 1000  # Default
                else:
                    event_attendance = 1000  # Assume 1000 if missing

                # ✅ Determine Capacity Level
                if event_attendance > 10000:
                    capacity_level = "High"
                elif 2000 <= event_attendance <= 10000:
                    capacity_level = "Medium"
                else:
                    capacity_level = "Low"

                # ✅ Determine if the event impacts hotel demand
                affects_hotel = "Yes" if "Whitefield" in venue or city.lower() == "bangalore" else "No"
                reason = "Close proximity to Whitefield, expected high demand." if affects_hotel == "Yes" else "Far from Whitefield."

                # ✅ Append to event list
                event_list.append({
                    "eventName": event_name,
                    "eventCapacityLevel": capacity_level,
                    "expectedAttendees": event_attendance,
                    "eventLocation": {
                        "venue": venue,
                        "city": city
                    },
                    "startDate": event_start_date,
                    "endDate": event_end_date,
                    "affectsHotel": affects_hotel,
                    "reason": reason,
                    "eventLink": event_link
                })

            print("\n🔹 Filtered Events List:\n", json.dumps(event_list, indent=2))  # ✅ Print filtered events

            return {"events": event_list}

        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}

    else:
        return {"error": f"API request failed: {response.status_code}, {response.text}"}


# ✅ Example Call
if __name__ == "__main__":
    test_date = "2025-03-21"
    result = get_events(test_date)
    print(json.dumps(result, indent=2))
