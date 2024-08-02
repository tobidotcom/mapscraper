# Contents of openai_api.py
import requests
import pandas as pd

def evaluate_businesses(csv_file_path, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Check if the dataframe is empty
    if df.empty:
        return "No data available for evaluation."

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
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for HTTP error responses
        result = response.json()

        # Debug: print the response content
        print("OpenAI API response:", result)

        if result.get("choices"):
            evaluation = result["choices"][0]["message"]["content"]
            return evaluation
        
        return "Evaluation could not be performed."
    
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return f"Request error: {e}"
    except Exception as e:
        # Handle any other exceptions
        return f"An unexpected error occurred: {e}"
