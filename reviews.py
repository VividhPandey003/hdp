import requests
import json
import os

# SerpAPI Configuration
SERP_API_KEY = os.getenv("SERP_API_KEY")
HOTEL_NAME = "The Den Bengaluru"
LOCATION = "ITPL Main Rd, KIADB Export Promotion Industrial Area, Whitefield, Bengaluru, Karnataka 560066"

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Step 1: Fetch Reviews from SerpAPI
def fetch_hotel_reviews(hotel_name, location):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps_reviews",
        "data_id": "0x3bae11ef82478417:0xb16280be4e67f5ff",
        "api_key": SERP_API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        reviews = response.json().get("reviews", [])
        return [review["snippet"] for review in reviews if "snippet" in review]
    else:
        print("Error fetching reviews:", response.text)
        return []

# Step 2: Process Reviews with Groq API
def analyze_painpoints(reviews):
    prompt = f"""
    Analyze the following hotel reviews and extract key insights.

    - Identify pain points and categorize them as High, Medium, or Low severity.
    - If no pain points are found, highlight positive aspects guests loved.

    Reviews: {json.dumps(reviews, indent=2)}

    Output should be a JSON array with:
    - painpoint (or positive_aspect): A brief description of the issue or praise.
    - severity (if applicable): High, Medium, or Low.

    Example:
    [
        {{"painpoint": "Poor cleanliness", "severity": "High"}},
        {{"painpoint": "Slow check-in process", "severity": "Medium"}},
        {{"positive_aspect": "Friendly staff and excellent service"}}
    ]
    """


    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "llama3-70b-8192", "messages": [{"role":"user","content":prompt}], "response_format":{"type":"json_object"}}

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "[]")
    else:
        print("Error processing with Groq:", response.text)
        return "[]"

# Execute the pipeline
if __name__ == "__main__":
    reviews = fetch_hotel_reviews(HOTEL_NAME, LOCATION)
    if reviews:
        painpoints_json = analyze_painpoints(reviews)
        print(reviews)
        print("Extracted Pain Points:", painpoints_json)
    else:
        print("No reviews found.")
