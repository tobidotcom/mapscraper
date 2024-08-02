import requests
import logging

def add_contact_to_gohighlevel(api_key, contact):
    url = "https://rest.gohighlevel.com/v1/contacts/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json=contact)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error adding contact to GoHighLevel: {e}")
        raise
