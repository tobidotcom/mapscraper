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
    response = requests.post(url, headers=headers, json=data)
    
    try:
        response.raise_for_status()
        postal_codes_str = response.json()["choices"][0]["message"]["content"]
        
        # Validate the response to ensure it's a list of postal codes
        postal_codes = [code.strip() for code in postal_codes_str.split(",") if code.strip().isdigit()]
        
        if not postal_codes:
            raise ValueError("No valid postal codes found in the response.")
        
        return postal_codes
    except Exception as e:
        logging.error(f"Error fetching postal codes: {e}")
        return []

# Test function to see output
if __name__ == "__main__":
    test_city = "New York"
    test_api_key = "YOUR_OPENAI_API_KEY"
    print(get_postal_codes(test_city, test_api_key))
