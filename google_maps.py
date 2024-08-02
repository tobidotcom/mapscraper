import requests
import time

def get_place_details(place_id, api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,rating,user_ratings_total,reviews",
        "key": api_key
    }
    response = requests.get(url, params=params)
    details_data = response.json()
    
    if details_data.get("result"):
        phone = details

