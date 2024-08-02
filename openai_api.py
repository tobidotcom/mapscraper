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

def evaluate_businesses(description, address, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "You are an expert in B2B lead generation and niche analysis, focusing on specific business services for distinct industries."},
        {"role": "user", "content": f"Based on the business description and address provided, list the top 10 specific B2B niches that combine particular business services with specific industries, which can be found on Google My Business. For example, 'SEO Services for Landscapers' or 'PPC Advertising for Fitness Centers.' The list should be comma-separated and contain only the niche names, with no additional text.\n\nBusiness Description: {description}\nAddress: {address}"}
    ]
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 150
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("choices"):
        niches = result["choices"][0]["message"]["content"].strip()
        niche_list = [niche.strip() for niche in niches.split(',')]
        return niche_list
    else:
        return []

        return niche_list
    else:
        return []
