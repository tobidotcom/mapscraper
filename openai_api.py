# Contents of openai_api.py
import requests

def get_postal_codes(city, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant who can generate comprehensive lists."},
            {"role": "user", "content": f"Please provide a comma-separated list of all postal codes for {city}."}
        ],
        "max_tokens": 100
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        postal_codes_str = response.json()["choices"][0]["message"]["content"]
        return [code.strip() for code in postal_codes_str.split(",")]
    else:
        raise Exception(f"Error fetching postal codes: {response.status_code} {response.text}")
