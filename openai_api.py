import requests
import pandas as pd

def get_postal_codes(city, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"List all postal codes for {city} in a comma-separated list format. Do only respond with the list, nothing else."}
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

def evaluate_businesses(csv_file_path, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    # Read CSV file
    df = pd.read_csv(csv_file_path)
    businesses_data = df.to_dict(orient='records')
    
    # Format data for OpenAI
    businesses_str = "\n\n".join(
        [f"Name: {b['name']}, Address: {b['address']}, Phone: {b['phone']}, Website: {b['website']}, Rating: {b.get('rating', 'N/A')}, Reviews: {b.get('user_ratings_total', 'N/A')}" for b in businesses_data]
    )
    
    messages = [
        {"role": "system", "content": "You are an expert in lead evaluation."},
        {"role": "user", "content": f"Given the following businesses data, please evaluate and rank which businesses are the best to work with based on the provided information.\n\n{businesses_str}"}
    ]
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 1000
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("choices"):
        evaluation = result["choices"][0]["message"]["content"].strip()
        return evaluation
    else:
        return "Evaluation not available."

