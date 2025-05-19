import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ✅ Load SERPAPI key
load_dotenv()
SERPAPI_KEY = os.getenv("SERP_API_KEY")

def filter_relevant_news(news_items, target_date):
    """
    Filters news within ±2 days of the target_date.
    """
    target = datetime.strptime(target_date, "%Y-%m-%d")
    relevant_news = []

    for item in news_items:
        date_str = item.get("date")
        if not date_str:
            continue

        try:
            news_date = datetime.strptime(date_str, "%b %d, %Y")  # e.g., "May 17, 2025"
        except ValueError:
            continue

        if target - timedelta(days=2) <= news_date <= target + timedelta(days=2):
            relevant_news.append(item)

    return relevant_news


def get_news(target_date, location="Bangalore"):
    """
    Uses SerpAPI Google News to fetch news headlines near Bangalore
    and filters only those that might impact hotel pricing.
    """
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_news",
        "q": f"{location} protests OR outbreak OR strike OR flood OR political unrest OR election",
        "location": location,
        "hl": "en",
        "gl": "in",
        "api_key": SERPAPI_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "news_results" not in data:
            return {"error": "No news found"}

        filtered_news = filter_relevant_news(data["news_results"], target_date)

        news_list = []
        for news in filtered_news:
            title = news.get("title", "No Title")
            date_str = news.get("date", "N/A")
            link = news.get("link", "#")
            snippet = news.get("snippet", "")

            # ✅ Basic heuristic for impactLevel
            title_lower = title.lower()
            if any(x in title_lower for x in ["strike", "flood", "outbreak", "unrest", "protest"]):
                impact_level = "High"
            elif "election" in title_lower or "power cut" in title_lower:
                impact_level = "Medium"
            else:
                impact_level = "Low"

            news_list.append({
                "newsTitle": title,
                "impactLevel": impact_level,
                "startDate": date_str,
                "endDate": date_str,  # Assuming 1-day news item
                "reason": snippet,
                "newsLink": link
            })

        return {"news": news_list}
    else:
        return {"error": f"API request failed: {response.status_code}, {response.text}"}


# ✅ Example usage
if __name__ == "__main__":
    test_date = "2025-03-21"
    result = get_news(test_date)
    print(json.dumps(result, indent=2))
