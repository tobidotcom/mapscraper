# Contents of gohighlevel.py
import requests

def add_contact_to_gohighlevel(api_key, contact):
    url = "https://rest.gohighlevel.com/v1/contacts/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=contact)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error adding contact to GoHighLevel: {response.status_code} {response.text}")
