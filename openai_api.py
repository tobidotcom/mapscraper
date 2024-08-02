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
            {"role": "user", "content": f"Please provide a comma-separated list of all postal codes for {city}, including those from the surrounding areas. Ensure that the list is comprehensive and covers a broad range of postal codes."}
        ],
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from OpenAI API: {response.text}")

    result = response.json()

    postal_codes = []
    if result.get("choices"):
        postal_codes = result["choices"][0]["message"]["content"]
        postal_codes = postal_codes.strip().split(',')
        postal_codes = [code.strip() for code in postal_codes]

    # Check if postal_codes is a list of strings
    if not all(isinstance(code, str) for code in postal_codes):
        raise ValueError("Invalid postal codes: postal_codes should be a list of strings")

    return postal_codes
