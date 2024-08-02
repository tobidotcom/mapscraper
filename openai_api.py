# Contents of openai_api.py
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

    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    businesses = df.to_dict(orient="records")
    
    # Create messages for the API request
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Given the following data on businesses, identify the best ones to work with based on their ratings, number of reviews, and other details. Provide a summary of why each selected business is considered the best.\n\nData: {businesses}"}
    ]
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 1500
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("choices"):
        evaluation = result["choices"][0]["message"]["content"]
        return evaluation
    
    return "Evaluation could not be performed."

