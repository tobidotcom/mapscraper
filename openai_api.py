import requests
import logging

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
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()
        logging.debug(f"API Response: {response_json}")
        postal_codes_str = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        postal_codes = [code.strip() for code in postal_codes_str.split(",") if code.strip().isdigit()]
        if not postal_codes:
            raise ValueError("No valid postal codes found in the response.")
        return postal_codes
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return []
    except ValueError as e:
        logging.error(f"Value error: {e}")
        return []
    except Exception as e:
        logging.error(f"Error fetching postal codes: {e}")
        return []
