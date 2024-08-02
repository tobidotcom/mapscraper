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

def evaluate_businesses(description, website_content, address, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "You are an expert in B2B lead generation and niche analysis."},
        {"role": "user", "content": f"Based on the business description, website content, and the address provided, suggest the top 10 B2B niches that would be ideal for finding leads on Google My Business. The niches should be common B2B sectors where businesses are listed on Google My Business.\n\nBusiness Description: {description}\nWebsite Content: {website_content}\nAddress: {address}"}
    ]
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 1000
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("choices"):
        niches = result["choices"][0]["message"]["content"].strip()
        # Assuming niches are provided as a comma-separated list
        niche_list = [niche.strip() for niche in niches.split(',')]
        return niche_list
    else:
        return []

