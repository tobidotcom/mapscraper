import openai
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

def evaluate_businesses(file_path, openai_api_key):
    openai.api_key = openai_api_key
    
    # Load the data from CSV
    df = pd.read_csv(file_path)
    businesses = df.to_dict(orient='records')
    
    # Create a prompt for OpenAI
    prompt = "Evaluate the following businesses and rank them based on their potential to benefit from GoHighLevel services. Consider factors like star rating, number of reviews, and overall reviews text.\n\n"
    for business in businesses:
        prompt += f"Business Name: {business['name']}\n"
        prompt += f"Address: {business['address']}\n"
        prompt += f"Rating: {business['rating']}\n"
        prompt += f"Number of Reviews: {business['reviews_count']}\n"
        prompt += f"Reviews: {business['reviews_text']}\n\n"
    
    prompt += "Rank these businesses from the best to worst based on the potential to work with GoHighLevel.\n\n"

    # Send the prompt to OpenAI
    response = openai.Completion.create(
        model="text-davinci-003",  # Use the latest or appropriate model
        prompt=prompt,
        max_tokens=1500,
        temperature=0.5
    )

    return response.choices[0].text.strip()

