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

def get_news(date):
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that provides structured data on news and developments in Bangalore that could impact hotel pricing, including disease outbreaks, political unrest, protests, elections, economic changes, strikes, or other factors. Your response must strictly follow the provided JSON schema."
            },
            {
                "role": "user",
                "content": "List major ongoing or upcoming news events in Bangalore that could impact hotel pricing on {date}. These may include:\n"
                          "- Disease outbreaks (e.g., COVID-19, dengue, flu epidemic)\n"
                          "- Protests, political unrest, or large-scale strikes\n"
                          "- Elections and political events\n"
                          "- Economic downturns, inflation spikes, or currency fluctuations\n"
                          "- Natural disasters (floods, earthquakes, heavy rainfall warnings)\n\n"
                          "Format your response as a JSON object with the following structure:\n\n"
                          "{\n"
                          "  \"news\": [\n"
                          "    {\n"
                          "      \"newsTitle\": \"string\",\n"
                          "      \"impactLevel\": \"High | Medium | Low\",\n"
                          "      \"startDate\": \"YYYY-MM-DD\",\n"
                          "      \"endDate\": \"YYYY-MM-DD\",\n"
                          "      \"reason\": \"string\"\n"
                          "    }\n"
                          "  ]\n"
                          "}\n\n"
                          "Ensure that all required fields are included and that impactLevel is categorized as 'High', 'Medium', or 'Low'. If an issue is ongoing (e.g., a disease outbreak), set the startDate to when it began and endDate to an estimated resolution date, if known. \nOnly provide valid JSON. Do not include ```json in response or any other text."
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "name": "fetch_Bangalore_news",
                    "description": "Retrieve major news and developments in Bangalore that could influence hotel pricing.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "news": {
                                "type": "array",
                                "description": "A list of major news factors that may affect hotel pricing.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "newsTitle": {"type": "string"},
                                        "impactLevel": {"type": "string", "enum": ["High", "Medium", "Low"]},
                                        "startDate": {"type": "string", "format": "date"},
                                        "endDate": {"type": "string", "format": "date"},
                                        "reason": {"type": "string"}
                                    },
                                    "required": ["newsTitle", "impactLevel", "startDate", "endDate", "reason"]
                                }
                            }
                        },
                        "required": ["news"]
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


