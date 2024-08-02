import requests

def get_postal_codes(address, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"List all postal codes for the area around {address} in a comma-separated list format. Do only respond with the list, nothing else."}
        ],
        "max_tokens": 500
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    postal_codes = []
    if result.get("choices"):
        postal_codes = result["choices"][0]["message"]["content"]
        postal_codes = postal_codes.strip().split(',')
        postal_codes = [code.strip() for code in postal_codes]
    
    return postal_codes

def evaluate_businesses(description, website=None, openai_api_key=None):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "You are a business consultant and lead generation expert."},
        {"role": "user", "content": f"Based on the description and services of the business, and optionally the website content, find the ideal B2B niche. Provide a customer avatar and suggest the best areas in the United States to find leads for the business. \n\nDescription: {description}\nWebsite: {website if website else 'None'}"}
    ]
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 1000
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("choices"):
        return result["choices"][0]["message"]["content"].strip()
    else:
        return None
