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

def evaluate_businesses(description, website_content, city, openai_api_key=None):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "You are a business consultant and lead generation expert."},
        {"role": "user", "content": f"Brainstorm all possible business niches relevant to the following information and provide a list of the top 10 niches suitable for Google My Business, in a comma-separated list format. Do only respond with the list, nothing else.\n\nDescription: {description}\nWebsite Content: {website_content}\nCity: {city}"}
    ]
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 500
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    niches = []
    if result.get("choices"):
        niches = result["choices"][0]["message"]["content"]
        niches = niches.strip().split(',')
        niches = [niche.strip() for niche in niches]
    
    return niches[:10]  # Return only the top 10 niches
