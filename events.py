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

def get_events(date):
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that provides structured data on major events in Bangalore affecting hotel pricing. Your response must strictly follow the provided JSON schema."
            },
            {
                "role": "user",
                "content": "List major upcoming events in Bangalore that could impact hotel pricing on {date}. Format your response as a JSON object with the following structure:\n\n"
                          "{\n"
                          "  \"events\": [\n"
                          "    {\n"
                          "      \"eventName\": \"string\",\n"
                          "      \"eventCapacityLevel\": \"High | Medium | Low\",\n"
                          "      \"startDate\": \"YYYY-MM-DD\",\n"
                          "      \"endDate\": \"YYYY-MM-DD\",\n"
                          "      \"reason\": \"string\"\n"
                          "    }\n"
                          "  ]\n"
                          "}\n\n"
                          "Ensure that all required fields are included and that eventCapacityLevel is categorized as 'High', 'Medium', or 'Low'.\nOnly give valid json. Do not include ```json in response or any other text"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "name": "fetch_Bangalore_events",
                    "description": "Retrieve major upcoming events in or near Bangalore that could impact hotel pricing.",
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
                                        "startDate": {"type": "string", "format": "date"},
                                        "endDate": {"type": "string", "format": "date"},
                                        "reason": {"type": "string"}
                                    },
                                    "required": ["eventName", "eventCapacityLevel", "startDate", "endDate", "reason"]
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

